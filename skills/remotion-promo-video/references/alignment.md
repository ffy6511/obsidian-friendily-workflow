# 字幕-语音词级对齐

两层配合:`tts-align.py`(模板)产出词级时间戳,`src/components/Subtitles.tsx`(骨架)运行时做 LCS 匹配 + 插值。这套是自包含的;外部参考(未安装,仅思路来源):`https://github.com/browser-use/video-use`。

## 数据流

```
en/0N_*.wav --mlx_whisper--> captions.json --LCS+插值--> 每行每词的 [start, end) --帧内查表--> 高亮哪个词
```

- `tts-align.py`:对每个 en 段跑 `mlx_whisper.transcribe(..., word_timestamps=True)`(模型 `mlx-community/whisper-large-v3-turbo`),写出
  `{ "<segment id>": { "duration": <s>, "words": [{"w","s","e"}, ...] } }` 到 `src/captions.json`。
- `Subtitles.tsx`:把 timeline 的 caption 行拆成词流,与 whisper 词流做 LCS;匹配上的词拿真实时间,没匹配上的词在"前一个匹配词的 end"与"后一个匹配词的 start"之间线性插值。
- 时间基准:**Sequence 相对秒**(组件在幕的 Sequence 内,`useCurrentFrame()/fps`),whisper 时间也是单段相对秒——天然对齐,不要引入全局偏移。

## 归一化与匹配规则

```ts
const norm = (w) => w.toLowerCase().replace(/[^a-z0-9]+/g, "");
const matches = (a, b) =>
  a === b || (a.length >= 4 && b.length >= 4 && (a.includes(b) || b.includes(a)));
```

- 大小写、标点全抹平(`level:` vs `level.` 命中)。
- 包容匹配解决连写词:字幕 `first-class`(→`firstclass`)对上 whisper 拆开的 `first` + `class` 中的前者。
- 专有名词听错(`AgEval` → whisper `AGL`)**不匹配、走插值**;插值区间是 [前词.end, 后词.start],实际发音点就落在里面,视觉误差 <0.5s,可接受。不要试图穷举纠错。

## 踩坑记录(真实事故)

1. **插值扫描写错 → 未匹配词塌缩到 [0,0]**。错误写法:
   ```ts
   while (e < flat.length && flat[e] !== null && Number.isNaN(flat[e]!.s)) e++;
   ```
   从未匹配词自身开始判断,`flat[k]` 为占位时条件立刻为假,循环体不执行,词的时间留在 NaN 占位,最终渲染成 `[0,0]`。后果链:该行 `start=0` → "当前行"选择逻辑(`now >= start` 的最后一行)让**这一行从整幕第 0 秒挂到最后**、且永远无高亮。正确写法(骨架已带):占位符带 `{t, s: NaN, e: NaN}`,扫描条件 `while (flat[e] && Number.isNaN(flat[e].s)) e++`,落到下一个真实词取 `nextS`。
2. **只改文案不改 captions/不重跑 align**:字幕文本与音频内容脱节,LCS 匹配率掉到 0.8 以下触发词数加权回退(线性铺时间),表现为"高亮大体能跑但明显不贴"。修法永远是把三处(generate.py、timeline captions、align)一起改。
3. **行首词匹配失败最致命**(见坑 1),行中词失败只是该词无独立高亮。拆 caption 行时尽量让**行的第一个词是实词**(代词/专有名词容易被 whisper 听花)。
4. **匹配率阈值 0.8**:低于则整体回退 `weightedSpans`(按词数线性铺)。回退是兜底不是修复——看到回退日志应先查文案是否同步,而不是调阈值。
5. whisper 偶发把整段首词时间标成 0.00 之后的一小段静音里——表现为字幕比语音早 ~0.3s。若整片系统性偏早,可在 align 输出统一加固定偏移(参考工程未做,出现再说)。

## 验证方法

渲染后抽帧,选**每行中段**的时刻,核对:字幕文本 = 该时刻正在念的句子;高亮词 = 正在念的词。参考命令见 `scripts/verify-frames.sh`。行首帧无法区分"正常切换"与"挂错",别用行首做抽查点。
