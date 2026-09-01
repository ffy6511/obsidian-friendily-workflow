import React from "react";
import { Composition } from "remotion";
import { MainVideo } from "./MainVideo";
import { FPS, HEIGHT, TOTAL_FRAMES, WIDTH } from "./timeline";

export const Root: React.FC = () => {
  return (
    <Composition
      id="Promo"
      component={MainVideo}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
