# Changelog

All notable changes to the Video Expert Analyzer skill will be documented in this file.

## [2.2.0] - 2026-03-24

### Added
- ⚡ **大规模场景分批处理协议**：>10 个场景时强制分批（5-10个/batch），每批输出子报告并汇报进度，全部完成后汇总为完整报告并清理子报告
- 🚫 **反抽样策略（Anti-Sampling Policy）**：禁止抽样/跳过/合并场景，每个场景必须附带唯一视觉描述作为查看证据
- 🔍 **100% 覆盖率校验**：完成全部分析后校验 frames/ 中帧数与 scene_scores.json 已评分数，覆盖率必须 = 100%
- 🌐 补充 Windows (`winget`) 和 Linux (`apt`) 的 ffmpeg 安装说明

### Changed
- 📝 **重写 description 触发词**：增加中文关键词（视频分析/镜头筛选/场景评分/视频拆解/精选片段/镜头打分/素材挑选）和场景描述，提升 skill 触发准确率
- 补充小红书（Xiaohongshu）到 description 支持平台列表
- 硬编码路径 `~/.openclaw/...` 替换为通用 `<skill_dir>`

### Removed
- 🗑️ 删除严重过时的 `QUICKSTART.md`（引用 v1.x 废弃的 pipeline.py / scoring_helper.py / Whisper 参数）
- 清理运行日志 `error.log`、`log.txt`

### Fixed
- `.gitignore` 补充 `*.log`、`log.txt`、`batch_*_report.md` 规则

### Model Compatibility Notes
- ⚠️ **Kimi 2.5**：>30 个镜头时会出现偷懒行为（抽样分析），推测为服务端限制了模型最大连续工作时长或工具调用次数
- ✅ **GPT 5.4**：经测试可完成高达 **127 个镜头**的连续分析任务，模型预热后仅需 **11 分 48 秒**
- 🔲 **Gemini / Opus**：尚未测试大规模场景分析

---

## [2.1.0] - 2026-02-27

### Added
- ✅ 智能字幕提取：对齐 video-copy-analyzer，支持 B站API → 内嵌字幕 → RapidOCR → FunASR 四级降级
- ✅ 新增小红书支持：集成 `xiaohongshu_downloader.py`
- ✅ 新增 `requirements.txt`：一键安装所有依赖
- ✅ 新增模型兼容性矩阵
- ✅ 重写 `check_environment.py`
- ✅ 新增 Troubleshooting 章节

### Removed
- 移除旧版 pipeline、Whisper 转录等 6 个废弃脚本

---

## [2.0.0] - 2026-02-27

### Changed
- ✅ 重写 AI 评分系统：移除假数据模拟，接入真实视觉大模型
- ✅ 双路径评分：Agent 模式（宿主 AI 直接看图）+ API 模式（远程调用）
- ✅ 修复场景检测：`detect-adaptive` → `detect-content`
- ✅ 语音转录引擎 Whisper → FunASR (Paraformer-zh)
- ✅ 内置 VAD 自动分段 + 标点恢复

---

## [1.4.0] - 2026-02-06

### Added
- 新增抖音视频下载支持（自动识别链接、无水印下载）

## [1.3.0] - 2026-02-05

### Added
- 新增中英双语术语对照

## [1.2.0] - 2026-02-05

### Added
- AI 自动分析功能、动态权重评分系统、自动生成完整分析报告

## [1.1.0] - 2026-02-05

### Added
- 可配置输出目录、精选片段自动保存

## [1.0.0] - 2026-02-05

### Added
- 初始版本：基于 Walter Murch 六法则的视频分析工具
- yt-dlp 下载 + PySceneDetect 场景检测 + Whisper 转录
- 五维评分体系、评分辅助工具、报告模板
