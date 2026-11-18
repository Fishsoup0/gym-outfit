（假设：男生，体脂偏高、腹部是弱项，冬季练全身，力量训练；"oversize"按 oversize 短袖、"跑鞋"按 running_shoes 处理。）

【第 1 套 · 推荐 · 9 分】
上：黑色 oversize 短袖 + 深灰卫衣  下：黑色收脚裤  鞋袜：白色跑鞋
为什么：宽松上衣和卫衣盖住腰腹，深色收身形；冬天卫衣加收脚裤合适。颜色是黑、深灰、白三色，在上限内。
扣分点：无。热了脱掉卫衣就是第 2 套。

【第 2 套 · 推荐 · 8 分】
上：黑色 oversize 短袖  下：黑色收脚裤  鞋袜：白色跑鞋
为什么：上下同黑、只有黑白两色，最干净，宽松上衣藏腹。
扣分点：无。

【第 3 套 · 推荐 · 8 分】
上：黑色 oversize 短袖  下：黑色5寸短裤  鞋袜：白色跑鞋
为什么：结构和第 2 套一样，只是露腿。
扣分点：冬天短裤脚本没扣分，但我觉得偏冷，热身前不建议。

不推荐：白色修身短袖，浅色贴身会放大腰腹；脚本排序里也靠后，没进前三。

## 过程记录

user.json:
```json
{"sex":"m","build":"high_fat","strengths":[],"weaknesses":["abs"],"day":"full","scene":"strength","season":"winter"}
```

wardrobe.json:
```json
[{"type":"fitted_tee","color":"white"},{"type":"oversized_tee","color":"black"},{"type":"hoodie","color":"grey_dark"},{"type":"joggers","color":"black"},{"type":"shorts_5","color":"black"},{"type":"running_shoes","color":"white"}]
```

命令：`python scripts/score.py rank --user ... --wardrobe ... --top 3`

猜测/不清楚：
- "肚子明显"我填成 weaknesses:["abs"]，同时 build=high_fat；SKILL 没说这种情况怎么填，实际 abs 弱项对没穿 crop_top 的搭配没有影响。
- 脚本里 oversize 短袖和卫衣各算一次"上衣×体型"+2，叠穿等于双倍加分，我觉得不合理（规则反馈：叠穿应只算可见上衣一次，或外层算、内层不算）。
- 第 1 套 4 件、第 2/3 套无外层，top-N 去重按 item_ids 前两项（上衣+外层或上衣+下装）算，导致第 1 套和"同上衣不同下装"的带卫衣版本被合并，实际没有"卫衣+短裤"这个选项出现，SKILL 没说明。
- 冬天短裤脚本不扣分（bad 只含 shorts_3），第 3 套 8 分推荐，我在文字里写了不同意，标为规则反馈，没有改分。
