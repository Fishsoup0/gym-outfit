（假设：男生，V形，肩背是强项，推日，拍视频，春秋季；黑白细条纹短袖按 regular_tee+fine_stripe 处理，"浅灰纯棉"按 cotton。）

【第 1 套 · 推荐 · 10 分】
上：黑色大挖肩背心  下：黑色5寸短裤  鞋袜：白色帆布鞋
为什么：大挖肩露出肩背这个强项，推日也看得清肩；上下同黑、加白鞋只有两色。
扣分点：无。

【第 2 套 · 推荐 · 10 分】
上：白色修身短袖  下：黑色5寸短裤  鞋袜：白色帆布鞋
为什么：上浅下深，视线集中在上身；白鞋和白上衣呼应。不露肩，更保守。
扣分点：无。

【第 3 套 · 推荐 · 10 分】
上：白色修身短袖  下：橄榄绿7寸短裤  鞋袜：白色帆布鞋
为什么：同样上浅下深，橄榄绿比黑柔和一点。
扣分点：无。

不要穿：黑白细条纹短袖，拍视频镜头会闪纹，直接否决；浅灰纯棉短袖出汗显渍，也不适合拍摄。白色中筒袜不改变得分，穿不穿都行。

## 过程记录

user.json:
```json
{"sex":"m","build":"v_shape","strengths":["shoulders","back"],"weaknesses":[],"day":"push","scene":"video","season":"spring_autumn"}
```

wardrobe.json:
```json
[{"type":"stringer","color":"black"},{"type":"regular_tee","color":"black","pattern":"fine_stripe","name":"黑白细条纹短袖"},{"type":"fitted_tee","color":"white"},{"type":"regular_tee","color":"grey_light","fabric":"cotton","name":"浅灰纯棉短袖"},{"type":"shorts_5","color":"black"},{"type":"shorts_7","color":"olive"},{"type":"flat_shoes","color":"white","name":"白色帆布鞋"},{"type":"crew_socks","color":"white"}]
```

命令：`python scripts/score.py rank --user ... --wardrobe ... --top 3`

猜测/不清楚：
- 季节没给，按 spring_autumn。
- 前三套都是 10 分并列，脚本没有二级排序，我按输出顺序写；也没说并列时该怎么讲。
- 袜子在所有套装里都不加分（呼应规则只取第一个，鞋已经触发），所以 rank 永远不会把袜子放进推荐，白色中筒袜这个输入被浪费，我只能手动提示。
- 否决项（细条纹）对应的搭配被排到最后，没出现在 rank 结果里；SKILL 说"命中否决项的搭配不推荐，单独提醒一句"，我是从衣柜内容自己看出来的，不是脚本输出的。
- "黑白细条纹"填 color:black 是猜的。
