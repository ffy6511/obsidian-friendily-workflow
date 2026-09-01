# ffmpeg 素材配方

所有输出统一参数(实测稳定的屏幕录制处理):

```
-c:v libx264 -crf 20 -preset veryfast -pix_fmt yuv420p -an -movflags +faststart
```

`-an` 去音轨(成片里素材静音,VO 另挂)。

## 多段保留(trim + concat 一次成型)

```bash
ffmpeg -y -v error -i 源.mp4 -filter_complex \
  "[0:v]trim=0:8,setpts=PTS-STARTPTS[a]; \
   [0:v]trim=10:17,setpts=PTS-STARTPTS[b]; \
   [0:v]trim=26:32,setpts=PTS-STARTPTS[c]; \
   [a][b][c]concat=n=3:v=1[out]" \
  -map "[out]" <统一参数> public/cuts/xx.mp4
```

秒数来自分镜文档的"视频内时间点"表;剪完必须 `measure.sh` 核对时长。

## 尾部定格(补齐幕长)

```bash
ffmpeg -y -v error -i in.mp4 -vf "tpad=stop_mode=clone:stop_duration=2.5" <统一参数> out.mp4
```

定格目标 = 幕长,不是 VO 长度:素材永远 ≥ 幕长,视频播完绝不出现白屏(Remotion 的 `<Video>` 越过媒体末尾行为不可靠)。

## 单段截取

```bash
ffmpeg -y -v error -ss 14 -i 源.mp4 <统一参数> out.mp4   # 14s 到结尾
ffmpeg -y -v error -ss 0 -t 14 -i 源.mp4 <统一参数> out.mp4
```

## 测时长

`scripts/measure.sh f1 f2 ...`(无参数 = 当前目录全部文件),内部是 `ffprobe -show_entries format=duration`。

## 踩坑记录

- **zsh 变量不分词**:`ENC="-c:v libx264 ..."; ffmpeg ... $ENC` 在 zsh 里是**一个参数**,ffmpeg 报奇怪的 filtergraph 错误。参数要么写全,要么用数组 `"${enc[@]}"`。
- `-filter_complex` 里 label 要闭合(`[out]` 必须被 `-map "[out]"` 消费),段名别与输入序号混淆。
- 抽帧验证用 `-ss <t> -i video -frames:v 1 out.png`(输入侧 seek,重编码源上精确)。
- 源素材文件名带空格/中文没问题(Quoted 传给 staticFile 即可),但**链到链的软链**在 Remotion 打包时会 404,实体拷贝最稳。
