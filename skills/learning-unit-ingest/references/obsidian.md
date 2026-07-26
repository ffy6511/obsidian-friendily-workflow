# Obsidian Learning Unit Reference

Use Obsidian wikilinks for vault-local relationships and normal Markdown links for external sources.

## Unit Template

```markdown
---
title: <Unit Title>
type: learning-unit
domain: <domain>
status: inbox
source: '<public-url>'
resource_type: html
tags:
  - <domain>
---

## 学习资源

- <主资料名称>: <<public-url>>

<iframe
  src="<public-url>"
  style="width:100%; height:300px; border:0;"
  allowfullscreen>
</iframe>

- <补充资料名称>: <<supplementary-public-url>>

<iframe
  src="<supplementary-public-url>"
  style="width:100%; height:300px; border:0;"
  allowfullscreen>
</iframe>

## 学习导引

这个学习单元主要帮助学习：...

它在这个领域中的位置是：...

资料之间的分工是：...

阅读或观看时优先关注：... ^guide

## 知识总览

### 核心脉络

...

### 关键概念

- [[...]]

### 需要区分的概念

- ...

## 我的笔记

### 这篇笔记解决什么问题

...

### 1. 从第一性原理展开

...

### 自检与资料出处

...
```

`## 学习资源` should start each resource with `- <resource name>: <URL>` and place the matching iframe immediately below it. `## 知识总览` is a compact map; `## 我的笔记` should contain the complete substantive learning note by default. Leave it empty only when the user explicitly requests a blank personal-notes area. Preserve existing user-authored note content unless the requested revision authorizes changing it.

One unit may aggregate multiple public URLs when the resources teach the same learning object from complementary angles. Use `source` for the primary URL. Add `sources` in frontmatter when useful:

```yaml
sources:
  - '<primary-public-url>'
  - '<supplementary-public-url>'
```

## Resource Types

Use `resource_type: html`, `youtube`, `bilibili`, `video`, or `other`.

For YouTube, use watch URLs for the visible resource line and embed URLs for iframe `src`:

```text
https://www.youtube.com/watch?v=<id>
https://www.youtube.com/embed/<id>
https://www.youtube.com/embed/<id>?start=90
```

Use the `watch?v=` URL in the visible resource line and `sources` metadata. Use `/embed/<id>` in iframe `src` for a cleaner embedded player. If a specific video blocks embedded playback, handle that unit as an exception.

For Bilibili, use the player URL when possible:

```text
https://player.bilibili.com/player.html?bvid=<bvid>&page=1&t=90&autoplay=0
```

## Domain Map Template

```markdown
---
title: <Domain Title>
type: learning-domain
status: active
tags:
  - learning-domain
  - <domain>
---

# <Domain Title>

## 学习目标

- ...

## Roadmap

![[learning/domains/<domain>/<Domain Title> roadmap.canvas]]

## 学习地图

### <topic group>

- [[learning/domains/<domain>/units/<Unit Title>|<Unit Title>]] - <why it matters>.![[learning/domains/<domain>/units/<Unit Title>#^guide]]

## 推荐路径

1. [[learning/domains/<domain>/units/<Unit Title>|<Unit Title>]]

## 概念索引

- [[...]]
```

Use `#^guide` embeds in the domain map so the map shows each unit's learning guidance directly.

## Domain Roadmap Canvas

Each domain map should have a paired `.canvas` roadmap. Use this visual convention:

- Center spine: main learning path nodes, orange `#f6a800`, with unit wikilinks.
- Side branches: supporting concepts and subtopics, blue `#b9dcff`, with blue branch lines `#2f7de1`.
- Third level: every side-branch concept should have a one-sentence explanation node, pale blue `#eaf4ff`.
- Explanation edges: connect second-level concepts to third-level explanations with gray `#9ca3af`, no arrow (`toEnd: "none"`), and horizontal center alignment.
- Neutral top blocks: prerequisites and usage notes, white.
- Node width: keep current text legible. Increase node width for long Chinese or mixed Chinese/English labels; do not leave clipped text.
