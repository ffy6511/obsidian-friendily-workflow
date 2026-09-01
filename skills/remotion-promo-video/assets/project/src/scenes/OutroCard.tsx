import React from "react";
import { Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { COLORS } from "../theme/colors";
import { FONTS } from "../theme/typography";
import { BRAND } from "../timeline";

/** Outro: an optional image with the repo line — GitHub mark on the left —
 *  beneath it, all one vertically-centred group fading in on the same beat. */

const FADE_FROM = 20;
const FADE_TO = 75;

const GitHubMark: React.FC<{ size: number; color: string }> = ({ size, color }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 16 16"
    fill={color}
    aria-hidden
    style={{ display: "block", flexShrink: 0 }}
  >
    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
  </svg>
);

export const OutroCard: React.FC = () => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const fade = interpolate(frame, [FADE_FROM, FADE_TO], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: COLORS.bg,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {BRAND.outroImage ? (
        <Img
          src={staticFile(BRAND.outroImage)}
          style={{
            width: 1360,
            display: "block",
            borderRadius: 14,
            boxShadow: "0 24px 48px -16px rgba(15, 23, 42, 0.28)",
            opacity: fade,
            transform: `translateY(${interpolate(fade, [0, 1], [24, 0])}px)`,
          }}
        />
      ) : (
        <div
          style={{
            fontFamily: FONTS.title,
            fontSize: 120,
            fontWeight: 700,
            letterSpacing: 8,
            color: COLORS.textPrimary,
            opacity: fade,
          }}
        >
          {BRAND.name}
        </div>
      )}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
          marginTop: 52,
          opacity: fade,
          transform: `translateY(${interpolate(fade, [0, 1], [18, 0])}px)`,
        }}
      >
        <GitHubMark size={30} color={COLORS.textPrimary} />
        <span
          style={{
            fontFamily: FONTS.mono,
            fontSize: 24,
            color: COLORS.textSecondary,
            letterSpacing: 0.4,
          }}
        >
          {BRAND.repoLine}
        </span>
      </div>
    </div>
  );
};
