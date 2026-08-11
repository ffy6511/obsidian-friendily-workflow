/* Progressive left-prose / right-code walkthrough runtime. Content: window.SITE_CONTENT */

(function () {
  "use strict";

  const content = window.SITE_CONTENT;
  if (!content || !Array.isArray(content.lessons) || !content.lessons.length) {
    document.getElementById("app").innerHTML =
      '<main style="padding:48px;font-family:system-ui">Missing <code>SITE_CONTENT</code>. Run the scaffold script.</main>';
    return;
  }

  const site = content.site || {};
  const lessons = content.lessons;
  const themeKey = site.themeStorageKey || "cws-theme";
  const repoLabel = site.repoLabel || "repo /";

  document.documentElement.lang = site.lang || "zh-CN";
  document.title = site.title || site.brand || "Code Walkthrough";
  if (site.description) {
    let meta = document.querySelector('meta[name="description"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "description";
      document.head.appendChild(meta);
    }
    meta.content = site.description;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function renderMarkdown(markdown) {
    const withAnchors = String(markdown || "").replace(
      /<!--\s*checkpoint:\s*([a-zA-Z0-9_-]+)\s*-->/g,
      '<div class="checkpoint-anchor" data-checkpoint="$1" aria-hidden="true"></div>',
    );

    const renderer = new marked.Renderer();
    renderer.code = function ({ text, lang }) {
      const language = lang && hljs.getLanguage(lang) ? lang : "plaintext";
      const highlighted = hljs.highlight(text, { language, ignoreIllegals: true }).value;
      return `<pre class="article-code" data-language="${escapeHtml(lang || "code")}"><code>${highlighted}</code></pre>`;
    };
    renderer.link = function ({ href, title, tokens }) {
      const text = this.parser.parseInline(tokens);
      const external = /^https?:\/\//.test(href || "");
      const attrs = external ? ' target="_blank" rel="noreferrer"' : "";
      return `<a href="${escapeHtml(href || "#")}"${title ? ` title="${escapeHtml(title)}"` : ""}${attrs}>${text}</a>`;
    };

    return marked.parse(withAnchors, { gfm: true, renderer });
  }

  function addedLines(previous, current) {
    const before = previous ? previous.split("\n") : [];
    const after = current ? current.split("\n") : [];
    if (!previous) return new Set(after.map((_, index) => index + 1));

    const matrix = Array.from({ length: before.length + 1 }, () =>
      new Uint16Array(after.length + 1),
    );
    for (let i = 1; i <= before.length; i += 1) {
      for (let j = 1; j <= after.length; j += 1) {
        matrix[i][j] =
          before[i - 1] === after[j - 1]
            ? matrix[i - 1][j - 1] + 1
            : Math.max(matrix[i - 1][j], matrix[i][j - 1]);
      }
    }

    const matched = new Set();
    let i = before.length;
    let j = after.length;
    while (i > 0 && j > 0) {
      if (before[i - 1] === after[j - 1]) {
        matched.add(j);
        i -= 1;
        j -= 1;
      } else if (matrix[i - 1][j] >= matrix[i][j - 1]) {
        i -= 1;
      } else {
        j -= 1;
      }
    }

    return new Set(
      after.map((_, index) => index + 1).filter((line) => !matched.has(line)),
    );
  }

  function langForPath(path) {
    const ext = (path.split(".").pop() || "").toLowerCase();
    const map = {
      ts: "typescript",
      tsx: "typescript",
      js: "javascript",
      jsx: "javascript",
      mjs: "javascript",
      cjs: "javascript",
      py: "python",
      rs: "rust",
      go: "go",
      json: "json",
      sh: "bash",
      bash: "bash",
      zsh: "bash",
      md: "markdown",
      css: "css",
      html: "xml",
      yaml: "yaml",
      yml: "yaml",
    };
    return map[ext] || "plaintext";
  }

  function highlightedLine(line, language) {
    if (!line) return "&nbsp;";
    const lang = language && hljs.getLanguage(language) ? language : "plaintext";
    return hljs.highlight(line, { language: lang, ignoreIllegals: true }).value;
  }

  function shortName(path) {
    const parts = path.split("/");
    return parts[parts.length - 1] || path;
  }

  function treeRootLabel(files) {
    if (!files.length) return "src";
    const first = files[0];
    const slash = first.indexOf("/");
    return slash > 0 ? first.slice(0, slash) : ".";
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
  }

  function initTheme() {
    let saved = null;
    try {
      saved = localStorage.getItem(themeKey);
    } catch {
      saved = null;
    }
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme =
      saved === "light" || saved === "dark" ? saved : prefersDark ? "dark" : "light";
    applyTheme(theme);
  }

  function toggleTheme() {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
    try {
      localStorage.setItem(themeKey, next);
    } catch {
      /* ignore */
    }
  }

  const state = {
    lessonId: lessons[0].id,
    activeIndex: -1,
    openFiles: [],
    navigationLocked: false,
    mobilePanelOpen: false,
    fileChoice: null,
    suppressedAnimationPhases: new Set(),
    scrollPositions: new Map(),
    selectionCause: "checkpoint",
  };

  const app = document.getElementById("app");
  const refs = {};

  function currentLesson() {
    return lessons.find((item) => item.id === state.lessonId) || lessons[0];
  }

  function navigateLesson(id) {
    if (!lessons.some((item) => item.id === id)) return;
    state.lessonId = id;
    state.activeIndex = -1;
    state.openFiles = [];
    state.navigationLocked = false;
    state.mobilePanelOpen = false;
    state.fileChoice = null;
    state.suppressedAnimationPhases = new Set();
    state.scrollPositions = new Map();
    state.selectionCause = "checkpoint";
    window.history.pushState(null, "", `#${id}`);
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    render();
  }

  function mountShell() {
    app.innerHTML = `
      <header class="site-header">
        <button class="brand" type="button" data-action="home" aria-label="返回首页">
          <span class="brand-mark"></span>
          <strong class="brand-text"></strong>
        </button>
        <nav class="chapter-nav" aria-label="课程章节"></nav>
        <div class="header-actions">
          <button class="theme-toggle" type="button" data-action="theme" aria-label="切换浅色或深色模式" title="切换显示模式">◐</button>
        </div>
      </header>
      <div class="reading-progress" aria-hidden="true"><span data-ref="progress"></span></div>
      <main class="reader-shell" data-ref="shell"></main>
    `;

    refs.progress = app.querySelector("[data-ref=progress]");
    refs.shell = app.querySelector("[data-ref=shell]");
    app.querySelector(".brand-mark").textContent = site.brandMark || "◇";
    app.querySelector(".brand-text").textContent = site.brand || "Walkthrough";

    const nav = app.querySelector(".chapter-nav");
    if (lessons.length > 1) {
      nav.innerHTML = lessons
        .map(
          (lesson) =>
            `<button type="button" data-lesson="${escapeHtml(lesson.id)}">${escapeHtml(lesson.title)}</button>`,
        )
        .join("");
    } else {
      nav.innerHTML = "";
    }

    app.querySelector('[data-action="home"]').addEventListener("click", () => {
      navigateLesson(lessons[0].id);
    });
    app.querySelector('[data-action="theme"]').addEventListener("click", toggleTheme);
    nav.addEventListener("click", (event) => {
      const button = event.target.closest("[data-lesson]");
      if (!button) return;
      navigateLesson(button.dataset.lesson);
    });
  }

  function renderNavActive() {
    app.querySelectorAll(".chapter-nav button").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.lesson === state.lessonId);
    });
  }

  function render() {
    const lesson = currentLesson();
    renderNavActive();

    const articleHtml = renderMarkdown(lesson.markdown);
    refs.shell.innerHTML = `
      <section class="reader-grid">
        <article class="lesson-column" data-ref="article">
          <header class="lesson-header">
            <h1>${escapeHtml(lesson.title)}</h1>
            ${lesson.description ? `<p class="lesson-description">${escapeHtml(lesson.description)}</p>` : ""}
            ${lesson.readingTime ? `<div class="lesson-meta">${escapeHtml(lesson.readingTime)}</div>` : ""}
          </header>
          <div class="article-body">${articleHtml}</div>
          <footer class="lesson-footer">滚动阅读 · 右侧代码会随 checkpoint 渐显</footer>
        </article>
        <div class="panel-column ${state.mobilePanelOpen ? "is-mobile-open" : ""}" data-ref="panelColumn">
          <button class="drawer-close" type="button" data-action="close-panel" aria-label="关闭右侧面板">✕</button>
          <aside class="code-panel" data-ref="panel" aria-label="随阅读演进的代码仓库">
            <div class="panel-heading">
              <strong>${escapeHtml(repoLabel)}</strong>
              <button
                class="editor-lock ${state.navigationLocked ? "is-active" : ""}"
                type="button"
                data-action="lock"
                aria-pressed="${state.navigationLocked}"
                title="${state.navigationLocked ? "继续跟随阅读" : "停止跟随阅读"}"
              >${state.navigationLocked ? "🔒" : "🔓"}</button>
            </div>
            <div class="repo-workspace" data-ref="workspace"></div>
          </aside>
        </div>
      </section>
      ${state.mobilePanelOpen ? '<button class="drawer-backdrop" type="button" data-action="close-panel" aria-label="关闭右侧面板"></button>' : ""}
      <button class="mobile-panel-button" type="button" data-action="open-panel" aria-expanded="${state.mobilePanelOpen}">
        查看代码 <span data-ref="completion">0%</span>
      </button>
    `;

    refs.article = refs.shell.querySelector("[data-ref=article]");
    refs.panelColumn = refs.shell.querySelector("[data-ref=panelColumn]");
    refs.panel = refs.shell.querySelector("[data-ref=panel]");
    refs.workspace = refs.shell.querySelector("[data-ref=workspace]");
    refs.completion = refs.shell.querySelector("[data-ref=completion]");

    refs.shell.querySelector('[data-action="lock"]').addEventListener("click", () => {
      toggleNavigationLock();
    });
    refs.shell.querySelectorAll('[data-action="close-panel"]').forEach((el) => {
      el.addEventListener("click", () => {
        state.mobilePanelOpen = false;
        render();
      });
    });
    refs.shell.querySelector('[data-action="open-panel"]').addEventListener("click", () => {
      state.mobilePanelOpen = true;
      render();
    });

    bindScrollObserver();
    syncPanelFrame();
    renderCodePanel();
    updateActiveFromScroll();
  }

  function toggleNavigationLock() {
    const lesson = currentLesson();
    const checkpoint =
      state.activeIndex >= 0 ? lesson.checkpoints[state.activeIndex] : null;

    if (state.navigationLocked) {
      const checkpointFile = checkpoint?.file;
      if (checkpointFile) {
        if (!state.openFiles.includes(checkpointFile)) {
          state.openFiles = [...state.openFiles, checkpointFile];
        }
      }
      state.selectionCause = "checkpoint";
      state.fileChoice = null;
      state.navigationLocked = false;
    } else {
      const selected = getSelectedFile();
      state.selectionCause = "settled";
      state.fileChoice = {
        checkpointId: checkpoint?.id || "initial",
        file: selected || null,
      };
      state.navigationLocked = true;
    }
    renderCodePanel();
  }

  function getCheckpointContext() {
    const lesson = currentLesson();
    const checkpoint =
      state.activeIndex >= 0 ? lesson.checkpoints[state.activeIndex] : null;
    const previous =
      state.activeIndex > 0 ? lesson.checkpoints[state.activeIndex - 1] : null;
    const initialRepo = lesson.initialRepo || {};
    const repo = checkpoint?.repo || initialRepo;
    const previousRepo = previous?.repo || initialRepo;
    return { lesson, checkpoint, previous, initialRepo, repo, previousRepo };
  }

  function getSelectedFile() {
    const { checkpoint, repo } = getCheckpointContext();
    const phaseId = checkpoint?.id || "initial";
    const files = Object.keys(repo);
    if (
      state.fileChoice &&
      (state.navigationLocked || state.fileChoice.checkpointId === phaseId)
    ) {
      if (state.fileChoice.file && state.fileChoice.file in repo) {
        return state.fileChoice.file;
      }
      return "";
    }
    return checkpoint?.file && checkpoint.file in repo
      ? checkpoint.file
      : files[0] || "";
  }

  function changesForFile(file) {
    const { checkpoint, repo, previousRepo } = getCheckpointContext();
    if (!checkpoint || file !== checkpoint.file) return new Set();
    if (Array.isArray(checkpoint.focus) && checkpoint.focus.length === 2) {
      const [start, end] = checkpoint.focus;
      return new Set(
        Array.from({ length: end - start + 1 }, (_, index) => start + index),
      );
    }
    return addedLines(previousRepo[file] || "", repo[file] || "");
  }

  function renderCodePanel() {
    const { checkpoint, repo, previousRepo } = getCheckpointContext();
    const files = Object.keys(repo);
    const phaseId = checkpoint?.id || "initial";
    const newFiles = new Set(files.filter((file) => !(file in previousRepo)));
    const selectedFile = getSelectedFile();
    const availableOpenFiles = state.openFiles.filter((file) => file in repo);
    const visibleOpenFiles =
      selectedFile && !availableOpenFiles.includes(selectedFile)
        ? [...availableOpenFiles, selectedFile]
        : availableOpenFiles;
    const hasSelectedFile = selectedFile in repo;
    const rootLabel = treeRootLabel(files);

    const treeHtml = files.length
      ? files
          .map((file) => {
            const complete = false;
            return `<button type="button" class="${selectedFile === file ? "is-active" : ""}" data-file="${escapeHtml(file)}" title="${escapeHtml(file)}">
              <span>◇</span><span>${escapeHtml(shortName(file))}</span>
              ${complete ? '<span class="file-check" aria-label="已完成">✓</span>' : ""}
            </button>`;
          })
          .join("")
      : '<p class="empty-tree">空目录</p>';

    let stageHtml = "";
    if (!hasSelectedFile) {
      stageHtml = `
        <div class="empty-code">
          <strong>${files.length ? "没有打开的文件" : "仓库还是空的"}</strong>
          <p>${files.length ? "从左侧文件树打开一个文件。" : "读到第一个 checkpoint，代码才会出现。"}</p>
        </div>`;
    } else {
      const tabs = visibleOpenFiles
        .map(
          (file) => `
          <div class="code-tab ${selectedFile === file ? "is-active" : ""}">
            <button class="code-tab-select" type="button" data-file="${escapeHtml(file)}">
              <span>${escapeHtml(shortName(file))}</span>
            </button>
            <button class="code-tab-close" type="button" data-close="${escapeHtml(file)}" aria-label="关闭 ${escapeHtml(file)}">✕</button>
          </div>`,
        )
        .join("");

      const scrolls = visibleOpenFiles
        .map((file) => {
          const fileCode = repo[file] || "";
          const fileChanges = changesForFile(file);
          const changedOrder = new Map(
            Array.from(fileChanges)
              .sort((a, b) => a - b)
              .map((line, index) => [line, index]),
          );
          const shouldAnimate = Boolean(
            checkpoint &&
              file === checkpoint.file &&
              !state.suppressedAnimationPhases.has(phaseId),
          );
          const writeLead = newFiles.has(file) ? 820 : 120;
          const language = langForPath(file);
          const lines = fileCode.split("\n");
          const lineHtml = lines
            .map((line, index) => {
              const lineNumber = index + 1;
              const isChanged = fileChanges.has(lineNumber);
              const isEntering = isChanged && shouldAnimate;
              const writeIndex = changedOrder.get(lineNumber) || 0;
              const writeDelay = writeLead + Math.min(writeIndex * 28, 900);
              const writeDuration = Math.min(640, Math.max(260, line.length * 10));
              const style = isEntering
                ? ` style="--write-delay:${writeDelay}ms;--write-duration:${writeDuration}ms"`
                : "";
              return `<div class="code-line ${isChanged ? "is-new" : ""} ${isEntering ? "is-entering" : ""}" data-line="${lineNumber}"${style}>
                <span class="line-number">${lineNumber}</span>
                <code>${highlightedLine(line, language)}</code>
              </div>`;
            })
            .join("");

          return `<div class="code-scroll ${selectedFile === file ? "is-active" : ""}" data-editor-file="${escapeHtml(file)}" aria-hidden="${selectedFile !== file}">${lineHtml}</div>`;
        })
        .join("");

      stageHtml = `<div class="code-tabs" role="tablist">${tabs}</div>${scrolls}`;
    }

    refs.workspace.innerHTML = `
      <nav class="file-tree" aria-label="仓库文件">
        <div class="tree-root">📁 ${escapeHtml(rootLabel)}</div>
        ${treeHtml}
      </nav>
      <div class="code-stage">${stageHtml}</div>
    `;

    refs.workspace.querySelectorAll("[data-file]").forEach((button) => {
      button.addEventListener("click", () => selectFile(button.dataset.file));
    });
    refs.workspace.querySelectorAll("[data-close]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        closeFile(button.dataset.close);
      });
    });

    // restore scroll / focus
    requestAnimationFrame(() => {
      const container = refs.workspace.querySelector(
        `.code-scroll[data-editor-file="${CSS.escape(selectedFile)}"]`,
      );
      if (!container || !selectedFile) return;

      const changed = changesForFile(selectedFile);
      const focusLine = changed.size ? Math.min(...changed) : 1;
      const saved = state.scrollPositions.get(selectedFile);
      const followsCheckpoint =
        !state.navigationLocked &&
        state.selectionCause === "checkpoint" &&
        checkpoint &&
        selectedFile === checkpoint.file;

      if (followsCheckpoint && repo[selectedFile]) {
        const target = container.querySelector(`[data-line="${focusLine}"]`);
        if (target) {
          container.scrollTo({
            top: Math.max(0, target.offsetTop - container.clientHeight * 0.28),
            left: 0,
            behavior: "auto",
          });
        }
      } else if (saved) {
        container.scrollTo({ top: saved.top, left: saved.left, behavior: "auto" });
      }
      state.selectionCause = "settled";

      container.addEventListener(
        "scroll",
        () => {
          state.scrollPositions.set(selectedFile, {
            top: container.scrollTop,
            left: container.scrollLeft,
          });
        },
        { passive: true },
      );
    });

    const total = currentLesson().checkpoints.length || 1;
    const completion =
      state.activeIndex < 0
        ? 0
        : Math.round(((state.activeIndex + 1) / total) * 100);
    if (refs.completion) refs.completion.textContent = `${completion}%`;

    // lock button label refresh without full re-render of article
    const lock = refs.panel.querySelector('[data-action="lock"]');
    if (lock) {
      lock.classList.toggle("is-active", state.navigationLocked);
      lock.setAttribute("aria-pressed", String(state.navigationLocked));
      lock.textContent = state.navigationLocked ? "🔒" : "🔓";
      lock.title = state.navigationLocked ? "继续跟随阅读" : "停止跟随阅读";
    }
  }

  function selectFile(file) {
    const { checkpoint, repo } = getCheckpointContext();
    if (!(file in repo)) return;
    const phaseId = checkpoint?.id || "initial";
    const selected = getSelectedFile();
    const container = refs.workspace.querySelector(
      `.code-scroll[data-editor-file="${CSS.escape(selected)}"]`,
    );
    if (container && selected) {
      state.scrollPositions.set(selected, {
        top: container.scrollTop,
        left: container.scrollLeft,
      });
    }
    state.selectionCause = "manual";
    state.suppressedAnimationPhases.add(phaseId);
    if (!state.openFiles.includes(file)) {
      state.openFiles = [...state.openFiles, file];
    }
    state.fileChoice = { checkpointId: phaseId, file };
    renderCodePanel();
  }

  function closeFile(file) {
    const { checkpoint } = getCheckpointContext();
    const phaseId = checkpoint?.id || "initial";
    const selected = getSelectedFile();
    const visible = state.openFiles.filter((item) => {
      const { repo } = getCheckpointContext();
      return item in repo;
    });
    // recompute visible with selected
    const available = state.openFiles.filter((item) => item in getCheckpointContext().repo);
    const withSelected =
      selected && !available.includes(selected) ? [...available, selected] : available;
    const index = withSelected.indexOf(file);
    const remaining = withSelected.filter((item) => item !== file);
    state.openFiles = remaining;
    if (file !== selected) {
      renderCodePanel();
      return;
    }
    state.selectionCause = "manual";
    state.suppressedAnimationPhases.add(phaseId);
    state.fileChoice = {
      checkpointId: phaseId,
      file: remaining[Math.min(index, remaining.length - 1)] ?? null,
    };
    renderCodePanel();
  }

  let scrollFrame = 0;
  function updateActiveFromScroll() {
    const lesson = currentLesson();
    const article = refs.article;
    if (!article) return;
    const anchors = Array.from(
      article.querySelectorAll("[data-checkpoint]"),
    );
    const readingLine = window.innerHeight * 0.42;
    let next = -1;
    anchors.forEach((anchor) => {
      if (anchor.getBoundingClientRect().top <= readingLine) {
        const index = lesson.checkpoints.findIndex(
          (item) => item.id === anchor.dataset.checkpoint,
        );
        if (index >= 0) next = index;
      }
    });

    if (next !== state.activeIndex) {
      state.activeIndex = next;
      state.selectionCause = state.navigationLocked ? "settled" : "checkpoint";
      const nextFile = next >= 0 ? lesson.checkpoints[next]?.file : null;
      if (nextFile && !state.navigationLocked && !state.openFiles.includes(nextFile)) {
        state.openFiles = [...state.openFiles, nextFile];
      }
      if (!state.fileChoice || !state.navigationLocked) {
        // stay on auto nav unless locked
        if (!state.navigationLocked) state.fileChoice = null;
      }
      renderCodePanel();
    }

    const rect = article.getBoundingClientRect();
    const travel = Math.max(1, rect.height - window.innerHeight * 0.55);
    const progress = Math.min(1, Math.max(0, (-rect.top + 72) / travel));
    if (refs.progress) refs.progress.style.width = `${progress * 100}%`;
  }

  function scheduleScrollUpdate() {
    if (scrollFrame) return;
    scrollFrame = requestAnimationFrame(() => {
      scrollFrame = 0;
      updateActiveFromScroll();
    });
  }

  function bindScrollObserver() {
    window.removeEventListener("scroll", scheduleScrollUpdate);
    window.removeEventListener("resize", onResize);
    window.addEventListener("scroll", scheduleScrollUpdate, { passive: true });
    window.addEventListener("resize", onResize);
  }

  function syncPanelFrame() {
    const column = refs.panelColumn;
    const panel = refs.panel;
    if (!column || !panel) return;
    const desktop = window.matchMedia("(min-width: 1181px)");
    if (!desktop.matches || state.mobilePanelOpen) {
      panel.removeAttribute("data-viewport-pinned");
      panel.style.removeProperty("--panel-fixed-left");
      panel.style.removeProperty("--panel-fixed-width");
      return;
    }
    const rect = column.getBoundingClientRect();
    panel.style.setProperty("--panel-fixed-left", `${rect.left}px`);
    panel.style.setProperty("--panel-fixed-width", `${rect.width}px`);
    panel.setAttribute("data-viewport-pinned", "true");
  }

  function onResize() {
    syncPanelFrame();
    scheduleScrollUpdate();
  }

  function bootFromHash() {
    const hash = window.location.hash.slice(1);
    if (hash && lessons.some((item) => item.id === hash)) {
      state.lessonId = hash;
    }
  }

  initTheme();
  mountShell();
  bootFromHash();
  render();
  window.addEventListener("hashchange", () => {
    bootFromHash();
    render();
  });
})();
