"""Unit tests for scripts/score.py (rules come from scripts/rules.py).

Inputs are small hand-built wardrobes. Item ids default to f"{type}-{color}-{idx}",
so the type of a result item can be read back from its id.
"""
import os
import sys

import pytest

SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, SCRIPTS)

import rules as R  # noqa: E402
import score as S  # noqa: E402

FEMALE_TYPES = {"sports_bra", "crop_top", "leggings"}
FIT_RULE = "上松紧×下松紧"
VERDICT_VETO = "不合格"


def base_user(**kw):
    u = {"sex": "m", "build": "average", "day": "full",
         "scene": "strength", "season": "spring_autumn"}
    u.update(kw)
    return u


def rows_for(result, rule):
    return [r for r in result["breakdown"] if r["rule"] == rule]


def type_of(item_id):
    return item_id.split("-")[0]


# ---------- 1. norm_item validation ----------
def test_norm_item_rejects_unknown_type():
    with pytest.raises(ValueError, match="未知类型"):
        S.norm_item({"type": "cape", "color": "black"})


def test_norm_item_rejects_unknown_color():
    with pytest.raises(ValueError, match="未知颜色"):
        S.norm_item({"type": "fitted_tee", "color": "mauve"})


# ---------- 2. norm_user defaults and emphasis ----------
def test_norm_user_fills_defaults():
    u = S.norm_user({})
    assert u["sex"] == "m"
    assert u["build"] == "average"
    assert u["day"] == "full"
    assert u["scene"] == "strength"
    assert u["season"] == "spring_autumn"
    assert u["strengths"] == []
    assert u["weaknesses"] == []
    assert u["emphasis"] == "balanced"


def test_emphasis_lower_when_strengths_are_legs_or_glutes():
    assert S.norm_user({"strengths": ["legs"]})["emphasis"] == "lower"
    assert S.norm_user({"strengths": ["glutes"]})["emphasis"] == "lower"


def test_emphasis_upper_when_strength_is_shoulders():
    assert S.norm_user({"strengths": ["shoulders"]})["emphasis"] == "upper"


def test_explicit_emphasis_is_kept():
    assert S.norm_user({"strengths": ["legs"], "emphasis": "upper"})["emphasis"] == "upper"


# ---------- 3. FIT_CONTRAST rows ----------
def test_loose_top_loose_bottom_scores_minus_two():
    res = S.score_outfit(base_user(), [
        {"type": "oversized_tee", "color": "black"},
        {"type": "wide_pants", "color": "black"},
    ])
    rows = rows_for(res, FIT_RULE)
    assert len(rows) == 1
    assert rows[0]["score"] == -2
    assert rows[0]["kind"] == "交叉"


def test_tight_top_loose_bottom_scores_plus_two():
    res = S.score_outfit(base_user(), [
        {"type": "fitted_tee", "color": "black"},
        {"type": "wide_pants", "color": "black"},
    ])
    rows = rows_for(res, FIT_RULE)
    assert len(rows) == 1
    assert rows[0]["score"] == 2


# ---------- 4. vetoes ----------
def test_two_neon_items_veto():
    res = S.score_outfit(base_user(), [
        {"type": "fitted_tee", "color": "neon"},
        {"type": "shorts_5", "color": "neon"},
    ])
    assert R.VETO_TEXT["neon_full"] in res["vetoes"]
    assert res["verdict"] == VERDICT_VETO


def test_one_neon_item_does_not_veto():
    res = S.score_outfit(base_user(), [
        {"type": "fitted_tee", "color": "neon"},
        {"type": "shorts_5", "color": "black"},
    ])
    assert R.VETO_TEXT["neon_full"] not in res["vetoes"]
    assert res["verdict"] != VERDICT_VETO


def test_fine_stripe_vetoes_in_video_scene():
    items = [
        {"type": "fitted_tee", "color": "navy", "pattern": "fine_stripe"},
        {"type": "shorts_5", "color": "black"},
    ]
    res = S.score_outfit(base_user(scene="video"), items)
    assert R.VETO_TEXT["pattern_video"] in res["vetoes"]
    assert res["verdict"] == VERDICT_VETO


def test_fine_stripe_does_not_veto_outside_video():
    items = [
        {"type": "fitted_tee", "color": "navy", "pattern": "fine_stripe"},
        {"type": "shorts_5", "color": "black"},
    ]
    res = S.score_outfit(base_user(scene="strength"), items)
    assert R.VETO_TEXT["pattern_video"] not in res["vetoes"]


def test_sheer_bottom_vetoes_on_legs_day():
    items = [
        {"type": "fitted_tee", "color": "black"},
        {"type": "shorts_5", "color": "black", "sheer": True},
    ]
    res = S.score_outfit(base_user(day="legs"), items)
    assert R.VETO_TEXT["sheer_legs"] in res["vetoes"]
    assert res["verdict"] == VERDICT_VETO


def test_sheer_bottom_ok_on_other_day():
    items = [
        {"type": "fitted_tee", "color": "black"},
        {"type": "shorts_5", "color": "black", "sheer": True},
    ]
    res = S.score_outfit(base_user(day="pull"), items)
    assert R.VETO_TEXT["sheer_legs"] not in res["vetoes"]


# ---------- 5. male users never get female-only types from rank() ----------
WARDROBE_MIXED = [
    {"type": "fitted_tee", "color": "black"},
    {"type": "shorts_5", "color": "black"},
    {"type": "running_shoes", "color": "white"},
    {"type": "sports_bra", "color": "black"},
    {"type": "crop_top", "color": "white"},
    {"type": "leggings", "color": "black"},
]


def test_rank_male_never_returns_female_only_types():
    out = S.rank(base_user(), WARDROBE_MIXED, top_n=10)
    assert out
    for r in out:
        for iid in r["item_ids"]:
            assert type_of(iid) not in FEMALE_TYPES


def test_female_wardrobe_does_yield_female_types():
    # Sanity check: the same wardrobe does produce female-only items for a female user,
    # so the male filter above is not passing vacuously.
    out = S.rank(base_user(sex="f"), WARDROBE_MIXED, top_n=10)
    ids = {type_of(iid) for r in out for iid in r["item_ids"]}
    assert ids & FEMALE_TYPES


# ---------- 6. rank(): size limit, ordering, vetoes ----------
RANK_WARDROBE = [
    {"type": "fitted_tee", "color": "black"},
    {"type": "tank", "color": "white"},
    {"type": "oversized_tee", "color": "olive"},
    {"type": "fitted_tee", "color": "neon"},
    {"type": "shorts_5", "color": "black"},
    {"type": "joggers", "color": "grey_dark"},
    {"type": "shorts_7", "color": "neon"},
    {"type": "flat_shoes", "color": "white"},
]


def test_rank_returns_at_most_top_n():
    assert len(S.rank(base_user(), RANK_WARDROBE, top_n=2)) == 2
    assert len(S.rank(base_user(), RANK_WARDROBE, top_n=3)) == 3


def test_rank_sorted_by_total_desc_among_non_vetoed():
    out = S.rank(base_user(), RANK_WARDROBE, top_n=3)
    assert all(not r["vetoes"] for r in out)
    totals = [r["total"] for r in out]
    assert totals == sorted(totals, reverse=True)


def test_rank_puts_vetoed_outfits_last():
    # 4 tops x 3 bottoms = 12 outfits; only the neon top + neon shorts pair is vetoed.
    out = S.rank(base_user(), RANK_WARDROBE, top_n=50)
    assert len(out) == 12
    assert out[-1]["verdict"] == VERDICT_VETO
    assert all(r["verdict"] != VERDICT_VETO for r in out[:-1])
    totals = [r["total"] for r in out[:-1]]
    assert totals == sorted(totals, reverse=True)


# ---------- 7. gap() with an empty wardrobe ----------
def test_gap_empty_wardrobe_lists_purchases():
    res = S.gap(base_user(), [])
    assert res["current_best"] is None
    assert res["buy_for_best_possible"]
    assert all(isinstance(x, str) and x for x in res["buy_for_best_possible"])


# ---------- 8. color_count_score boundaries ----------
@pytest.mark.parametrize("n, expected", [(2, 2), (3, 1), (4, 0), (5, -2)])
def test_color_count_score_boundaries(n, expected):
    assert R.color_count_score(n)[0] == expected


def test_rank_report_names_only_culprit_item():
    import score as S
    user = {"sex": "m", "build": "v_shape", "day": "push", "scene": "video", "season": "summer"}
    wardrobe = [
        {"type": "fitted_tee", "color": "black", "pattern": "fine_stripe", "name": "条纹短袖"},
        {"type": "fitted_tee", "color": "white"},
        {"type": "shorts_5", "color": "black"},
    ]
    rep = S.rank_report(user, wardrobe, 3)
    assert rep["veto_warnings"] == [{"reason": rep["veto_warnings"][0]["reason"], "involved_items": ["条纹短袖"]}]
    assert rep["outfits"][0]["verdict"] != "不合格"


def test_inner_layer_negative_counts_when_outer_worn():
    import score as S
    user = {"sex": "m", "build": "high_fat", "season": "winter"}
    r = S.score_outfit(user, [{"type": "fitted_tee", "color": "white"},
                              {"type": "hoodie", "color": "black"},
                              {"type": "joggers", "color": "black"}])
    assert any(x["rule"] == "内层×体型" and x["score"] < 0 for x in r["breakdown"])
