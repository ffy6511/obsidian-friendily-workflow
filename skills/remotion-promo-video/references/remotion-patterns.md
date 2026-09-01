# Remotion 模式(骨架已实现)

## SHOTS:单一事实源

`src/timeline.ts` 的 `SHOTS` 数组描述整支片子,所有组件从它派生:

```ts
type Shot = {
  id: string; title: string;           // Sequence 名 / 章节条名
  tts: string;                          // "tts/en/01_xxx.wav"(该幕口播)
  video: string | null;                 // "cuts/xx.mp4" 或 null
  address: string;                      // VideoChrome 地址栏文案
  captions: string[];                   // EN VO 文本,一句话一行
  durationInSeconds: number;            // max(VO + 0.5, 素材下限)
  layout: "intro" | "diagram" | "video" | "duo" | "outro";
  diagram: string | null;               // public/ 下整宽图
  duo?: { left: string; right: string; leftAddress: string; rightAddress: string; swapAtSeconds: number };
};
```

`SHOT_TIMELINE`(累加 from)与 `TOTAL_FRAMES` 由 reduce 派生,Composition 时长用后者——**不要手写总帧数**。

## 五种布局(MainVideo 按 layout 分发)

- **intro**:品牌开场卡。骨架给的是标题淡入 + 上移;参考工程换成了粒子 logo(点线绕结→凝聚成 mark,用 `useCurrentFrame` 替代 `performance.now()` 保证确定性)——需要时从参考工程移植 `ThinkingLogo`。
- **diagram**:整宽图(架构图/流程图),`ShotStage` 里 `<Img>` 居中,首 0.25s 淡入。
- **video**:素材居中全宽,窗口化 `VideoChrome`(红绿灯 + 地址栏),宽度按高度约束取最大:`min(CONTENT_W, (CONTENT_H - CHROME_H) * VIDEO_NATIVE.w / VIDEO_NATIVE.h)`。
- **duo**:双窗口左右对称同步播放,重点随旁白交替——`swapAtSeconds` 从 align 数据里查转折句的实际时间点,非焦点窗压暗到 0.55 并微缩(0.982),0.7s 交叉淡化。
- **outro**:收尾卡。骨架给"居中一组:图 + GitHub mark + repo 行,同步淡入"。

## 章节条(TopBar)

中间幕常驻顶栏:左品牌名、中间 `xx | yy` 章节列表(当前章节 `textPrimary` + 600,其余 `textMuted`)、右固定文案。`sections` 数组从 SHOTS 过滤 `diagram/video/duo` 派生,**不手写**。

## 字幕(Subtitles)

见 references/alignment.md。渲染层两条铁律:

- **每个词的盒子恒定**(统一 `inline-block + padding + margin`,高亮词不换 weight、不加 padding)——高亮/取消高亮绝不能改变排版,否则逐帧抖动;
- 时间基准用 Sequence 相对帧;行选择 = `now >= span.start` 的最后一行(VO 停顿期间保持上一行)。

## 音频

- 每幕 VO:`<Audio src={staticFile(shot.tts)} />`(@remotion/media 的 Audio)放在该幕 `<Sequence>` **内部**,与画面同进退。
- BGM:整片一层,放在所有 Sequence 之外(见 references/bgm.md)。

## 确定性

一切动画都是 `useCurrentFrame()` 的纯函数;禁 `requestAnimationFrame`/`Date.now`/`Math.random`(要随机用带种子的伪随机)。否则渲染帧不可复现、抽查帧对不上。

## 双 composition

主成片 `<Composition id="Promo">` 之外,可保留独立场景 composition 便于 Studio 单测(参考工程保留旧六幕)。注意它们若共用 TopBar 等组件,props 接口变更时两边都要过。
