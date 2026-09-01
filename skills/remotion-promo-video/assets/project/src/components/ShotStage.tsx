import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Img, staticFile } from "remotion";
import { VideoChrome } from "./VideoChrome";
import { COLORS } from "../theme/colors";
import { CHROME_H, VIDEO_NATIVE, type Shot } from "../timeline";

/** Safe area, scaled to 1920×1080. */
const PAD_X = 80;
const PAD_TOP = 100;
const PAD_BOTTOM = 108;
const CONTENT_W = 1920 - PAD_X * 2;
const CONTENT_H = 1080 - PAD_TOP - PAD_BOTTOM;

/** The capture fills the stage: as wide as the safe area allows once the
 *  chrome bar and the vertical padding are paid for. */
const VIDEO_W = Math.min(
  CONTENT_W,
  ((CONTENT_H - CHROME_H) * VIDEO_NATIVE.width) / VIDEO_NATIVE.height
);

/** Duo windows: two halves side by side, the emphasis crossfading between
 *  them at `swapAtSeconds` — the active window full and still, the other
 *  dimmed and pulled back a touch. */
const DUO_W = (CONTENT_W - 28) / 2;
const DIM_OPACITY = 0.55;
const CROSSFADE = 0.7;

export const ShotStage: React.FC<{ shot: Shot }> = ({ shot }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = interpolate(frame, [0, 0.25 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  if (shot.duo) {
    const now = frame / fps;
    const swap = shot.duo.swapAtSeconds;
    const t = interpolate(now, [swap - CROSSFADE, swap + CROSSFADE], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.4, 0, 0.2, 1),
    });
    const sideStyle = (active: boolean): React.CSSProperties => ({
      opacity: active ? 1 - (1 - DIM_OPACITY) * t : DIM_OPACITY + (1 - DIM_OPACITY) * t,
      transform: `scale(${active ? 1 - 0.018 * t : 0.982 + 0.018 * t})`,
    });
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: COLORS.bg,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 28,
          opacity: appear,
        }}
      >
        <div style={sideStyle(true)}>
          <VideoChrome
            shot={{ ...shot, video: shot.duo.left, address: shot.duo.leftAddress }}
            width={DUO_W}
          />
        </div>
        <div style={sideStyle(false)}>
          <VideoChrome
            shot={{ ...shot, video: shot.duo.right, address: shot.duo.rightAddress }}
            width={DUO_W}
          />
        </div>
      </div>
    );
  }

  if (shot.layout === "video") {
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: COLORS.bg,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: appear,
        }}
      >
        <VideoChrome shot={shot} width={VIDEO_W} />
      </div>
    );
  }

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: COLORS.bg,
      }}
    >
      {shot.diagram ? (
        <div
          style={{
            position: "absolute",
            top: PAD_TOP,
            bottom: PAD_BOTTOM,
            left: PAD_X,
            right: PAD_X,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: appear,
          }}
        >
          <Img
            src={staticFile(shot.diagram)}
            style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
          />
        </div>
      ) : null}
    </div>
  );
};
