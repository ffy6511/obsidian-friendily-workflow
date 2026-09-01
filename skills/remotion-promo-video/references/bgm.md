# BGM(已验证接法 + 站点)

## 站点

- 首选:[Pixabay Music](https://pixabay.com/music/) — 免费可商用、无需署名,按 mood/genre 筛,Lofi/Ambient 类很适合垫底。
- 备选:YouTube Audio Library、Free Music Archive、incompetech(需署名)。
- 下载的 mp3 放 `public/bgm/`,**在分镜文档里记录曲目名与来源链接**(许可追溯)。

参考工程实际用的曲目:`Lofi Midnight Club`(Pixabay)。

## 接法(骨架 MainVideo.tsx 已带,真实实现)

BGM 是**整片一层**,放在所有幕的 Sequence 之外(与每幕的 VO `<Audio>` 互不干扰):

```tsx
import { Audio as BgmAudio, interpolate, staticFile } from "remotion";

{/* BGM bed: loops under the VO at low level, 1.5s fade-in, 2.5s fade-out. */}
<BgmAudio
  loop
  src={staticFile("bgm/<track>.mp3")}
  volume={(f) => {
    const fadeIn = interpolate(f, [0, 90], [0, 1], {            // 1.5s 淡入
      extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const fadeOut = interpolate(f, [TOTAL_FRAMES - 180, TOTAL_FRAMES - 30], [1, 0], { // 尾部 2.5s 淡出
      extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return 0.1 * Math.min(fadeIn, fadeOut);                     // 常驻 0.1 垫底
  }}
/>
```

要点(全部实测):

- 用 **remotion 包的 `Audio`**(不是 `@remotion/media` 的那个;工程里两者并存:`Audio` 给每幕 VO,`BgmAudio` 是 remotion 的别名给 BGM)。
- `volume` 是**帧回调**,0.1 的常驻系数让 VO 永远压得住;淡入淡出用帧数写死相对 `TOTAL_FRAMES`,片子改长自动跟随。
- `loop` 属性必须有——BGM 曲长 < 片长时循环垫满。
- 换曲目只改 `staticFile` 路径一行;音量手感 0.08–0.12 之间调。

## 何时进流程

初版渲染(无 BGM)验收通过后再加 BGM,避免调试字幕/时长时多一层变量。
