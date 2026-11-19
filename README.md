# gym-outfit

**把健身房穿搭拆成属性向量、多维打分的 Claude Skill。**

> **Summary.** gym-outfit is a Claude Agent Skill for gym outfit recommendation. Claude identifies each garment as an attribute vector (type, fit, color, pattern), and a standard-library Python scorer (`scripts/score.py` with rules in `scripts/rules.py`) ranks outfits, finds the most valuable item to buy, or rates a single outfit, with a reason for every point. All aesthetic rules live in one editable file.

## 它能做什么

| 用法 | 命令 | 回答的问题 |
| --- | --- | --- |
| 搭配 (rank) | `score.py rank` | 从我现有的衣柜里，搭出得分最高的前 3 套 |
| 补缺 (gap) | `score.py gap` | 再买哪一件，对整体搭配的提升最大 |
| 评价 (score) | `score.py score` | 这一套好不好看，好在哪、扣在哪 |

既有衣柜又想买衣服时，先 rank 再 gap。

## 核心思路

四条审美原则：

- **露强项**：肩、背、手臂是强项就选能露出来的上衣。
- **藏弱项**：弱项用宽松、深色或长袖带过，不硬露。
- **颜色收敛**：全身最好不超过 3 个颜色，避免高饱和撞色。
- **松紧对比**：上紧下松或上松下紧，上下都宽会显得松垮。

工程上的分工是 **感知交给 Claude，打分交给代码**。Claude 擅长从文字和照片里认出衣服，但不擅长稳定地算分；脚本不会看图，但同样的输入永远得到同样的分数。

```
 用户文字 / 照片
        |
        v
 Claude 识别属性向量      (type, color, fit, pattern ...)
        |
        v
 score.py  <---  rules.py   (确定性打分，只用标准库)
        |
        v
 带理由的推荐              (总分 + 逐条 breakdown + 否决项)
```

## 打分维度

每条规则的分值在 -2 到 +2 之间，总分是所有命中规则之和。

| 类别 | 规则 |
| --- | --- |
| 单维适配 | 上衣×体型、松紧×体型、明度×体型、下装×腿、训练日、季节、场景、鞋×场景、露强项/藏弱项 |
| 交叉兼容 | 上松紧×下松紧、明度×重点、同色套装、颜色数、撞色、呼应、袜×下装、logo |
| 一票否决 | 全身两件以上荧光色、练腿日下装偏透（深蹲会透）、拍视频穿细条纹或小格子 |

命中否决项的搭配直接判为"拉完了"。按总分分梯队：

| 分数 | 梯队 | English |
|---|---|---|
| ≥ 11 | 夯 | GOAT |
| 9–10 | 顶级 | Top tier |
| 7–8 | 人上人 | Above the crowd |
| 4–6 | NPC | NPC |
| ≤ 3 或命中否决 | 拉完了 | Cooked |

Skill 支持中英文：用什么语言问，就用什么语言回答。

## 示例

数据取自 `evals/cases/03_vshape_video.json`：V 形男生，肩背是强项，推日、夏天、要拍视频；衣柜里有黑色大挖肩背心、黑白细条纹短袖、白色修身短袖、浅灰纯棉短袖、黑色 5 寸短裤、橄榄绿 7 寸短裤、白色帆布鞋、白色中筒袜。

```bash
cd gym-outfit
python3 scripts/score.py rank --user /tmp/user.json --wardrobe /tmp/wardrobe.json
```

输出（节选第 1 套和否决提醒，其余字段省略）：

```json
{
  "outfits": [{
    "total": 12,
    "verdict": "推荐",
    "tier": "夯",
    "tier_en": "GOAT",
    "items": ["黑大挖肩背心", "黑5寸短裤", "白平底鞋", "白中筒袜"],
    "breakdown": [
      { "kind": "单维", "rule": "上衣×体型",     "score": 2, "reason": "大挖肩背心适合V形" },
      { "kind": "单维", "rule": "露强项",       "score": 1, "reason": "露出肩臂这个强项" },
      { "kind": "单维", "rule": "下装×腿",       "score": 1, "reason": "5寸短裤：腿一般时合适" },
      { "kind": "单维", "rule": "训练日",       "score": 1, "reason": "推日露肩或贴身，看得清肩胸" },
      { "kind": "单维", "rule": "季节",         "score": 1, "reason": "夏天穿5寸短裤合适" },
      { "kind": "单维", "rule": "鞋×场景",       "score": 1, "reason": "拍视频穿平底鞋合适" },
      { "kind": "交叉", "rule": "上松紧×下松紧", "score": 1, "reason": "上身贴合，下装常规" },
      { "kind": "交叉", "rule": "同色套装",     "score": 1, "reason": "上下同为黑，同色套装" },
      { "kind": "交叉", "rule": "颜色数",       "score": 2, "reason": "全身 2 色，干净" },
      { "kind": "交叉", "rule": "袜子",         "score": 1, "reason": "短裤露出白中筒袜，和鞋或衣服同色，下半身收得干净" }
    ]
  }],
  "veto_warnings": [
    { "reason": "拍视频穿细条纹或小格子，镜头会闪纹", "involved_items": ["黑白细条纹短袖"] }
  ]
}
```

10 条规则加起来 12 分，梯队"夯"。黑白细条纹短袖被一票否决，并在 `veto_warnings` 里单独点名。

## 安装

**(a) Claude.ai / Claude App**

把整个 `gym-outfit/` 文件夹压缩成 zip，在 设置 → Skills 里上传；或者直接让 Claude 帮你保存为 Skill。

**(b) Claude Code**

```bash
git clone https://github.com/<you>/gym-outfit ~/.claude/skills/gym-outfit
```

运行时只需要 `SKILL.md` 和 `scripts/`，`tests/` 和 `evals/` 仅用于开发，打包时可以去掉。脚本只依赖 Python 3 标准库。

## 用法

安装后直接用自然语言说，Claude 会补全缺失信息（并写明假设）、调用脚本、再把结果讲清楚：

```
今天练背，我偏瘦，衣柜里有黑色修身短袖、灰色宽松卫衣、黑色 5 寸短裤、白色帆布鞋，帮我搭一套。
```

```
我是女生，腿和臀是强项，想拍一条练腿日的视频，现在只有两件黑色运动内衣，该买哪件提升最大？
```

```
这套好看吗：亮绿色背心 + 橙色短裤 + 紫色跑鞋，在健身房练有氧穿。
```

## 调规则

审美标准全部在 `scripts/rules.py`：上衣×体型表、下装×腿表、颜色族、松紧对比、否决项、购买候选清单。`score.py` 只负责按规则计算，不需要改。

改完后运行：

```bash
python3 evals/run_evals.py     # 6 个场景用例，加 -v 查看每个用例的前几名
python3 -m pytest -q tests     # 单元测试
```

## 目录结构

```
gym-outfit/
├── SKILL.md              # Skill 入口：流程、词表、输出格式
├── scripts/
│   ├── rules.py          # 规则表（调审美只改这里）
│   └── score.py          # 打分引擎：score / rank / gap
├── evals/
│   ├── run_evals.py      # 用例运行器
│   └── cases/            # 6 个端到端用例（JSON）
└── tests/                # 单元测试
```

## 开发路线

- [x] **v1 规则打分**（当前）：手写规则表，可解释、可复现。
- [ ] **v2 用户反馈校准权重**：收集"这套我愿意穿 / 不愿意穿"，用来调整各规则的分值。
- [ ] **v3 照片自动识别属性**：从衣柜或穿搭照片直接提取属性向量，减少手动描述。
- [ ] 可选：引入 CLIP 图文相似度，作为一个补充打分维度，不替代规则。

## License

MIT
