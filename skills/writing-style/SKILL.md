---
name: writing-style
description: >
  Constrain Chinese writing: detect bureaucratic jargon that is not ordinary
  vocabulary (抓手, 赋能, 颗粒度, 拉通, 闭环管理, 组合拳, …) and overused contrast
  frames (不是 X，而是 Y / 不仅仅是 X，更是 Y). Do not invent obscure
  metaphors or treat private imagery as vocabulary; name the actual object.
  Run scripts/check_writing_style.py on drafts; the script prints replacements
  and extracts X/Y so each contrast can be judged. Keep a contrast only when X
  is a real competing reading; otherwise write Y only. Soft-limit contrasts per
  piece — do not stack them. Metaphors are judged by eye, not by the script.
  Apply automatically whenever drafting or editing Chinese prose in notes,
  docs, replies, slides, or commit messages; do not wait for $writing-style or
  /writing-style. Skip code, inline code, URLs, and quoted titles. Not a full
  anti-AI-slop rewrite (shuorenhua / humanizer-zh / no-ai-slop).
---

# Writing Style

中文里不要用机关腔、咨询腔、互联网黑话冒充常用词。`抓手` 不是口语。也不要靠「不是 X，而是 Y」制造顿悟感。文档里不要塞读者解不开的自造隐喻。

权威数据（只覆盖词和对比句式）：

- 词：[references/banned-terms.tsv](references/banned-terms.tsv)
- 句式：[references/sentence-patterns.tsv](references/sentence-patterns.tsv)

本文件不复述词条。去 AI 套话、改节奏交给 `$shuorenhua` / `$humanizer-zh` / `$no-ai-slop`。本 skill 管：词是不是日常汉语；对比句的 X 值不值得出现；有没有把私有比喻当成在写事实。

## 默认就做

写或改中文正文时自动执行，用户不必调用 `$writing-style`。

不要用在：代码、配置、日志、论文标题/引用原文、用户明确要求保留的原文。

## 流程

1. 写完或改完中文后跑检测脚本，不要靠眼扫。
2. 每个 `ban` 词必须改掉或删掉。
3. 每个 `flag` 词先看 `keep_if`：符合则留，否则换成脚本给出的日常说法。
4. 每条对比句式按下面「怎么判 X」处理；超软上限的默认再砍。
5. 改完再跑一遍，直到没有 `ban`、剩下的 `flag` / 句式都有理由。
6. 再目测自造隐喻（脚本不管）：读者要猜「这对应哪件实事」就删比喻、写那件事。
7. 词表没有、但读起来仍是机关腔或假对比的，按同类处理，并考虑补表。隐喻不入库。

## 怎么判 X

脚本会标出「不是 X，而是 Y」的 X / Y 和本篇次数，**不替你决定逻辑**。你必须逐条问：

1. 读者此刻会以为是 X 吗？（上文刚说错，或这是真会混的术语/指称。）
2. 不写 X，Y 会被误读吗？
3. X 和 Y 是真对立，还是为了句式硬凑的反例？（没有必然联系就不是对立。）

三条有一条是「否」，就删掉「不是 X」，直接写 Y。连「而是」也常一起删：`而是管理问题` → `这是管理问题`。

可留的例子：`这里的「关闭」不是杀进程，而是断开连接。`（术语消歧）

不留的例子：`文献不是一堆文件，而是工作材料。`（没人必须先否定「文件」；直接写后半。）

软上限在句式表里（默认每篇每种 1 次）。未超限不等于自动可留；超限则更应删，同一篇不要堆对比。

## 自造隐喻

脚本不检测。写文档、笔记、说明时默认禁止晦涩的自造比喻，也不要把比喻当成术语用。

- 读者必须猜「这对应现实里哪一件」→ 删掉比喻，写那一件。
- 领域里已经是词的可留（栈、管道、缓存、垃圾回收）。你自己造的意象不留（飞轮燃料、心智压舱石、把流程织成网）。
- 引用原文里的比喻可留；不要接着往下延伸成一套私有意象。
- 一次性明喻且两边都点名（A 像 B，因为…）可以。用隐喻代替机制、或一段里混好几套比喻，不行。
- 改法：换成主语 + 动作 + 对象。比喻能删就删，不要换成另一个更新鲜的比喻。

## 脚本

从本 skill 目录跑（本文件所在目录）。词表按脚本自己的位置解析，不要写仓库根下的 `.agents/skills/...`。

```bash
python3 scripts/check_writing_style.py --text '以调研为抓手推进'
python3 scripts/check_writing_style.py path/to/note.md
python3 scripts/check_writing_style.py --json path/to/note.md
```

标准输入：

```bash
pbpaste | python3 scripts/check_writing_style.py --stdin
```

退出码：`0` 无命中，`1` 有词或句式命中，`2` 用法或数据错误。

脚本跳过围栏代码、行内代码、URL。反引号里讨论用词本身不算违规。

## 怎么改词

- 先换成词表里的日常说法，再按句子收紧，不要用另一个黑话替换。
- 多种替换里，选能说清**谁对谁做了什么**的那个。
- 删掉更清楚就删。引用、书名、接口名、论文标题里的原词保留。

## 补表

新黑话或新对比骨架只在这两种情况入库：现有条目吃不住，或误杀边界变了。

词加 `banned-terms.tsv`，句式加 `sentence-patterns.tsv`，列顺序与表头一致，然后：

```bash
python3 scripts/check_writing_style.py --self-test
```
