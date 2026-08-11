# Obsidian Friendily Workflow Skills

个人用的 agent skills：写 Obsidian 库，以及日常开发里对齐理解、整理 commit。

分组方式参考 [mattpocock/skills](https://github.com/mattpocock/skills)：先说容易出什么问题，再列对应 skill。



## 模块

### #1：Obsidian 知识工作流

没有固定流程时，agent 容易各写各的 Markdown：地图、文献、雷达队列和笔记格式会散掉。

| Skill | 用途 |
| --- | --- |
| [`obsidian-markdown`](skills/obsidian-markdown/SKILL.md) | wikilink、embed、callout、properties 等 Obsidian 语法 |
| [`obsidian-vault`](skills/obsidian-vault/SKILL.md) | domain map、roadmap canvas、导航结构 |
| [`obsidian-format-validation`](skills/obsidian-format-validation/SKILL.md) | 校验 heading-fragment / block-ID wikilink |
| [`learning-unit-ingest`](skills/learning-unit-ingest/SKILL.md) | 公开页 / YouTube / Bilibili → `learning/` 单元与地图 |
| [`paper-md-ingest`](skills/paper-md-ingest/SKILL.md) | 论文 → `papers/`（含图表抽取） |
| [`knowledge-radar-actions`](skills/knowledge-radar-actions/SKILL.md) | 雷达 digest 勾选后的 deep-read / 论文 / 学习单元 |
| [`obsidian-public-sync`](skills/obsidian-public-sync/SKILL.md) | 私库笔记同步到公开 Quartz，保留路径和 wikilink 依赖 |

适合：改 vault 笔记、建 map、ingest 论文或学习材料、处理雷达队列、同步公开站。

---

### #2：日常开发协作

> "No-one knows exactly what they want"  
> — David Thomas & Andrew Hunt, *The Pragmatic Programmer*  
> （同类问题见 [mattpocock/skills §#1](https://github.com/mattpocock/skills#1-the-agent-didnt-do-what-i-want)）


| Skill | 用途 |
| --- | --- |
| [`as-far-as-i-know`](skills/as-far-as-i-know/SKILL.md) | 用户写当前理解；agent 先给结论（共识 / 部分共识 / 未达成共识 / 证据不足），再给**仓库/文档/代码**论据。不客套附和。 |
| [`as-the-field-knows`](skills/as-the-field-knows/SKILL.md) | 用户写观点；agent 先搜索开源/业界流行实现，再给结论（主流对齐 / 部分对齐 / 偏离主流 / 领域分裂 / 证据不足）与搜索论据。默认不用 subagent。 |
| [`spec-driven-delivery`](skills/spec-driven-delivery/SKILL.md) | 快节奏 SDD：短 Spec + 用户故事/验收；执行时按 Phase 提交（对齐 staged-commit-message）；中途对抗审查默认关，收尾默认 subagent 查验收与代码质量并改。 |
| [`staged-commit-message`](skills/staged-commit-message/SKILL.md) | 按 staged diff + 近期 commit 文风写 Conventional Commit。默认一条；意图能分开时（或用户要求时）拆多条，写入 `COMMIT.md`。只有用户明确说「提交」才 `git commit`。 |
| [`prepare-release`](skills/prepare-release/SKILL.md) | 发版准备：先核对/声明项目版本；默认只根据上次发版以来的提交起草中英双语 release note；只有用户明确说「直接发版 / ship」才 tag/发布。 |


## 其他
### 本地偏好

机器相关路径、工具选项放在各 skill 的 `preferences.toml`，**不进 git**。仓库只保留 `preferences.example.toml`。

```bash
cp skills/<name>/preferences.example.toml skills/<name>/preferences.toml
# 编辑 preferences.toml，设 initialized = true
```

根目录 `.gitignore` 已忽略 `**/preferences.toml`。新增带本机配置的 skill 时：example 进仓，真实文件 gitignore，SKILL.md 写清首次 setup。
