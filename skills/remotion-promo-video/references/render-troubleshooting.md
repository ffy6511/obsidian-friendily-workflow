# 渲染与故障排查

## 渲染

```bash
npx remotion render Promo out/promo-en.mp4     # 全片
npx remotion render Promo out/mini.mp4 --frames=1080-1440   # 抽段调试
```

`remotion.config.ts`(骨架已带)固定 png 帧格式 / h264 / crf20 / `-tune animation` / `+faststart`。

## 渲染前检查

- **残留进程**:之前取消的 Bash 可能留下活着的 Chrome/renderer 子进程,先 `ps aux | grep -i remotion` 再开新渲染,避免两个渲染互相踩。
- `npx tsc --noEmit` 过了再渲染。

## 字体:为什么渲染会报 fonts.gstatic NetworkError

Remotion 启动的 Chrome 带 `--no-proxy-server --proxy-server='direct://' --proxy-bypass-list='*'`(硬编码在
`node_modules/.pnpm/@remotion+renderer@<版本>_*/node_modules/@remotion/renderer/dist/open-browser.js`),
在需要代理的网络里 **fonts.gstatic.com 直连不通**,`@remotion/google-fonts` 的运行时加载直接失败。

**正解(骨架默认):自托管字体**——woff2 下载到 `public/fonts/`,用 `@remotion/fonts` 的 `loadFont({url: staticFile(...)})` 加载(参考工程的 `src/theme/typography.ts` 有完整写法)。本地文件永远可用。

**兜底:代理补丁**(仅当被迫用 google-fonts 时)。完整闭环,缺一步都会留下坏状态:

```bash
F=$(find node_modules/.pnpm -path "*renderer/dist/open-browser.js" | head -1)
cp "$F" /tmp/open-browser.js.bak<N>          # 1. 备份(N 递增)
grep -v "proxy-server\|proxy-bypass-list\|no-proxy-server" "$F" > /tmp/ob-clean.js
mv /tmp/ob-clean.js "$F"                     # 2. 剥离三行 flag
npx remotion render ...                      # 3. 渲染
grep -c proxy /tmp/open-browser.js.bak<N>    # 4a. 渲染后恢复前,先校验备份还有 flag!
cp /tmp/open-browser.js.bak<N> "$F"          # 4b. 恢复
grep -c proxy "$F"                           # 5. 复核 = 3
```

踩过的坑:**备份时机**。跨多次渲染复用备份时,拿到的"备份"可能本身就是剥离版(上次恢复失败/顺序错误),用它"恢复"等于永远裸奔。所以第 4a 步的校验不可省;发现备份无效就换更早的备份(保留多个递增备份正是为此)。

## 渲染后的验证(必做)

Studio 里看一眼不算数——字幕错位、定格缺失、duo 焦点时机这类问题只在成片上按时间点抽查才能发现:

```bash
scripts/verify-frames.sh out/promo-en.mp4 12.5:p2-mid 15.2:p2-l4 124.5:outro
```

每个抽查点应是"已知状态"的时刻:某行字幕中段(核对文本+高亮词)、duo 交换点前后各一张(核对明暗)、开场/收尾(核对构图)。

## 其他

- 输出时长 ≠ 预期:先查 `timeline.ts` 的 TOTAL_FRAMES(ffprobe 成片对照),再查某幕 `durationInSeconds` 是否被脚本批量替换误伤。
- 渲染中断在重试前先删掉半成品输出文件,避免 `+faststart` 二次封装踩旧文件。
