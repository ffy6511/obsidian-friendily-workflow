# TTS(mlx_audio + Qwen3-TTS)

模板:`assets/tts-generate.py`(放项目 `tts/` 目录,`uv run` 执行)。

## 模型与配置

- 模型:`mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit`(48GB 统一内存实测可用;0.6B 是更快的草稿版,音质略差)。
- `resolve_model()`:优先用 HuggingFace 缓存里的本地 snapshot,**避免渲染机联网** huggingface.co。
- Metal 内存三档(48GB 机器实测值,按机器调整):`WIRED_LIMIT_GB=36 / MEMORY_LIMIT_GB=37 / CACHE_LIMIT_GB=8`。TTS 是 GPU 逐步解码,加 CPU 核不涨速。
- 速度:~42 tokens/s,**实时率约 2.8×**(30s 音频约 11s 生成),整片重导很快。

## 声音与提示词

- 中文:`Vivian`(备选 Serena/Dylan/Eric);英文:`Aiden`(备选 Ryan/Chelsie/Ethan)。
- instruct 决定语气,直接决定"像不像产品讲解":
  - zh:`产品介绍，像对着镜头跟用户讲话。语速中等稍快。不要播音腔，不要卖货。`
  - en:`Calm product walkthrough, talking to another engineer on camera. Medium-fast. Hit <术语> clearly. Not a radio host, not a sales pitch.`(把该读清楚的术语列进去)
- `TEMPERATURE=0.55`、`SPEED=1.0`。同一段重导音色/语速会有细微差异——又一个"没改文案就别重导"的理由。

## SEGMENTS 结构

```python
SEGMENTS = [
    {"id": "01_slogan", "zh": "……", "en": "……"},
    ...
]
```

- 数组顺序 = 播放顺序;`id` 即文件名,**重排幕序不改 id**,注释写清映射。
- 每次运行结尾会把**全部已有 wav** 按数组顺序拼 `en/full.wav`、`zh/full.wav`(0.5s 间隔)——按新顺序重排 SEGMENTS 后随便重导一段即可重建参考混音;只想重排混音不重导音频时,用 python 直接调 `_concat()`。

## 发音问题的处理方式

TTS 念不对的词,**改 TTS 文本的拼写而不改字幕**(字幕保持书面形式,对齐算法兜底):

| 问题 | TTS 文本写法 |
| --- | --- |
| 品牌名被念错(如 "AgEval"→"AgEvil") | 按音节拆写,实测哪种读法对用哪种 |
| `×` 符号 | en: "times";zh: "乘以" |
| `qwen3.8-max` | "Qwen 3.8 Max" |
| URL | 整串照写通常可读;念不好就口播里去掉 URL,屏幕展示 |

whisper 侧听错(如 "AgEval"→"AGL")**不需要修**——对齐算法把未匹配词插值掉,详见 references/alignment.md。

## 增量重导与幂等

```bash
uv run tts-generate.py             # 全部
uv run tts-generate.py 02_pain     # 单段(支持唯一前缀)
uv run tts-generate.py --list
```

重导单段后**必须重跑 tts-align.py**,并检查 timeline.ts 里对应 captions 是否还与文案一致。
