---
name: docs-substance
description: >
  Review and rewrite any documentation for reader value and content substance:
  name the reader, replace jargon they would not know, place each claim in the
  right slot of the document layout (expected vs basic vs beyond-expectation).
  Use only when the user explicitly invokes $docs-substance / /docs-substance
  / "文档内容审查". Do not auto-load on ordinary doc edits. Not a substitute
  for dedicated anti-AI-style skills; include only a short rewrite hygiene pass.
disable-model-invocation: true
---

# Docs Substance

审查并改写**任意文档**的事实与内容：谁在读、值不值得留、该放在这篇布局的哪一格。  
不是只审 README / landing，也不是只写亮点栏。

文风不是主业。改写时做短的防套话。完整去 AI 味交给 `$humanizer-zh` / `$shuorenhua` / `$no-ai-slop`。

仅当用户显式调用 `$docs-substance` / `/docs-substance` 时使用。先审查，用户说改再改。不要提交，除非用户要求。

## 流程

1. **点名读者和这篇的栏。** 谁在读、在哪读、实际有哪些栏。细则：[references/reader.md](references/reader.md)。
2. **把每条主张分进三层，再对栏。** 细则：[references/placement.md](references/placement.md)。
3. **黑话。** 按 reader.md 的测试换词。有问答栏也走 reader.md。
4. **改写（若用户要求）。** 按层挪栏或删。改完走 [references/hygiene.md](references/hygiene.md)。
5. **词表。** 仓库已有检查就跑。要冻结再用 [references/glossary.md](references/glossary.md) 和 [scripts/check_banned_terms.py](scripts/check_banned_terms.py) 建。

对照反例：[references/examples.md](references/examples.md)。需要时才读，不要一上来整份灌进上下文。

## 报告

审查阶段先给表，再动手：

| 主张 | 层（默认 / 基本 / 超出预期） | 现在所在栏 | 应去哪（特点栏 / 正文 / 删） | 黑话？ |
| --- | --- | --- | --- | --- |

改写后：动了哪些栏、删了什么、词表脚本是否跑过。
