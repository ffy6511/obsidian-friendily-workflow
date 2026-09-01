import React from "react";
import { staticFile } from "remotion";
import { Video } from "@remotion/media";
import { COLORS, SHADOWS } from "../theme/colors";
import { FONTS } from "../theme/typography";
import { CHROME_H, VIDEO_NATIVE, type Shot } from "../timeline";

export const videoDisplayHeight = (width: number) =>
  width * (VIDEO_NATIVE.height / VIDEO_NATIVE.width);

const TrafficLights: React.FC = () => (
  <div style={{ display: "flex", alignItems: "center", gap: 7, width: 52, flexShrink: 0 }}>
    <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ff5f56" }} />
    <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ffbd2e" }} />
    <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#27c93f" }} />
  </div>
);

const Pending: React.FC<{ shot: Shot }> = ({ shot }) => (
  <div
    style={{
      width: "100%",
      height: "100%",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 10,
      background: COLORS.bgSubtle,
      fontFamily: FONTS.mono,
      fontSize: 16,
      color: COLORS.textMuted,
    }}
  >
    {shot.video ?? "footage"}
  </div>
);

/** Browser-chrome framing for one footage clip. The <Video> runs muted —
 *  the VO is a separate per-scene <Audio>. Media that ends before the scene
 *  should be tail-frozen (ffmpeg tpad) to the scene length. */
export const VideoChrome: React.FC<{ shot: Shot; width: number }> = ({ shot, width }) => {
  const videoH = videoDisplayHeight(width);

  return (
    <div
      style={{
        width,
        height: videoH + CHROME_H,
        borderRadius: 10,
        overflow: "hidden",
        border: `1px solid ${COLORS.cardBorderStrong}`,
        boxShadow: SHADOWS.window,
        background: "#ffffff",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          height: CHROME_H,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          padding: "0 12px",
          gap: 10,
          background: "#ffffff",
          borderBottom: `1px solid ${COLORS.cardBorder}`,
        }}
      >
        <TrafficLights />
        <div
          style={{
            flex: 1,
            height: 22,
            borderRadius: 6,
            background: COLORS.bgSubtle,
            border: `1px solid ${COLORS.cardBorder}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: FONTS.mono,
            fontSize: 12,
            color: COLORS.textSecondary,
          }}
        >
          {shot.address}
        </div>
      </div>
      <div style={{ width, height: videoH, position: "relative", overflow: "hidden" }}>
        {shot.video ? (
          <Video
            src={staticFile(shot.video)}
            muted
            objectFit="cover"
            style={{ width: "100%", height: "100%" }}
          />
        ) : (
          <Pending shot={shot} />
        )}
      </div>
    </div>
  );
};
