#!/usr/bin/env python3
"""跑 evals/cases 下全部用例，检查打分引擎的输出是否符合预期。

python evals/run_evals.py          # 全部
python evals/run_evals.py -v       # 打印每个用例的前几名
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import score as S  # noqa: E402


def types_of(result):
    return [i.split("-")[0] for i in result["item_ids"]]


def check(case):
    exp, fails = case["expect"], []
    if case["mode"] == "rank":
        res = S.rank(case["user"], case["wardrobe"], 3)
        top1 = res[0]
        t = types_of(top1)
        if "top1_include_any" in exp and not set(t) & set(exp["top1_include_any"]):
            fails.append(f"第一名应包含 {exp['top1_include_any']}，实际 {top1['items']}")
        if "top1_exclude" in exp and set(t) & set(exp["top1_exclude"]):
            fails.append(f"第一名不应包含 {exp['top1_exclude']}，实际 {top1['items']}")
        if "top1_exclude_names" in exp and set(top1["items"]) & set(exp["top1_exclude_names"]):
            fails.append(f"第一名不应包含 {exp['top1_exclude_names']}，实际 {top1['items']}")
        if "top1_verdict_in" in exp and top1["verdict"] not in exp["top1_verdict_in"]:
            fails.append(f"第一名评级应为 {exp['top1_verdict_in']}，实际 {top1['verdict']}")
        shown = [(r["total"], r["verdict"], r["items"]) for r in res]
    else:
        res = S.gap(case["user"], case["wardrobe"], 5)
        g = res["single_item_gains"]
        if "gap_top3_include_any" in exp and not {x["type"] for x in g[:3]} & set(exp["gap_top3_include_any"]):
            fails.append(f"购买前三应含 {exp['gap_top3_include_any']}，实际 {[x['buy'] for x in g[:3]]}")
        if "gap_top1_color_in" in exp and (not g or g[0]["color"] not in exp["gap_top1_color_in"]):
            fails.append(f"第一件该买中性色，实际 {g[0]['buy'] if g else None}")
        shown = [(x["gain"], x["buy"]) for x in g[:3]]
    if "veto_outfit" in exp:
        v = S.score_outfit(case["user"], exp["veto_outfit"]["outfit"])
        if not any(exp["veto_outfit"]["veto_contains"] in x for x in v["vetoes"]):
            fails.append(f"应触发否决：{exp['veto_outfit']['veto_contains']}，实际 {v['vetoes']}")
    return fails, shown


def main():
    verbose = "-v" in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, "evals", "cases", "*.json")))
    passed = 0
    for f in files:
        case = json.load(open(f, encoding="utf-8"))
        fails, shown = check(case)
        name = os.path.basename(f)
        print(f"{'PASS' if not fails else 'FAIL'}  {name}  {case['desc']}")
        for x in fails:
            print("      ✗", x)
        if verbose:
            for s in shown:
                print("      ·", s)
        passed += not fails
    print(f"\n{passed}/{len(files)} 通过")
    sys.exit(0 if passed == len(files) else 1)


if __name__ == "__main__":
    main()
