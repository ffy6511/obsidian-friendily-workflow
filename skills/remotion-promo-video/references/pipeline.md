# 流水线详解

参考实现:`视频素材/ageval-promo`(下称"参考工程")。所有命令都在工程根目录执行。

## 1. 输入收集

- **视频素材**:原始录制即可(ffmpeg 预剪在后面)。先 `scripts/measure.sh` 量一遍每个源文件时长,写进分镜文档。
- **旁白**:按幕组织,每幕 zh + en 双语(en 成片,zh 备用)。en 文案要写成"可发音"形式:产品名按读法拼写(如 Qwen3.8 Max → "Qwen 3.8 Max")、符号转口语("×" → en "times" / zh "乘以")。屏幕字幕(captions)用**书面拼写**,对齐算法会兜底。
- **命名规范**:品牌名(口播/屏上)与代码标识(CLI、域名、仓库路径,保持小写)分开,全程一致。
- 分镜结构(几幕、顺序、每幕用什么素材)先和用户对齐再动工;用户改了文案,以用户稿为准同步另一语言,不要自行增删内容。

## 2. 工程结构

拷 `assets/project/`,改名后 `npm install`。目录约定:

```
project/
├── tts/                  # tts-generate.py / tts-align.py;生成 en/ zh/ wav
├── public/
│   ├── tts -> ../tts     # 软链或直接拷贝;Remotion staticFile 读取
│   ├── cuts/             # ffmpeg 预剪后的素材(定格外)
│   ├── bgm/              # 背景音乐
│   ├── fonts/            # 自托管 woff2(可选,见 render-troubleshooting.md)
│   └── media/            # 直用的图/视频(hero 图、logo 等)
└── src/                  # Remotion 源码(timeline.ts 是单一事实源)
```

注意:public 里的**目录软链**在打包时可正常解析,但**跨两级**的软链(链到链)会 404——参考工程里 `public/hero.png` 最终用了实体拷贝。

## 3. 文案双写

`SEGMENTS`(tts-generate.py)与 `SHOTS`(src/timeline.ts)的 captions 必须逐字一致。约定:

- SEGMENTS 数组顺序 = 播放顺序;`id` 是文件名,**重排幕序时不改 id**(如 `04_demo` 可以排第三),在注释里写清映射。
- captions 按"一句话一行"拆分——行的粒度决定字幕换行节奏,过长的一行在 1200px 胶囊里会折两行。
- en TTS 文本与 en 字幕允许有拼写差(TTS 用可发音形式,字幕用书面形式),对齐算法按归一化词匹配 + 插值兜底。

## 4. TTS 导出与测量

```bash
cd tts
uv run tts-generate.py            # 全部段落,zh+en
uv run tts-generate.py 02_pain    # 只重导一段(其他 wav 不动!)
../scripts/measure.sh en/*.wav    # 实测时长,填进分镜文档表格
```

增量重导是关键习惯:**没改文案的段绝不重导**——TTS 有随机性,重导会让已对齐的 whisper 时间戳失效。

## 5. 对齐

```bash
uv run tts-align.py               # 全部 en 段 → ../src/captions.json
```

输出格式 `{ "<segment id>": { "duration": s, "words": [{"w","s","e"}, ...] } }`,Subtitles 组件运行 LCS 匹配。**每次重导 TTS 后必须重跑**。算法与坑详见 references/alignment.md。

## 6. 素材预剪

见 references/ffmpeg.md。要点:

- 多段保留用 `filter_complex` 的 `trim/setpts/concat` 一次成型;
- 尾部用 `tpad=stop_mode=clone:stop_duration=N` 冻结到**幕长**(不是到 VO 长度);
- 重剪后 `scripts/measure.sh public/cuts/*.mp4` 核对。

## 7. 校准、渲染、验证

**时长校准规则**:幕长 = `max(EN VO + 0.5s 呼吸, 素材下限)`。
- 图表幕(无素材)纯跟 VO;
- 视频幕受素材下限约束;VO 结束后多余的素材画面继续播(或定格)是正常的;
- 需要改 `durationInSeconds` 时用脚本批量替换 timeline.ts,改完 `npx tsc --noEmit` 验证。

```bash
# 渲染(先看 render-troubleshooting.md 的字体/代理一节)
npx remotion render Promo out/promo-en.mp4
# 验证:在"已知对齐时刻"抽帧,核对字幕文本 + 高亮词 + 画面状态
../scripts/verify-frames.sh out/promo-en.mp4 12.5:p2-mid 15.2:p2-l4 124.5:outro
open out/promo-en.mp4
```

验证不是可选步骤:字幕错位类问题在 Studio 里很难发现,必须在成片抽帧核对。抽查点选在**一行的中段**(而非行首)——行首帧分不清"刚显示"还是"挂错"。

## 双语版本

- en 成片先行;zh 素材同源(TTS 已双导)。
- zh 音频时长 ≠ en:做中文版前逐幕 `measure.sh zh/*.wav`,幕长重校准,素材定格重补;某幕 zh 超长是常态(参考工程里曾出现 zh 比 en 幕长多 5s)。
