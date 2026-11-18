（假设：男生，偏瘦，练背日，力量训练，春秋季；"宽松短袖"按 oversize 短袖处理，"帆布鞋"按平底鞋处理。）

【第 1 套 · 推荐 · 8 分】
上：黑色修身短袖  下：黑色7寸短裤  鞋袜：白色帆布鞋
为什么：修身短袖适合偏瘦，练背日贴身能看清背部线条；上下同黑、加白鞋只有两个颜色，干净。
扣分点：无。

【第 2 套 · 可以穿 · 5 分】
上：黑色修身短袖  下：藏青收脚裤  鞋袜：白色帆布鞋
为什么：上衣同样贴身露背线；收脚裤和上衣是上紧下常规的对比。
扣分点：黑、藏青、白三色，在上限内但不如第 1 套干净；想穿长裤时选这套。

【第 3 套 · 不推荐 · 2 分】
上：浅灰纯棉宽松短袖  下：黑色7寸短裤  鞋袜：白色帆布鞋
为什么：浅色能给偏瘦的人加一点体积，但宽松 oversize 对偏瘦减分，背部线条也被盖住。
扣分点：宽松上衣、练背日看不到背；纯棉浅灰出汗显渍。想要"显壮"选第 1 套更稳。

## 过程记录

user.json:
```json
{"sex":"m","build":"slim","strengths":[],"weaknesses":[],"day":"pull","scene":"strength","season":"spring_autumn"}
```

wardrobe.json:
```json
[{"type":"fitted_tee","color":"black"},{"type":"oversized_tee","color":"grey_light","fabric":"cotton","name":"浅灰纯棉宽松短袖"},{"type":"shorts_7","color":"black"},{"type":"joggers","color":"navy"},{"type":"flat_shoes","color":"white","name":"白色帆布鞋"}]
```

命令：`python scripts/score.py rank --user /tmp/ab_with/01_slim_pull/user.json --wardrobe /tmp/ab_with/01_slim_pull/wardrobe.json --top 3`

猜测/不清楚：
- "宽松短袖"可以是 oversized_tee 或 regular_tee+fit:loose，词表没说，我选 oversized_tee。
- 季节没给，今天是 11 月但没说地点，按默认 spring_autumn；SKILL 没说是否用当前日期推季节。
- 第 3 套的"浅灰棉出汗显渍"规则只在 video/cardio 场景触发，这里没有打分，但我在文字里提了，这属于我自己的看法，应该标"规则反馈"，已按此理解处理（见下）。
- 规则反馈：浅灰纯棉上衣出汗显渍在力量训练场景也会发生，脚本未计分。
