---
name: gym-outfit
description: 健身房穿搭：把衣服拆成属性向量（上衣/下装类型、松紧、颜色、鞋袜），按体型强弱项、训练日、场景多维打分，从已有衣服搭出前几套或算出买哪件提升最大。说"健身穿搭""练什么穿""搭一套""买训练服""这套好看吗"时用。
---

# 健身房穿搭

思路：**露强项、藏弱项、颜色收敛、松紧对比**。打分由 `scripts/score.py` 完成，你负责识别衣服、补全用户信息、把结果讲清楚。不要自己心算分数。

## 流程

1. **用户向量**：整理成 user.json。缺的字段不追问，按下面的默认值，在回复开头用一行写明假设：
   - 性别 m、体型 average、训练日 full、场景 strength；季节按当前日期推断（6–8 月夏，12–2 月冬，其余春秋）
   - "肚子明显"同时填 `build: high_fat` 和 `weaknesses: ["abs"]`；"宽松短袖"用 `oversized_tee`
   - 预算不进脚本，只用来控制推荐几件、先买哪件
2. **衣服向量**：把用户描述或照片里的每件衣服写成一条记录，字段只用下面词表里的值。看不清的属性取最可能的值，并在回复里注明。
3. **选命令**（脚本路径相对本 skill 目录）：
   - 从衣柜搭配：`python scripts/score.py rank --user user.json --wardrobe w.json --top 3`
   - 要买什么：`python scripts/score.py gap --user user.json --wardrobe w.json`
   - 评价一套：`python scripts/score.py score --user user.json --outfit o.json`
   - 用户既有衣柜又想买：先跑 rank，再跑 gap。
   - rank 返回 `too_few: true`（能搭的不到 3 套）时，也跑 gap。
4. **讲结果**：按下方输出格式，把 breakdown 翻译成人话，只挑影响最大的 2–3 条理由。语气像懂行的朋友，不要念规则名。
   - rank 输出里的 `veto_warnings` 一定要提：哪件单品、为什么别穿。
   - 同分的几套，说清它们的差别（比如"背心更显肩，短袖更日常"），让用户按心情选。
   - gap 里 `pair_gains` 不为空时，说明单买一件救不回来，要两件一起买。
   - 最后可以加一条实用提示（拍摄打光、热身先穿外套等），一句话。
5. **你不同意某个分数**：照实给出脚本结果，再单独说明你的看法，标注为"规则反馈"。不要改分数。

## 词表

**user**
- `sex`: m / f
- `build`: slim 偏瘦 · lean 薄肌 · v_shape V形 · average 普通 · high_fat 体脂偏高
- `strengths` / `weaknesses`: shoulders, back, arms, chest, abs, legs, glutes
- `day`: push, pull, legs, upper, arms, full, cardio
- `scene`: strength, cardio, video
- `season`: summer, spring_autumn, winter
- `emphasis`（可省略，由强项推出）：upper, lower, balanced

**衣服**（每件必填 `type`、`color`）
- 上衣：tank 宽肩带背心 · stringer 大挖肩 · fitted_tee 修身短袖 · regular_tee 常规短袖 · oversized_tee · fitted_ls 修身长袖 · loose_ls 宽松长袖 · sports_bra · crop_top
- 外层：hoodie 卫衣 · zip_jacket 拉链外套
- 下装：shorts_3 / shorts_5 / shorts_7（内档英寸）· shorts_2in1 · joggers 收脚裤 · leggings 紧身裤 · wide_pants
- 鞋袜配件：flat_shoes 平底鞋（帆布鞋、硬拉鞋）· running_shoes · slides · no_show_socks · crew_socks · long_socks · cap · belt · watch
- `color`: black, grey_dark, navy, brown, burgundy, grey, olive, white, grey_light, beige, sage, red, blue, green, purple, orange, pink, yellow, neon
- 可选：`fit`（compression/fitted/regular/loose，默认按类型）、`pattern`（solid/fine_stripe/small_check/big_logo/graphic）、`fabric`（cotton/quick_dry）、`sheer`（深蹲会透填 true）、`name`（用户自己的叫法，输出时显示）

## 输出格式

```
（假设：…）

【第 1 套 · 推荐 · 11 分】
上：…  下：…  鞋袜：…
为什么：露了什么、藏了什么、颜色怎么收（一两句）
扣分点：有就写，没有就省略

…第 2、3 套…

缺什么：gap 结果里提升最大的 1–3 件，写清类型、颜色、为什么
```

- 只问买什么时，省略"第 N 套"，直接写"缺什么"，再给一套买完后的搭法。
- 命中否决项的搭配不推荐，单独提醒一句为什么。
- 评级：8 分及以上"推荐"，4–7"可以穿"，4 以下"不推荐"。
- 不报价格。用户要品牌时现场搜索。
- 不评价身材好坏，只说怎么穿更好看。

## 规则在哪改

审美标准全在 `scripts/rules.py`：上衣×体型表、下装×腿表、颜色族、松紧对比、否决项、购买候选。改完运行 `python evals/run_evals.py` 确认用例仍然通过。
