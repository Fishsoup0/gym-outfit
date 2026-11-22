# Changelog

## v1.1 — 2026-11-22
- 衣服库：`closet add / list / remove / clear` 保存衣柜，`profile set / show` 保存身材档案，存在 `~/.gym-outfit/`
- `rank` / `gap` 不传参数时直接用已保存的衣柜和档案
- 衣柜里搭不出"人上人"以上时，自动附上购买建议（单件和两件组合）
- README：定位为通用 Agent Skill，补充 Claude、ChatGPT、Codex、Gemini CLI、DeepSeek Harness 等安装方式

## v1.0 — 2026-11-19
- 五档梯队：夯 / 顶级 / 人上人 / NPC / 拉完了，中英文输出

## v0.1 — 2026-11-18
- 属性向量 + 规则打分引擎（单维适配、交叉兼容、一票否决）
- `score` / `rank` / `gap` 三个命令，6 个评测用例，单元测试
