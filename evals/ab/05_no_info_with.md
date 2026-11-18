（假设：男生，体型普通，练全身，力量训练，春秋季；"黑短袖"按常规短袖，"灰短裤"按5寸、中灰，"白鞋"按平底鞋。这些都是猜的，不对告诉我。）

【第 1 套 · 可以穿 · 4 分】
上：黑色常规短袖  下：中灰5寸短裤  鞋袜：白色平底鞋
为什么：就一套，三色在上限内，常规短袖适合普通体型，5 寸短裤露一点腿，平底鞋适合力量训练。
扣分点：没有明显扣分，也没有亮点，只是中规中矩。

想更好看：上下松紧做一点对比，例如换修身短袖，或者上下同色，会更出彩。

## 过程记录

user.json:
```json
{"sex":"m","build":"average","strengths":[],"weaknesses":[],"day":"full","scene":"strength","season":"spring_autumn"}
```

wardrobe.json:
```json
[{"type":"regular_tee","color":"black"},{"type":"shorts_5","color":"grey"},{"type":"flat_shoes","color":"white"}]
```

命令：`python scripts/score.py rank --user ... --wardrobe ... --top 3`

猜测/不清楚：
- 用户几乎没给信息，性别、体型、训练日、季节全按默认；SKILL 说"缺的字段按常见情况假设"但没列出默认值，我参考 score.py 的 norm_user 默认值（m/average/full/strength/spring_autumn）。
- 短裤长度、鞋类型是猜的；"白鞋"如果是跑鞋，结果会不同（平底鞋力量训练 +1，跑鞋 0）。
- 衣柜只有 3 件，rank 只出 1 套，--top 3 实际只有 1 套，SKILL 没说此时是否还要跑 gap；我没跑。
- "想更好看"那句是我自己的建议，不是脚本结果。
