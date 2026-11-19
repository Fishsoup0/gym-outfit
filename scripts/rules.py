"""gym-outfit 规则表。调审美标准只改这个文件，score.py 不用动。

分值约定：单维和交叉规则都在 -2..+2 之间；否决项直接判不合格。
"""

# ---------- 词表 ----------
BUILDS = {"slim": "偏瘦", "lean": "薄肌", "v_shape": "V形", "average": "普通", "high_fat": "体脂偏高"}
BODY_PARTS = {"shoulders": "肩", "back": "背", "arms": "手臂", "chest": "胸",
              "abs": "腹", "legs": "腿", "glutes": "臀"}
UPPER_PARTS = {"shoulders", "back", "arms", "chest", "abs"}
LOWER_PARTS = {"legs", "glutes"}
DAYS = {"push": "推（胸肩）", "pull": "拉（背）", "legs": "腿", "upper": "上肢",
        "arms": "手臂", "full": "全身", "cardio": "有氧"}
SCENES = {"strength": "力量训练", "cardio": "有氧", "video": "拍视频"}
SEASONS = {"summer": "夏", "spring_autumn": "春秋", "winter": "冬"}

TYPES = {
    # 上衣
    "tank": ("top", "宽肩带背心", "fitted"),
    "stringer": ("top", "大挖肩背心", "fitted"),
    "fitted_tee": ("top", "修身短袖", "fitted"),
    "regular_tee": ("top", "常规短袖", "regular"),
    "oversized_tee": ("top", "oversize短袖", "loose"),
    "fitted_ls": ("top", "修身长袖", "fitted"),
    "loose_ls": ("top", "宽松长袖", "loose"),
    "sports_bra": ("top", "运动内衣", "compression"),
    "crop_top": ("top", "短款上衣", "fitted"),
    # 外层
    "hoodie": ("outer", "卫衣", "loose"),
    "zip_jacket": ("outer", "拉链外套", "regular"),
    # 下装
    "shorts_3": ("bottom", "3寸短裤", "regular"),
    "shorts_5": ("bottom", "5寸短裤", "regular"),
    "shorts_7": ("bottom", "7寸短裤", "regular"),
    "shorts_2in1": ("bottom", "二合一短裤", "regular"),
    "joggers": ("bottom", "收脚长裤", "regular"),
    "leggings": ("bottom", "紧身裤", "compression"),
    "wide_pants": ("bottom", "阔腿长裤", "loose"),
    # 鞋袜配件
    "flat_shoes": ("shoes", "平底鞋", None),
    "running_shoes": ("shoes", "跑鞋", None),
    "slides": ("shoes", "拖鞋", None),
    "no_show_socks": ("socks", "隐形袜", None),
    "crew_socks": ("socks", "中筒袜", None),
    "long_socks": ("socks", "过小腿长袜", None),
    "cap": ("accessory", "帽子", None),
    "belt": ("accessory", "腰带", None),
    "watch": ("accessory", "手表", None),
}
FEMALE_ONLY = {"sports_bra", "crop_top", "leggings"}
FIT_CN = {"compression": "压缩", "fitted": "修身", "regular": "常规", "loose": "宽松"}
TIGHT, LOOSE = {"compression", "fitted"}, {"loose"}
EXPOSES_ARMS = {"tank", "stringer", "sports_bra", "crop_top"}
EXPOSES_LEGS = {"shorts_3", "shorts_5"}

# 颜色族：(明度, 饱和度, 中文)。明度 0 深 / 1 中 / 2 浅
COLORS = {
    "black": (0, "low", "黑"), "grey_dark": (0, "low", "深灰"), "navy": (0, "low", "藏青"),
    "brown": (0, "low", "咖"), "burgundy": (0, "low", "酒红"),
    "grey": (1, "low", "中灰"), "olive": (1, "low", "橄榄绿"),
    "white": (2, "low", "白"), "grey_light": (2, "low", "浅灰"), "beige": (2, "low", "燕麦米"),
    "sage": (2, "low", "鼠尾草绿"),
    "red": (1, "high", "红"), "blue": (1, "high", "亮蓝"), "green": (1, "high", "亮绿"),
    "purple": (1, "high", "紫"), "orange": (1, "high", "橙"),
    "pink": (2, "high", "粉"), "yellow": (2, "high", "黄"), "neon": (2, "high", "荧光"),
}

# ---------- 单维：上衣类型 × 体型 ----------
TOP_BY_BUILD = {
    #               slim lean v_shape average high_fat
    "tank":          (-1,  1,   2,      0,     -2),
    "stringer":      (-2,  0,   2,     -1,     -2),
    "fitted_tee":    ( 1,  1,   1,      1,     -1),
    "regular_tee":   ( 0,  0,   0,      1,      1),
    "oversized_tee": (-1,  0,   0,      1,      2),
    "fitted_ls":     ( 1,  2,   1,      0,     -1),
    "loose_ls":      (-1,  0,   0,      1,      2),
    "sports_bra":    ( 0,  1,   1,      0,     -1),
    "crop_top":      ( 0,  1,   1,      0,     -1),
    "hoodie":        (-1,  0,   0,      1,      2),
    "zip_jacket":    ( 0,  0,   0,      0,      1),
}
BUILD_ORDER = ["slim", "lean", "v_shape", "average", "high_fat"]

# 单维：上衣松紧 × 体型（叠加在类型分上，只管压缩/宽松两头）
FIT_BY_BUILD = {
    "compression": {"slim": -1, "lean": 1, "v_shape": 1, "high_fat": -2},
    "loose": {"slim": -1, "high_fat": 1},
}

# 单维：上衣明度 × 体型
TOP_VALUE_BY_BUILD = {
    "slim": {2: 1, 1: 1},          # 浅色、中间色增加体积感
    "high_fat": {0: 1},            # 深色收
}

# 单维：下装类型 × 腿（强项 / 弱项 / 一般）
BOTTOM_BY_LEGS = {
    #             strong weak neutral
    "shorts_3":   ( 1,   -2,   0),
    "shorts_5":   ( 2,   -1,   1),
    "shorts_7":   ( 0,    1,   1),
    "shorts_2in1":( 1,    0,   1),
    "joggers":    ( 0,    1,   0),
    "leggings":   ( 2,    0,   1),
    "wide_pants": (-1,    1,   0),
}

# 单维：女生下装偏好（高腰紧身裤是女生健身穿搭的基本款）
FEMALE_BOTTOM_BONUS = {"leggings": (1, "高腰紧身裤显臀腿线条，女生基本款")}

# 单维：训练日 × 露出部位
DAY_BONUS = {
    "legs": ("bottom", EXPOSES_LEGS | {"leggings"}, 1, "练腿日露腿，方便看发力"),
    "pull": ("top", {"tank", "stringer", "fitted_tee", "fitted_ls"}, 1, "练背日上衣贴身/露背，看得清背部线条"),
    "push": ("top", {"tank", "stringer", "fitted_tee"}, 1, "推日露肩或贴身，看得清肩胸"),
    "arms": ("top", {"tank", "stringer"}, 1, "练手臂日露手臂"),
    "cardio": ("top", {"regular_tee", "oversized_tee", "tank"}, 1, "有氧日上衣透气不闷"),
}

# 单维：季节
SEASON_RULES = {
    "winter": {"bad": {"tank", "stringer", "shorts_3", "shorts_5", "crop_top"}, "good": {"fitted_ls", "loose_ls", "hoodie", "joggers"}},
    "summer": {"bad": {"loose_ls", "hoodie", "wide_pants"}, "good": {"tank", "shorts_5", "shorts_7", "shorts_2in1"}},
}

# 鞋 × 场景
SHOES_BY_SCENE = {
    "strength": {"flat_shoes": 1, "running_shoes": 0, "slides": -2},
    "video": {"flat_shoes": 1, "running_shoes": 0, "slides": -2},
    "cardio": {"running_shoes": 1, "flat_shoes": -1, "slides": -2},
}

# ---------- 交叉：上衣松紧 × 下装松紧 ----------
def fit_class(fit):
    return "tight" if fit in TIGHT else "loose" if fit in LOOSE else "regular"

FIT_CONTRAST = {
    ("tight", "loose"): (2, "上紧下松，比例清楚"),
    ("loose", "tight"): (2, "上松下紧，比例清楚"),
    ("tight", "regular"): (1, "上身贴合，下装常规"),
    ("tight", "tight"): (0, "上下都紧，只在同色套装时好看"),
    ("loose", "loose"): (-2, "上下都宽，像穿了睡衣"),
}

# 颜色数（全身不同颜色族数量）
def color_count_score(n):
    if n <= 2: return 2, f"全身 {n} 色，干净"
    if n == 3: return 1, "全身 3 色，在上限内"
    if n == 4: return 0, "全身 4 色，偏杂"
    return -2, f"全身 {n} 色，太花"

# ---------- 否决项 ----------
VETO_TEXT = {
    "neon_full": "荧光色再配其他亮色，全身太跳",
    "sheer_legs": "下装偏透，练腿深蹲会走光",
    "pattern_video": "拍视频穿细条纹或小格子，镜头会闪纹",
    "loose_loose_set": None,  # 预留
}

# ---------- 购买候选（通用款，不含品牌和价格） ----------
CATALOG = [
    {"type": "fitted_tee", "color": "black"},
    {"type": "fitted_tee", "color": "white"},
    {"type": "fitted_tee", "color": "olive"},
    {"type": "fitted_tee", "color": "grey_dark"},
    {"type": "oversized_tee", "color": "black"},
    {"type": "oversized_tee", "color": "beige"},
    {"type": "tank", "color": "black"},
    {"type": "tank", "color": "white"},
    {"type": "stringer", "color": "black"},
    {"type": "fitted_ls", "color": "black"},
    {"type": "fitted_ls", "color": "sage"},
    {"type": "loose_ls", "color": "grey_dark"},
    {"type": "hoodie", "color": "black"},
    {"type": "hoodie", "color": "beige"},
    {"type": "shorts_5", "color": "black"},
    {"type": "shorts_5", "color": "grey_dark"},
    {"type": "shorts_7", "color": "black"},
    {"type": "shorts_7", "color": "olive"},
    {"type": "shorts_2in1", "color": "black"},
    {"type": "joggers", "color": "black"},
    {"type": "joggers", "color": "grey_dark"},
    {"type": "leggings", "color": "black"},
    {"type": "leggings", "color": "sage"},
    {"type": "sports_bra", "color": "black"},
    {"type": "sports_bra", "color": "sage"},
    {"type": "crop_top", "color": "white"},
    {"type": "flat_shoes", "color": "white"},
    {"type": "flat_shoes", "color": "black"},
    {"type": "running_shoes", "color": "white"},
    {"type": "crew_socks", "color": "white"},
    {"type": "crew_socks", "color": "black"},
]

VERDICT = [(8, "推荐"), (4, "可以穿"), (-99, "不推荐")]

# 梯队（中文互联网 tier list 说法）：(最低分, 中文, English)。命中否决项直接"拉完了"。
TIERS = [
    (11, "夯", "GOAT"),
    (9, "顶级", "Top tier"),
    (7, "人上人", "Above the crowd"),
    (4, "NPC", "NPC"),
    (-99, "拉完了", "Cooked"),
]
