import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
Config.setCodec("h264");
Config.setPixelFormat("yuv420p");
Config.setColorSpace("bt709");
Config.setCrf(20);
Config.setGopSize(30);
Config.setX264Preset("medium");
Config.overrideFfmpegCommand(({ type, args }) => {
  if (type !== "stitcher") {
    return args;
  }
  const output = args[args.length - 1];
  const rest = args.slice(0, -1);
  const extra: string[] = [];
  if (!rest.includes("-tune")) {
    extra.push("-tune", "animation");
  }
  if (!rest.includes("-movflags")) {
    extra.push("-movflags", "+faststart");
  }
  return [...rest, ...extra, output];
});
