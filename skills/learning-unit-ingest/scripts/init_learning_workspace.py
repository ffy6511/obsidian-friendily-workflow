#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


AGENTS = """# Learning Agent Workflow

这个目录维护个人领域学习工作流。核心对象是学习领域和学习单元：领域地图负责组织学习路径，学习单元负责承载公网资料、导学说明、知识脉络和用户自己的笔记。

当前结构：

```text
learning/
  AGENTS.md
  LEARNING.md
  domains/
    <domain>/
      <Domain Title>.md
      units/
        <unit-title>.md
      manifests/
        units.json
```

- `LEARNING.md` 是全局入口，列出所有学习领域。
- `domains/<domain>/<Domain Title>.md` 是领域地图，是进入该领域学习的主要入口。
- `domains/<domain>/units/` 存放一个个学习单元 note。
- `domains/<domain>/manifests/units.json` 是可选的批处理清单，服务 agent 批量创建、校验和审计。

## Use the Project Skill

新增、整理或校验学习单元时优先使用项目级 skill：

```text
learning-unit-ingest
```

从仓库根目录运行核心脚本：

```bash
python3 .agents/skills/learning-unit-ingest/scripts/init_learning_workspace.py --learning-root learning
python3 .agents/skills/learning-unit-ingest/scripts/validate_learning_workspace.py --learning-root learning
```

## Input

用户可能给出：

- 一个学习领域，例如 `Agentic RL`、`LLM Evaluation`、`Deep Learning`。
- 一个或多个公网 HTML 资料链接。
- YouTube、Bilibili 或其他可 iframe 嵌入的视频链接。
- 一个已有领域地图，需要补充学习单元、推荐路径或概念索引。
- 一个粗略学习目标，需要先搜索高质量公开资料并列出候选大纲。

当用户只给出领域时，先进入 discovery 阶段：搜索高质量资料，列出候选学习大纲，等待用户确认后再创建具体 unit note。

## Learning Unit

学习单元是最小学习对象。一个 unit 可以对应一个 URL，也可以聚合多个互补 URL，例如一篇主文档、一篇工程博客和一个视频讲解。

每个 unit note 使用固定顺序：

```markdown
---
title: <Unit Title>
type: learning-unit
domain: <domain>
status: inbox
source: "<primary public url>"
resource_type: html
tags:
  - <domain>
---

## 学习资源

- <资源名称>: <https://...>

<iframe ...></iframe>

- <补充资源名称>: <https://...>

<iframe ...></iframe>

## 学习导引

...

^guide

## 知识总览

...

## 我的笔记
```

- `学习资源` 放在正文最开头，按主资料、补充资料、视频讲解的顺序排列。
- 每个资源先写 `- 资源名称: <URL>`，下一行放对应 iframe，方便用户识别 iframe 内容并直接打开源页面。
- `source` 存主资料 URL；多个资料可在 frontmatter 中增加 `sources` 列表，或在 `学习导引` 中说明各资料分工。
- `学习导引` 说明这个 unit 学什么、在领域中的位置、各资料之间如何配合。
- `知识总览` 梳理整体脉络、核心概念和容易混淆的概念。
- `我的笔记` 初始化为空，留给用户自己填写。
- `^guide` 是领域地图嵌入学习导引的稳定 block id。

## Domain Maps

领域地图放在 `domains/<domain>/<Domain Title>.md`。它是该领域学习的主要入口，负责组织目标、路径、分组和概念索引。

推荐结构：

```markdown
# <Domain Title>

## 学习目标

- ...

## 学习地图

### <主题分组>

- [[learning/domains/<domain>/units/<Unit Title>|<Unit Title>]] - <为什么先学或值得学>.![[learning/domains/<domain>/units/<Unit Title>#^guide]]

## 推荐路径

1. [[learning/domains/<domain>/units/<Unit Title>|<Unit Title>]] - <阅读或观看理由>

## 概念索引

- [[...]]

## 待补资源

- ...
```

`学习地图` 用主题分组组织 unit。每个 unit 条目保留一行理由，并在同一 bullet 中嵌入 `#^guide`，方便快速浏览。

## LEARNING.md

`LEARNING.md` 只维护全局领域入口：

```markdown
# Learning

## 领域

- [[learning/domains/<domain>/<Domain Title>|<Domain Title>]]
```

## Verification

每次创建 unit、重命名 unit、更新领域地图或修改 manifest 后运行：

```bash
python3 .agents/skills/learning-unit-ingest/scripts/validate_learning_workspace.py --learning-root learning
```
"""


LEARNING = """# Learning

## 领域
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning-root", default="learning")
    parser.add_argument("--domain")
    parser.add_argument("--title")
    args = parser.parse_args()

    root = Path(args.learning_root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "domains").mkdir(exist_ok=True)

    agents = root / "AGENTS.md"
    if not agents.exists():
        agents.write_text(AGENTS, encoding="utf-8")

    learning = root / "LEARNING.md"
    if not learning.exists():
        learning.write_text(LEARNING, encoding="utf-8")

    if args.domain:
        title = args.title or args.domain
        domain_dir = root / "domains" / args.domain
        (domain_dir / "units").mkdir(parents=True, exist_ok=True)
        (domain_dir / "manifests").mkdir(exist_ok=True)
        manifest = domain_dir / "manifests" / "units.json"
        if not manifest.exists():
            manifest.write_text(json.dumps([], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        domain_map = domain_dir / f"{title}.md"
        if not domain_map.exists():
            domain_map.write_text(
                f"""---
title: {title}
type: learning-domain
status: active
tags:
  - learning-domain
  - {args.domain}
---

# {title}

## 学习目标

- 

## 学习地图

## 推荐路径

## 概念索引
""",
                encoding="utf-8",
            )

        entry = f"- [[learning/domains/{args.domain}/{title}|{title}]]\n"
        text = learning.read_text(encoding="utf-8")
        if entry not in text:
            learning.write_text(text.rstrip() + "\n\n" + entry, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
