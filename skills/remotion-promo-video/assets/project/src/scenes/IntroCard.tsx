import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { COLORS } from "../theme/colors";
import { FONTS } from "../theme/typography";
import { BRAND } from "../timeline";

/** Intro card: the brand wordmark fades in with a soft rise. No other
 *  on-screen text — the VO carries the slogan. The reference project
 *  replaces this with a particle logo (a dotted thread winding into the
 *  mark, driven by useCurrentFrame for render determinism). */
export const IntroCard: React.FC = () => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const enter = interpolate(frame, [10, 70], [0, 1], {
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
      <div
        style={{
          fontFamily: FONTS.title,
          fontSize: 140,
          fontWeight: 700,
          letterSpacing: 8,
          color: COLORS.textPrimary,
          opacity: enter,
          transform: `translateY(${interpolate(enter, [0, 1], [30, 0])}px)`,
        }}
      >
        {BRAND.name}
      </div>
    </div>
  );
};
