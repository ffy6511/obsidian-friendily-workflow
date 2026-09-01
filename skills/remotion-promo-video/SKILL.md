---
name: remotion-promo-video
description: Build a TTS-narrated promo/explainer video (MP4) from user-provided footage and narration text. Self-contained Remotion 4 pipeline with MLX Qwen3-TTS voiceover (zh+en), whisper word-level synchronized subtitles with word-highlight chips, ffmpeg footage preprocessing, split-screen layouts and an optional looping BGM bed. Use whenever the user wants to produce, revise, or re-cut a narrated video — mentions like 宣传片 / 宣传视频 / promo video / product video / 口播 / 配音视频 / TTS 视频 / 给视频配字幕 / 字幕和语音对齐 / Remotion — even if they don't name the tooling. macOS (Apple Silicon) + MLX.
---

# remotion-promo-video:Remotion + MLX TTS 宣传视频流水线

从用户提供的**视频素材 + 分幕旁白文案**出发,产出一支带**词级同步字幕**的 TTS 口播成片。整体框架是 Remotion 4(1920×1080@60fps),TTS 用 mlx_audio(Qwen3-TTS),字幕对齐用 mlx_whisper 词级时间戳 + LCS 文本匹配。参考实现:`/Users/zhuo/Developer/work/bora-设计文档/视频素材/ageval-promo`(AgEval 宣传片,本 skill 的全部模式与坑都出自它)。

## 前置条件

- macOS + Apple Silicon;`uv`;模型已缓存:Qwen3-TTS(`mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit`)与 whisper(`mlx-community/whisper-large-v3-turbo`),首次运行会自动下载
- Node ≥ 18 + ffmpeg(系统 PATH);Remotion 依赖在**使用时** `npm install`,不进本 skill

## 目录结构

```text
remotion-promo-video/
├── SKILL.md                    # 入口:七步流水线 + 硬规则(本文件)
├── references/                 # 按需深入,做哪步读哪份
│   ├── pipeline.md             # 七步流程详解 + 时长校准规则(先读这份)
│   ├── tts.md                  # TTS 参数、增量重导、发音问题处理
│   ├── alignment.md            # 对齐算法、未匹配词插值、踩坑记录
│   ├── remotion-patterns.md    # SHOTS 单一事实源、五种布局、章节条
│   ├── ffmpeg.md               # 剪切/拼接/定格配方、zsh 坑
│   ├── render-troubleshooting.md  # 字体网络问题与代理补丁、渲染验证法
│   └── bgm.md                  # BGM 站点(Pixabay 等)+ 已验证的混音接法
├── assets/                     # 拷进用户项目直接用的成品
│   ├── tts-generate.py         # SEGMENTS 驱动的双语 TTS 导出 → 放 <项目>/tts/
│   ├── tts-align.py            # whisper 词级对齐 → <项目>/src/captions.json
│   └── project/                # 最小 Remotion 工程骨架(源码;依赖使用时安装)
│       ├── package.json / tsconfig.json / remotion.config.ts
│       ├── public/             # tts / cuts / bgm / fonts / media 约定见其 README
│       └── src/                # timeline.ts(单一事实源)+ MainVideo + 组件
└── scripts/                    # 辅助命令
    ├── measure.sh              # ffprobe 批量测时长
    └── verify-frames.sh        # 按时间戳抽帧验证成片
```

## 流水线(七步)

1. **收输入**:视频素材(可为原始未剪)、分幕旁白(zh/en)、品牌命名规范(品牌名大写,CLI/域名小写)。缺失的分镜结构先和用户对齐再动工。
2. **建工程**:拷 `assets/project/` → `npm install`;`assets/tts-generate.py`、`assets/tts-align.py` 放进项目 `tts/`。详见 references/pipeline.md。
3. **写文案**:generate.py 的 `SEGMENTS`(数组顺序 = 播放顺序)与 timeline.ts 的 `SHOTS.captions` **必须逐字同步**;`SHOTS` 是时长/素材/字幕的单一事实源,见 references/remotion-patterns.md。
4. **导 TTS**:`uv run tts-generate.py`(全部)或 `uv run tts-generate.py <id>`(增量);`scripts/measure.sh tts/en/*.wav` 实测时长。参数与发音处理见 references/tts.md。
5. **对齐**:`uv run tts-align.py` → `src/captions.json`;**每次重导 TTS 后必须重跑**。算法与坑见 references/alignment.md。
6. **剪素材**:ffmpeg 预剪到 `public/cuts/`(配方见 references/ffmpeg.md),tpad 定格到幕长。
7. **校准 + 渲染**:幕时长 = max(EN VO + 0.5s 呼吸, 素材下限);渲染 → `scripts/verify-frames.sh` 抽帧验证 → 打开成片。可选 BGM(见 references/bgm.md)。

## 硬规则(踩过的坑,违反必返工)

- 改旁白 = 改**三处**:generate.py SEGMENTS、timeline.ts captions、重跑 align.py。只改一处字幕必错位。
- 素材永远用 `tpad` 冻结到幕长——视频播完不能出现白屏/黑屏。
- 每一幕的 VO 用独立 `<Audio>` 挂在该幕 Sequence 内;字幕组件的时间基准是 **Sequence 相对帧**,不要拿全局帧算。
- 字幕对齐里**未匹配词必须插值**;插值扫描写错会让词塌缩到 [0,0],表现为"整句字幕从幕首挂到最后且无高亮"(真实事故,见 references/alignment.md)。
- whisper 听错产品名是常态("AgEval"→"AGL"),靠插值兜底,不要试图让 TTS/whisper 完美。
- 渲染报 fonts.gstatic NetworkError:项目模板已用**自托管字体**规避;若引入 @remotion/google-fonts,按 references/render-troubleshooting.md 打代理补丁(备份→剥离→渲染→**校验备份**→恢复)。
- 开新渲染前先确认没有残留渲染进程(取消的 Bash 可能留下活着的子进程)。
- 双语 TTS:成片用 en 校准幕长;zh 音频常比 en 长,做中文版前必须逐幕重校。
