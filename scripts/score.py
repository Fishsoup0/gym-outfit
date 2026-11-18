#!/usr/bin/env python3
"""gym-outfit 打分引擎（只用标准库）。

用法：
  python score.py score --user user.json --outfit outfit.json   # 给一套打分
  python score.py rank  --user user.json --wardrobe w.json [--top 3]   # 从衣柜里搭出前 N 套
  python score.py gap   --user user.json --wardrobe w.json [--top 5]   # 买哪几件提升最大

user.json   {"sex":"m","build":"lean","strengths":["shoulders"],"weaknesses":["legs"],
             "day":"pull","scene":"strength","season":"summer","emphasis":"upper"}
outfit.json / wardrobe.json  物品列表，每件 {"type":"fitted_tee","color":"black", ...}
  可选字段：name, fit, value(0深/1中/2浅), pattern(solid/fine_stripe/small_check/big_logo/graphic),
            fabric(cotton/quick_dry/...), sheer(true/false), id
"""
import argparse
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402


# ---------- 规范化 ----------
def norm_item(raw, idx=0):
    t = raw.get("type")
    if t not in R.TYPES:
        raise ValueError(f"未知类型 type={t!r}，可选：{', '.join(R.TYPES)}")
    slot, cn, default_fit = R.TYPES[t]
    color = raw.get("color", "black")
    if color not in R.COLORS:
        raise ValueError(f"未知颜色 color={color!r}，可选：{', '.join(R.COLORS)}")
    value, sat, color_cn = R.COLORS[color]
    item = dict(raw)
    item.update(
        id=raw.get("id", f"{t}-{color}-{idx}"),
        slot=slot,
        type_cn=cn,
        fit=raw.get("fit", default_fit),
        value=raw.get("value", value),
        sat=raw.get("sat", sat),
        color_cn=color_cn,
        pattern=raw.get("pattern", "solid"),
        fabric=raw.get("fabric", "unknown"),
        sheer=bool(raw.get("sheer", False)),
    )
    item["label"] = raw.get("name") or f"{color_cn}{cn}"
    return item


def norm_user(u):
    u = dict(u)
    u.setdefault("sex", "m")
    u.setdefault("build", "average")
    u.setdefault("strengths", [])
    u.setdefault("weaknesses", [])
    u.setdefault("day", "full")
    u.setdefault("scene", "strength")
    u.setdefault("season", "spring_autumn")
    if "emphasis" not in u:
        up = len(set(u["strengths"]) & R.UPPER_PARTS)
        lo = len(set(u["strengths"]) & R.LOWER_PARTS)
        u["emphasis"] = "lower" if lo > up else "upper" if up else "balanced"
    for k, table in (("build", R.BUILDS), ("day", R.DAYS), ("scene", R.SCENES), ("season", R.SEASONS)):
        if u[k] not in table:
            raise ValueError(f"user.{k}={u[k]!r} 不合法，可选：{', '.join(table)}")
    return u


def legs_state(u):
    s, w = set(u["strengths"]), set(u["weaknesses"])
    if s & R.LOWER_PARTS:
        return 0  # strong
    if w & R.LOWER_PARTS:
        return 1  # weak
    return 2


# ---------- 打分 ----------
def score_outfit(user, items):
    u = norm_user(user)
    items = [i if "slot" in i else norm_item(i, n) for n, i in enumerate(items)]
    by = {}
    for i in items:
        by.setdefault(i["slot"], []).append(i)
    top = (by.get("top") or [None])[0]
    outer = (by.get("outer") or [None])[0]
    bottom = (by.get("bottom") or [None])[0]
    shoes = (by.get("shoes") or [None])[0]
    socks = (by.get("socks") or [None])[0]
    accs = by.get("accessory", [])
    visible_top = outer or top

    rows, vetoes, notes, culprits = [], [], [], {}

    def veto(key, *its):
        vetoes.append(R.VETO_TEXT[key])
        culprits.setdefault(R.VETO_TEXT[key], set()).update(i["label"] for i in its)

    def add(kind, rule, s, reason):
        if s:
            rows.append({"kind": kind, "rule": rule, "score": s, "reason": reason})

    if not top and not outer:
        notes.append("缺上衣")
    if not bottom:
        notes.append("缺下装")
    if not shoes:
        notes.append("未提供鞋，鞋相关规则未计分")

    build_cn = R.BUILDS[u["build"]]
    bi = R.BUILD_ORDER.index(u["build"])

    # 性别
    for i in items:
        if u["sex"] == "m" and i["type"] in R.FEMALE_ONLY:
            add("单维", "性别", -2, f"{i['type_cn']}一般不适合男生")

    # 上衣类型 × 体型
    for i in ([outer] if outer else [top]):
        if i:
            s = R.TOP_BY_BUILD[i["type"]][bi]
            add("单维", "上衣×体型", s, f"{i['type_cn']}{'适合' if s > 0 else '不适合'}{build_cn}")
    if outer and top:  # 练热了会脱外套，里面那件只计减分
        s = R.TOP_BY_BUILD[top["type"]][bi]
        if s < 0:
            add("单维", "内层×体型", s, f"脱掉外套后{top['type_cn']}不适合{build_cn}")
    # 上衣松紧 × 体型
    if visible_top:
        s = R.FIT_BY_BUILD.get(visible_top["fit"], {}).get(u["build"], 0)
        add("单维", "松紧×体型", s, f"{R.FIT_CN[visible_top['fit']]}上衣对{build_cn}{'加分' if s > 0 else '减分'}")
        s = R.TOP_VALUE_BY_BUILD.get(u["build"], {}).get(visible_top["value"], 0)
        add("单维", "明度×体型", s, "浅色、中间色给偏瘦身材加体积" if u["build"] == "slim" else "深色上衣收身形")
        if u["build"] == "high_fat" and visible_top["value"] == 2 and visible_top["fit"] in R.TIGHT:
            add("单维", "明度×体型", -1, "浅色贴身上衣会放大腰腹")

    # 强弱项露出
    s_parts, w_parts = set(u["strengths"]), set(u["weaknesses"])
    if visible_top:
        exposes = visible_top["type"] in R.EXPOSES_ARMS
        if exposes and s_parts & {"shoulders", "arms", "back"}:
            add("单维", "露强项", 1, "露出肩臂这个强项")
        if exposes and w_parts & {"shoulders", "arms"}:
            add("单维", "藏弱项", -1, "肩臂是弱项却露出来了")
        if visible_top["type"] == "fitted_ls" and w_parts & {"arms"}:
            add("单维", "藏弱项", 1, "修身长袖显手臂轮廓又不露细")
        if (w_parts & {"abs"} or u["build"] == "high_fat") and visible_top["type"] == "crop_top":
            add("单维", "藏弱项", -2, "短款上衣露腰腹弱项")

    # 下装 × 腿
    if bottom:
        ls = legs_state(u)
        s = R.BOTTOM_BY_LEGS[bottom["type"]][ls]
        cn = ["腿是强项", "腿是弱项", "腿一般"][ls]
        add("单维", "下装×腿", s, f"{bottom['type_cn']}：{cn}时{'合适' if s > 0 else '不合适'}")
        if u["sex"] == "f" and bottom["type"] in R.FEMALE_BOTTOM_BONUS:
            s, reason = R.FEMALE_BOTTOM_BONUS[bottom["type"]]
            add("单维", "女生下装", s, reason)

    # 训练日
    rule = R.DAY_BONUS.get(u["day"])
    if rule:
        slot, types, s, reason = rule
        target = visible_top if slot == "top" else bottom
        if target and target["type"] in types and not (slot == "top" and outer):
            add("单维", "训练日", s, reason)

    # 季节
    sr = R.SEASON_RULES.get(u["season"])
    if sr:
        for i in items:
            if i["type"] in sr["bad"] and not (u["season"] == "winter" and outer and i["slot"] == "top"):
                add("单维", "季节", -1, f"{R.SEASONS[u['season']]}天穿{i['type_cn']}不合适")
            elif i["type"] in sr["good"]:
                add("单维", "季节", 1, f"{R.SEASONS[u['season']]}天穿{i['type_cn']}合适")

    # 场景
    for i in items:
        if i["slot"] in ("top", "outer") and i["color"] == "grey_light" and \
                i["fabric"] in ("cotton", "unknown"):
            heavy = u["scene"] in ("video", "cardio")
            add("单维", "场景", -2 if heavy else -1,
                "浅灰棉上衣出汗显渍" + ("，拍视频和有氧更明显" if heavy else ""))
        if u["scene"] == "video" and i["pattern"] in ("fine_stripe", "small_check"):
            veto("pattern_video", i)
    if shoes:
        s = R.SHOES_BY_SCENE[u["scene"]].get(shoes["type"], 0)
        add("单维", "鞋×场景", s, f"{R.SCENES[u['scene']]}穿{shoes['type_cn']}{'合适' if s > 0 else '不合适'}")

    # ---- 交叉 ----
    if visible_top and bottom:
        key = (R.fit_class(visible_top["fit"]), R.fit_class(bottom["fit"]))
        if key in R.FIT_CONTRAST:
            s, reason = R.FIT_CONTRAST[key]
            add("交叉", "上松紧×下松紧", s, reason)
        tv, bv = visible_top["value"], bottom["value"]
        if u["emphasis"] == "upper":
            if tv > bv:
                add("交叉", "明度×重点", 2, "上浅下深，视线集中在上身")
            elif tv < bv:
                add("交叉", "明度×重点", -1, "上深下浅，把视线拉到下身，和上身是强项相反")
        elif u["emphasis"] == "lower" and bv >= tv:
            add("交叉", "明度×重点", 1, "下装不比上衣深，视线落在腿上")
        if top and bottom and top["color"] == bottom["color"] and not outer:
            add("交叉", "同色套装", 1, f"上下同为{top['color_cn']}，同色套装")

    families = {i["color"] for i in items}
    s, reason = R.color_count_score(len(families))
    add("交叉", "颜色数", s, reason)
    high = [i for i in items if i["sat"] == "high"]
    if len({i["color"] for i in high}) >= 2:
        add("交叉", "撞色", -2, "两种以上高饱和颜色撞在一起")
    if any(i["color"] == "neon" for i in items) and \
            len([i for i in items if i["sat"] == "high"]) >= 2:
        veto("neon_full", *[i for i in items if i["color"] == "neon"])

    clothes = {i["color"] for i in (top, outer, bottom) if i}
    echo = [i for i in [shoes] + accs if i and i["color"] in clothes]
    if echo:
        add("交叉", "呼应", 1, f"{echo[0]['label']}和衣服颜色呼应")
    if socks and bottom and bottom["type"].startswith("shorts") and \
            socks["color"] in clothes | ({shoes["color"]} if shoes else set()):
        add("交叉", "袜子", 1, f"短裤露出{socks['label']}，和鞋或衣服同色，下半身收得干净")
    if socks and bottom and socks["type"] == "long_socks" and bottom["type"].startswith("shorts"):
        add("交叉", "袜×下装", -1, "短裤配过小腿长袜，比例断开")
    if sum(1 for i in items if i["pattern"] == "big_logo") >= 2:
        add("交叉", "logo", -1, "两件以上大 logo，抢视线")

    if bottom and bottom["sheer"] and u["day"] == "legs":
        veto("sheer_legs", bottom)

    total = sum(r["score"] for r in rows)
    if vetoes:
        verdict = "不合格"
    else:
        verdict = next(v for th, v in R.VERDICT if total >= th)
    return {
        "total": total,
        "verdict": verdict,
        "vetoes": sorted(set(vetoes)),
        "veto_items": {k: sorted(v) for k, v in culprits.items()},
        "items": [i["label"] for i in items],
        "item_ids": [i["id"] for i in items],
        "core_ids": [i["id"] for i in items if i["slot"] in ("top", "outer", "bottom")],
        "breakdown": rows,
        "notes": notes,
        "user": {k: u[k] for k in ("sex", "build", "day", "scene", "season", "emphasis")},
    }


# ---------- 搭配枚举 ----------
def combos(items, season):
    by = {}
    for i in items:
        by.setdefault(i["slot"], []).append(i)
    tops = by.get("top", [])
    bottoms = by.get("bottom", [])
    outers = [None] + by.get("outer", [])
    shoes = by.get("shoes") or [None]  # 有鞋就必须穿鞋
    socks = [None] + by.get("socks", [])
    for t, o, b, sh, so in itertools.product(tops, outers, bottoms, shoes, socks):
        yield [x for x in (t, o, b, sh, so) if x]


def rank(user, wardrobe, top_n=3):
    u = norm_user(user)
    items = [norm_item(r, n) for n, r in enumerate(wardrobe)]
    if u["sex"] == "m":
        items = [i for i in items if i["type"] not in R.FEMALE_ONLY]
    results = [score_outfit(u, c) for c in combos(items, u["season"])]
    results.sort(key=lambda r: (r["verdict"] != "不合格", r["total"]), reverse=True)
    out, seen = [], set()
    for r in results:  # 前 N 套尽量换上衣或下装，避免只差一双袜子
        core = tuple(r["core_ids"])
        if core in seen:
            continue
        seen.add(core)
        out.append(r)
        if len(out) >= top_n:
            break
    return out


def rank_report(user, wardrobe, top_n=3):
    """CLI 用：前 N 套 + 衣柜里会触发否决的单品提醒。"""
    u = norm_user(user)
    items = [norm_item(r, n) for n, r in enumerate(wardrobe)]
    warn = {}
    for c in combos(items, u["season"]):
        r = score_outfit(u, c)
        for v, its in r["veto_items"].items():
            warn.setdefault(v, set()).update(its)
    outfits = rank(user, wardrobe, top_n)
    return {
        "outfits": outfits,
        "veto_warnings": [{"reason": k, "involved_items": sorted(v)} for k, v in warn.items()],
        "too_few": len(outfits) < top_n,
    }


def gap(user, wardrobe, top_n=5):
    u = norm_user(user)
    owned = [norm_item(r, n) for n, r in enumerate(wardrobe)]
    cat = [norm_item(dict(c, id=f"buy:{c['type']}-{c['color']}"), 1000 + n) for n, c in enumerate(R.CATALOG)]
    if u["sex"] == "m":
        cat = [c for c in cat if c["type"] not in R.FEMALE_ONLY]
    owned_keys = {(i["type"], i["color"]) for i in owned}
    cat = [c for c in cat if (c["type"], c["color"]) not in owned_keys]

    def best(items):
        rs = [score_outfit(u, c) for c in combos(items, u["season"])]
        rs = [r for r in rs if r["verdict"] != "不合格"]
        return max(rs, key=lambda r: r["total"]) if rs else None

    base = best(owned)
    base_score = base["total"] if base else None
    gains = []
    for c in cat:
        b = best(owned + [c])
        if not b or c["id"] not in b["item_ids"]:
            continue
        g = b["total"] - (base_score if base_score is not None else 0)
        if base_score is None or g > 0:
            gains.append({"buy": c["label"], "type": c["type"], "color": c["color"],
                          "gain": g, "best_outfit_after": b["items"], "score_after": b["total"]})
    gains.sort(key=lambda x: x["gain"], reverse=True)
    pairs = []
    if not gains or gains[0]["gain"] <= 2:  # 单件救不回来时，算两件一起买
        for a, b in itertools.combinations(cat, 2):
            if a["slot"] == b["slot"]:
                continue
            r = best(owned + [a, b])
            if r and a["id"] in r["item_ids"] and b["id"] in r["item_ids"]:
                g = r["total"] - (base_score if base_score is not None else 0)
                pairs.append({"buy": [a["label"], b["label"]], "gain": g,
                              "best_outfit_after": r["items"], "score_after": r["total"]})
        pairs.sort(key=lambda x: x["gain"], reverse=True)
    dream = best(owned + cat)
    starter = [x for x in (dream["items"] if dream else [])
               if x not in {i["label"] for i in owned}]
    return {
        "current_best": base,
        "single_item_gains": gains[:top_n],
        "pair_gains": pairs[:3],
        "best_possible": dream,
        "buy_for_best_possible": starter,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="gym-outfit 打分引擎")
    p.add_argument("cmd", choices=["score", "rank", "gap"])
    p.add_argument("--user", required=True)
    p.add_argument("--outfit")
    p.add_argument("--wardrobe")
    p.add_argument("--top", type=int)
    a = p.parse_args(argv)
    load = lambda path: json.load(open(path, encoding="utf-8"))  # noqa: E731
    user = load(a.user)
    if a.cmd == "score":
        res = score_outfit(user, load(a.outfit))
    elif a.cmd == "rank":
        res = rank_report(user, load(a.wardrobe), a.top or 3)
    else:
        res = gap(user, load(a.wardrobe), a.top or 5)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
