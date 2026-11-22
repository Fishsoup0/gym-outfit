# gym-outfit

**健身房穿搭打分与推荐的 AI 技能包：记住你的衣柜和身材，告诉你今天穿哪套、这套是哪一档、缺什么该买什么。**

遵循 [Agent Skills](https://agentskills.io) 开放标准，同一个文件夹可以装进 Claude、ChatGPT、Codex、Gemini CLI、DeepSeek、Cursor 等支持这个标准的 AI 工具里，不绑定任何一家。

> **Summary.** gym-outfit is an open Agent Skill for gym outfits. The AI reads each garment as an attribute vector (type, fit, color, pattern); a standard-library Python scorer ranks outfits from your saved wardrobe, rates a single look on a 5-tier scale, and tells you which item to buy when nothing in your closet works. It runs in any agent that supports the Agent Skills standard.

## 它能做什么

| 你说 | 它做 | 命令 |
| --- | --- | --- |
| "这套怎么样？"（发照片或描述） | 打分 + 梯队（夯 / 顶级 / 人上人 / NPC / 拉完了）+ 升一档的最小改法 | `score` |
| "今天练背，穿什么？" | 从**已保存的衣柜**里搭出前 3 套 | `rank` |
| "买什么能变好看？" | 算出买哪件（或哪两件）提升最大 | `gap` |
| "帮我把这些衣服存起来" | 建立你的**衣服库**和**身材档案**，以后不用重复说 | `closet` / `profile` |

衣柜里搭不出"人上人"以上的一套时，会**自动附上购买建议**：现在最好能穿到哪一档，买哪一件能升到哪一档。

## 核心思路

四条审美原则：**露强项、藏弱项、颜色收敛、松紧对比**。

工程上的分工是 **看图交给 AI，打分交给代码**：AI 擅长从文字和照片里认出衣服，但不擅长稳定地算分；脚本不会看图，但同样的输入永远得到同样的分数。

```
 照片 / 文字 ──▶ AI 识别成属性向量 ──▶ score.py（规则在 rules.py）──▶ 梯队 + 理由 + 改法 / 购买建议
                                        ▲
                     ~/.gym-outfit/ 里保存的衣柜和身材档案
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

运行时只需要 `SKILL.md` 和 `scripts/` 两部分，脚本只依赖 Python 3 标准库。`tests/` 和 `evals/` 只在开发时用到。

### 一条命令装进多个工具（推荐）

[`skills` CLI](https://github.com/vercel-labs/skills) 会自动检测你电脑上装了哪些 AI 工具，然后装到对应目录：

```bash
npx skills add Fishsoup0/gym-outfit
```

### 按工具手动安装

| 工具 | 安装方式 |
| --- | --- |
| **Claude Code** | `git clone https://github.com/Fishsoup0/gym-outfit ~/.claude/skills/gym-outfit` |
| **Claude 网页版 / App** | 把 `gym-outfit/` 文件夹压成 zip，在设置的 Skills 页面上传 |
| **ChatGPT** | Skills → Create → Upload from your computer，上传 zip。网页版、桌面版能否使用独立技能取决于账号类型，以 OpenAI 帮助文档为准 |
| **Codex CLI** | `git clone https://github.com/Fishsoup0/gym-outfit ~/.agents/skills/gym-outfit`（旧版本读 `~/.codex/skills/`），在对话里用 `/skills` 或 `$gym-outfit` 调用 |
| **Gemini CLI** | `gemini skills install https://github.com/Fishsoup0/gym-outfit` |
| **DeepSeek Harness（dsh）** | 克隆到 `~/.agents/skills/gym-outfit`，或项目内的 `.dsh/skills/gym-outfit` |
| **Cursor / GitHub Copilot / OpenCode 等** | 用上面的 `npx skills add`，或克隆到工具对应的 skills 目录 |
| **阿里云百炼 / 腾讯云等云平台智能体** | 上传 zip。注意有的平台要求 zip **根目录直接是 `SKILL.md`**，不能外面再包一层文件夹：在 `gym-outfit/` 目录**里面**执行 `zip -r ../gym-outfit.zip SKILL.md scripts` |

### 豆包、Kimi、DeepSeek 网页版这类聊天 App

到目前为止，我没有查到这几款 App 支持上传自定义技能包的官方说明。可以用退而求其次的方法：新建对话，把 `SKILL.md` 的全文粘贴进去，说"按这个流程帮我看穿搭"。

这样用有两个限制：
- 这些 App 不会运行 `scripts/` 里的打分脚本，分数会由模型按规则估算，同一套衣服每次的分数可能不一样。
- 衣柜不会自动保存，要靠你每次把衣服清单发给它。

### 关于衣柜存储

衣柜和身材档案默认保存在 `~/.gym-outfit/closet.json` 和 `profile.json`，是普通 JSON 文件，可以自己打开修改。用环境变量 `GYM_OUTFIT_HOME` 可以换位置。

在 Claude Code、Codex、Gemini CLI 这类本地工具里，这两个文件会一直保留。有些网页聊天每次对话都会重置运行环境，那里存不住，需要每次把衣服清单发一遍。

## 用法

装好以后直接用自然语言说：

```
帮我把衣服存起来：黑色修身短袖、灰色宽松卫衣、黑色 5 寸短裤、白色帆布鞋。我 178、偏瘦、肩是强项。
```

```
今天练背，穿什么？
```

```
这套怎么样？（附照片）
```

```
衣柜里没有好看的组合，买什么提升最大？
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
├── SKILL.md              # 技能入口：流程、词表、输出格式
├── scripts/
│   ├── rules.py          # 规则表（调审美只改这里）
│   └── score.py          # 打分引擎：score / rank / gap，衣柜 closet / 身材档案 profile
├── evals/
│   ├── run_evals.py      # 用例运行器
│   └── cases/            # 6 个端到端用例（JSON）
└── tests/                # 单元测试
```

## 开发路线

- [x] **v1 规则打分**：手写规则表，可解释、可复现。
- [x] **v1.1 衣服库**：保存衣柜和身材档案，直接按衣柜推荐；搭不出好看的自动给购买建议；五档梯队；中英文。
- [ ] **v2 用户反馈校准权重**：收集"这套我愿意穿 / 不愿意穿"，用来调整各规则的分值。
- [ ] **v3 照片自动识别属性**：从衣柜或穿搭照片直接提取属性向量，减少手动描述。
- [ ] 可选：引入 CLIP 图文相似度，作为一个补充打分维度，不替代规则。

## License

MIT
