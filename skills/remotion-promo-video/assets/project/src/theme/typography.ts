/**
 * Default: system font stacks — fully offline, zero setup.
 *
 * For a branded look, self-host woff2 files in public/fonts/ and load them
 * with @remotion/fonts (already a dependency). Do NOT use
 * @remotion/google-fonts: Remotion launches Chrome with --no-proxy-server,
 * so fonts.gstatic.com is unreachable at render time on proxied networks.
 *
 * import { loadFont } from "@remotion/fonts";
 * import { staticFile } from "remotion";
 * loadFont({
 *   family: "IBM Plex Sans",
 *   url: staticFile("fonts/IBMPlexSans-500.woff2"),
 *   style: "normal", weight: "500", format: "woff2",
 * });
 */

export const FONTS = {
  title: '-apple-system, "Helvetica Neue", "PingFang SC", sans-serif',
  body: '-apple-system, "Helvetica Neue", "PingFang SC", sans-serif',
  mono: 'ui-monospace, "SF Mono", Menlo, monospace',
};
