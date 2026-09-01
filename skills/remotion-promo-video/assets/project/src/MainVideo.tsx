import React from "react";
import { Audio as BgmAudio, Easing, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { Audio } from "@remotion/media";
import { TopBar } from "./components/TopBar";
import { ShotStage } from "./components/ShotStage";
import { Subtitles } from "./components/Subtitles";
import { IntroCard } from "./scenes/IntroCard";
import { OutroCard } from "./scenes/OutroCard";
import { COLORS } from "./theme/colors";
import { HEIGHT, SHOT_TIMELINE, TOTAL_FRAMES, WIDTH } from "./timeline";

const BGM_PATH = "bgm/track.mp3"; // drop your track in public/bgm/ (references/bgm.md)

const VisualFade: React.FC<{ durationInFrames: number; children: React.ReactNode }> = ({
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const fade = 16;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity: interpolate(frame, [0, fade, durationInFrames - fade, durationInFrames], [0, 1, 1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: [Easing.bezier(0.16, 1, 0.3, 1), Easing.linear, Easing.bezier(0.16, 1, 0.3, 1)],
        }),
      }}
    >
      {children}
    </div>
  );
};

export const MainVideo: React.FC = () => {
  const sections = SHOT_TIMELINE.filter(
    (shot) => shot.layout === "diagram" || shot.layout === "video" || shot.layout === "duo"
  ).map((shot) => shot.title);

  return (
    <div
      style={{
        width: WIDTH,
        height: HEIGHT,
        backgroundColor: COLORS.bg,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {SHOT_TIMELINE.map((shot) => (
        <Sequence
          key={shot.id}
          from={shot.from}
          durationInFrames={shot.durationInFrames}
          name={shot.id}
        >
          <VisualFade durationInFrames={shot.durationInFrames}>
            {shot.layout === "intro" ? (
              <IntroCard />
            ) : shot.layout === "outro" ? (
              <OutroCard />
            ) : (
              <>
                <TopBar sections={sections} active={shot.title} />
                <ShotStage shot={shot} />
              </>
            )}
            <Subtitles
              lines={shot.captions}
              durationInFrames={shot.durationInFrames}
              id={shot.tts.split("/").pop()?.replace(/\.wav$/, "") ?? shot.id}
            />
          </VisualFade>
          {/* Per-scene VO: lives INSIDE the Sequence so Subtitles and the
              audio share the same scene-relative time base. */}
          <Audio src={staticFile(shot.tts)} />
        </Sequence>
      ))}

      {/* BGM bed: loops under the VO at low level, 1.5s fade-in, 2.5s fade-out. */}
      <BgmAudio
        loop
        src={staticFile(BGM_PATH)}
        volume={(f) => {
          const fadeIn = interpolate(f, [0, 90], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const fadeOut = interpolate(f, [TOTAL_FRAMES - 180, TOTAL_FRAMES - 30], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return 0.1 * Math.min(fadeIn, fadeOut);
        }}
      />
    </div>
  );
};
