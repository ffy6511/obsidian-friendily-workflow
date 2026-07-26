# Learning Workspace Reference

Use this reference when initializing or changing `learning/`.

## Shape

```text
learning/
  AGENTS.md
  LEARNING.md
  domains/
    <domain>/
      <Domain Title>.md
      <Domain Title> roadmap.canvas
      units/
      manifests/
        units.json
```

Keep public source material on the web. Store learning maps, unit notes, manifests, and Obsidian links in the vault.

## `learning/AGENTS.md`

Create this file when missing:

````markdown
# Learning Agent Workflow

这个目录维护个人领域学习工作流。核心对象是学习领域和学习单元：领域地图负责组织学习路径，学习单元负责承载公网资料、导学说明、知识脉络和用户自己的笔记。

当前结构：

```text
learning/
  AGENTS.md
  LEARNING.md
  domains/
    <domain>/
      <Domain Title>.md
      <Domain Title> roadmap.canvas
      units/
        <unit-title>.md
      manifests/
        units.json
```
````

- `LEARNING.md` 是全局入口，列出所有学习领域。
- `domains/<domain>/<Domain Title>.md` 是领域地图，是进入该领域学习的主要入口。
- `domains/<domain>/<Domain Title> roadmap.canvas` 是领域配套路线图，使用橙色主线和蓝色分支。
- `domains/<domain>/units/` 存放一个个学习单元 note。
- `domains/<domain>/manifests/units.json` 是可选的批处理清单，服务 agent 批量创建、校验和审计。

````

## `learning/LEARNING.md`

Use this as the global entry:

```markdown
# Learning

## 领域

- [[learning/domains/<domain>/<Domain Title>|<Domain Title>]]
````

## Domain Directory

For each domain:

```text
learning/domains/<domain>/
  <Domain Title>.md
  <Domain Title> roadmap.canvas
  units/
  manifests/
    units.json
```

The domain map is the reading entry point. The roadmap canvas is the visual learning path for the domain. `units.json` is optional automation metadata.
