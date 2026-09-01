import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import captionsJson from "../captions.json";
import { FONTS } from "../theme/typography";

/**
 * Captions are the EN VO text, sentence-per-line (timeline.ts `captions`).
 * Timing comes from `src/captions.json` — mlx_whisper word-level alignment
 * of the actual audio (regenerate with `tts/tts-align.py`).
 *
 * Exactly ONE caption line is rendered per frame: the last line whose
 * aligned span started at or before `now` (VO pauses hold the previous
 * line). Word highlight uses the word's real timestamps. If alignment data
 * is missing or matches poorly we fall back to word-count-weighted slots.
 *
 * PITFILT: unmatched caption words MUST be time-interpolated between their
 * matched neighbours. A broken interpolation pass once collapsed them to
 * [0,0], which made that line show for the whole scene with no highlight.
 */

type AlignedWord = { w: string; s: number; e: number };
type Align = { duration: number; words: AlignedWord[] };
type Word = { t: string; s: number; e: number };
type LineSpan = { start: number; end: number; words: Word[] };

const CAPTIONS = captionsJson as unknown as Record<string, Align | undefined>;

// Look and feel (tune per project).
const PILL_BG = "#3D3D42";
const TEXT_COLOR = "#f8fafc";
const CHIP_COLOR = "#6EA8FF";
const CHIP_TEXT = "#ffffff";

const norm = (w: string) => w.toLowerCase().replace(/[^a-z0-9]+/g, "");

/** Token equality for the alignment pass. Beyond exact matches, a long token
 *  may absorb a fragment of itself the transcriber split off ("first-class"
 *  vs "first" + "class"). */
const matches = (a: string, b: string) =>
  a === b || (a.length >= 4 && b.length >= 4 && (a.includes(b) || b.includes(a)));

/** Align the whisper word stream to the caption words with an LCS pass:
 *  insertions (the voice splitting a word) and renames (it pronouncing a
 *  name differently) are skipped, and every later word snaps back to its
 *  true position. Unmatched caption words carry NaN times and are
 *  interpolated below. */
function spanLines(lines: string[], align: Align): { spans: LineSpan[]; matched: number; total: number } {
  const lineTokens = lines.map((line) => line.split(/\s+/).filter(Boolean));
  const capWords: { t: string; li: number; n: string }[] = [];
  lineTokens.forEach((toks, li) => toks.forEach((t) => capWords.push({ t, li, n: norm(t) })));
  const N = align.words.map((w) => ({ ...w, n: norm(w.w) }));

  const dp: number[][] = Array.from({ length: N.length + 1 }, () =>
    new Array(capWords.length + 1).fill(0)
  );
  for (let i = N.length - 1; i >= 0; i--) {
    for (let jj = capWords.length - 1; jj >= 0; jj--) {
      dp[i][jj] = matches(N[i].n, capWords[jj].n)
        ? dp[i + 1][jj + 1] + 1
        : Math.max(dp[i + 1][jj], dp[i][jj + 1]);
    }
  }

  const raw: Word[][] = lines.map(() => []);
  let i = 0;
  let jj = 0;
  let matched = 0;
  while (i < N.length && jj < capWords.length) {
    if (matches(N[i].n, capWords[jj].n)) {
      raw[capWords[jj].li].push({ t: capWords[jj].t, s: N[i].s, e: N[i].e });
      matched += 1;
      i += 1;
      jj += 1;
    } else if (dp[i + 1][jj] >= dp[i][jj + 1]) {
      i += 1;
    } else {
      raw[capWords[jj].li].push({ t: capWords[jj].t, s: NaN, e: NaN });
      jj += 1;
    }
  }
  while (jj < capWords.length) {
    raw[capWords[jj].li].push({ t: capWords[jj].t, s: NaN, e: NaN });
    jj += 1;
  }

  // Interpolate unmatched words between their matched neighbours: each run
  // of NaN words extends from the previous word's end to the next real
  // word's start. The scan MUST skip whole NaN runs — comparing the
  // placeholder against null here once broke this and froze timings at 0.
  const spans: LineSpan[] = [];
  const flat = raw.flat();
  let prevEnd = 0;
  for (let k = 0; k < flat.length; k++) {
    const word = flat[k];
    if (word && !Number.isNaN(word.s)) {
      prevEnd = word.e;
      continue;
    }
    let e = k;
    while (e < flat.length && flat[e] && Number.isNaN(flat[e]!.s)) e++;
    const nextWord = e < flat.length ? flat[e] : undefined;
    const nextS = nextWord && !Number.isNaN(nextWord.s) ? nextWord.s : align.duration;
    const count = e - k;
    const gap = Math.max(0.08, nextS - prevEnd);
    for (let m = k; m < e; m++) {
      flat[m] = {
        t: flat[m]!.t,
        s: prevEnd + (gap * (m - k)) / count,
        e: prevEnd + (gap * (m - k + 1)) / count,
      };
    }
    prevEnd = nextS;
  }

  let p = 0;
  lineTokens.forEach((toks) => {
    const words = flat.slice(p, p + toks.length).map((w, idx) => ({
      t: toks[idx],
      s: w?.s ?? 0,
      e: w?.e ?? 0,
    }));
    p += toks.length;
    spans.push({
      start: words[0]?.s ?? 0,
      end: words[words.length - 1]?.e ?? 0,
      words,
    });
  });
  return { spans, matched, total: capWords.length };
}

/** Fallback: slots weighted by word count, word timings linear within a line. */
function weightedSpans(lines: string[], sceneSeconds: number): LineSpan[] {
  const weights = lines.map((line) => Math.max(line.split(/\s+/).filter(Boolean).length, 1));
  const weightSum = weights.reduce((sum, w) => sum + w, 0);
  let t = 0;
  return lines.map((line, i) => {
    const dur = (weights[i] / weightSum) * sceneSeconds;
    const start = t;
    const words = line
      .split(/\s+/)
      .filter(Boolean)
      .map((w, idx, arr) => ({
        t: w,
        s: start + (dur * idx) / arr.length,
        e: start + (dur * (idx + 1)) / arr.length,
      }));
    t += dur;
    return { start, end: start + dur, words };
  });
}

export const Subtitles: React.FC<{ lines: string[]; durationInFrames: number; id: string }> = ({
  lines,
  durationInFrames,
  id,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (lines.length === 0) {
    return null;
  }
  const now = frame / fps;

  let spans: LineSpan[] | null = null;
  const align = CAPTIONS[id];
  if (align && align.words.length > 0) {
    const result = spanLines(lines, align);
    if (result.total > 0 && result.matched / result.total >= 0.8) {
      spans = result.spans;
    }
  }
  if (!spans) {
    spans = weightedSpans(lines, durationInFrames / fps);
  }

  // The single active line: the last span that started at or before `now`.
  // Inside a VO pause the previous line holds; before the first, the first.
  let index = 0;
  for (let i = 0; i < spans.length; i++) {
    if (now >= spans[i].start) {
      index = i;
    }
  }
  const span = spans[index];
  const fadeIn = interpolate((now - span.start) * fps, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const activeIndex = span.words.findIndex((w) => now >= w.s && now < w.e);

  const typography: React.CSSProperties = {
    fontFamily: FONTS.body,
    fontSize: 32,
    fontWeight: 600,
    lineHeight: 1.5,
    textAlign: "center",
  };

  // Every word — chip or not — gets the SAME inline-block box (padding,
  // margin, weight) in both layers, so the highlight can never change word
  // spacing or line wrapping. The hidden layer owns the flow; the ink layer
  // paints the same boxes on top, switching the background of the active
  // word only.
  const wordStyle: React.CSSProperties = {
    display: "inline-block",
    borderRadius: 6,
    padding: "2px 10px",
    margin: "0 1px",
  };

  const renderWords = (mode: "layout" | "ink") =>
    span.words.map((word, i) => {
      const text = i === 0 ? word.t : ` ${word.t}`;
      if (mode === "layout") {
        return (
          <span key={i} style={wordStyle}>
            {text}
          </span>
        );
      }
      if (i === activeIndex) {
        return (
          <span key={i} style={{ ...wordStyle, position: "relative" }}>
            <span
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: 6,
                background: CHIP_COLOR,
              }}
            />
            <span style={{ position: "relative", color: CHIP_TEXT }}>{text}</span>
          </span>
        );
      }
      return (
        <span key={i} style={{ ...wordStyle, color: TEXT_COLOR }}>
          {text}
        </span>
      );
    });

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 28,
        zIndex: 80,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          position: "relative",
          maxWidth: 1200,
          padding: "10px 12px",
          borderRadius: 12,
          background: PILL_BG,
          boxShadow: "0 14px 34px -12px rgba(0, 0, 0, 0.5)",
          color: TEXT_COLOR,
          opacity: fadeIn,
          ...typography,
        }}
      >
        <div style={{ visibility: "hidden" }}>{renderWords("layout")}</div>
        <div style={{ position: "absolute", inset: 0, padding: "10px 12px", ...typography }}>
          {renderWords("ink")}
        </div>
      </div>
    </div>
  );
};
