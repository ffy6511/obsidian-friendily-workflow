export const FPS = 60;
export const WIDTH = 1920;
export const HEIGHT = 1080;

/** Native size of the demo captures; the video stage sizes by height. */
export const VIDEO_NATIVE = { width: 1652, height: 1080 };
export const CHROME_H = 40;

/** Brand strings used by TopBar / IntroCard / OutroCard. */
export const BRAND = {
  name: "BRAND",
  repoLine: "github.com/your-org/your-repo",
  outroImage: "media/outro.png", // set to "" to render text-only outro
};

/**
 * One scene of the cut. `durationInSeconds` is calibrated to the exported EN
 * TTS: scene = max(VO + 0.5s breath, footage floor). Every scene carries its
 * VO clip; `captions` are the EN VO text, one sentence per line — keep them
 * in sync with tts/tts-generate.py SEGMENTS, then re-run tts-align.py.
 *
 * Array order = playback order. Ids are filenames only: when scenes are
 * reordered keep the ids and fix this comment (id != position).
 */
export type ShotLayout = "intro" | "diagram" | "video" | "duo" | "outro";

export type Shot = {
  id: string;
  title: string;
  tts: string;
  video: string | null;
  address: string;
  captions: string[];
  durationInSeconds: number;
  layout: ShotLayout;
  diagram: string | null;
  /** Duo shots: two footage halves play side by side in sync; the visual
   *  emphasis crosses from the left window to the right at `swapAtSeconds`
   *  (pick the moment from captions.json where the narration turns). */
  duo?: {
    left: string;
    right: string;
    leftAddress: string;
    rightAddress: string;
    swapAtSeconds: number;
  };
};

export const SHOTS: Shot[] = [
  {
    id: "p1_intro",
    title: "Intro",
    tts: "tts/en/01_intro.wav",
    video: null,
    address: "",
    layout: "intro",
    diagram: null,
    durationInSeconds: 4.5,
    captions: ["One-line brand slogan goes here."],
  },
  {
    id: "p2_demo",
    title: "Demo",
    tts: "tts/en/02_demo.wav",
    video: "cuts/02-demo.mp4",
    address: "app.example.com",
    layout: "video",
    diagram: null,
    durationInSeconds: 20,
    captions: [
      "What this scene covers,",
      "one sentence per line.",
    ],
  },
  {
    id: "p3_compare",
    title: "Compare",
    tts: "tts/en/03_compare.wav",
    video: null,
    address: "app.example.com",
    layout: "duo",
    diagram: null,
    duo: {
      left: "cuts/03a-left.mp4",
      right: "cuts/03b-right.mp4",
      leftAddress: "left.example.com",
      rightAddress: "right.example.com",
      swapAtSeconds: 6,
    },
    durationInSeconds: 16,
    captions: ["First half narrates the left window.", "Then the right one takes over."],
  },
  {
    id: "p4_arch",
    title: "Architecture",
    tts: "tts/en/04_arch.wav",
    video: null,
    address: "",
    layout: "diagram",
    diagram: "media/architecture.png",
    durationInSeconds: 10,
    captions: ["Full-width diagram scenes follow the VO."],
  },
  {
    id: "p5_outro",
    title: "Outro",
    tts: "tts/en/05_outro.wav",
    video: null,
    address: "",
    layout: "outro",
    diagram: null,
    durationInSeconds: 6,
    captions: ["This is BRAND.", "Star the repo to see more!"],
  },
];

export const framesOf = (shot: Shot) => Math.round(shot.durationInSeconds * FPS);

export const SHOT_TIMELINE = SHOTS.reduce<
  Array<Shot & { from: number; durationInFrames: number }>
>((acc, shot) => {
  const from =
    acc.length === 0 ? 0 : acc[acc.length - 1].from + acc[acc.length - 1].durationInFrames;
  acc.push({ ...shot, from, durationInFrames: framesOf(shot) });
  return acc;
}, []);

export const TOTAL_FRAMES = SHOT_TIMELINE.reduce((sum, shot) => sum + shot.durationInFrames, 0);
