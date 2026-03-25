<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/python-3.9+-yellow" alt="Python">
  <img src="https://img.shields.io/badge/AI-Gemini%203.0%20%7C%20Kimi%202.5%20%7C%20Claude-purple" alt="AI Models">
</p>

<p align="center">
  <b>🌐 Language / 语言</b><br>
  <a href="#english">English</a> | <a href="#chinese">中文</a>
</p>

---

<a name="english"></a>
# 🎬 Video Expert Analyzer

> AI-powered professional video analysis tool based on **Walter Murch's Six Rules of Editing**, with real multimodal AI vision scoring (Gemini 3.0 / Kimi 2.5 / Claude).

## ✨ Features

- 🤖 **Real AI Vision Scoring** — Multimodal models (Gemini/Kimi/GPT-4o) analyze actual frame content
- 🔀 **Dual Scoring Paths** — Agent mode (IDE AI reads frames) + API mode (remote API calls)
- 🎯 **Dynamic Weighting** — Weights auto-adjust based on scene type (Hook/Narrative/Aesthetic/Commercial)
- 🎬 **Scene Detection** — PySceneDetect `detect-content` for accurate scene splitting
- 🎤 **Smart Subtitle Extraction** — 4-tier fallback: Bilibili API → Embedded → RapidOCR → FunASR
- ⭐ **Best Shots** — Auto-copy top-rated clips to `best_shots/`
- 📊 **5D Scoring** — Aesthetic, Credibility, Impact, Memorability, Fun/Interest
- 🌐 **Bilingual** — All terminology with Chinese translations

## 📱 Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **Bilibili** | ✅ Full Support | yt-dlp download + Bilibili API subtitles |
| **YouTube** | ✅ Full Support | yt-dlp download |
| **Douyin (抖音)** | ✅ Full Support | Dedicated downloader (public/share links do not need browser cookies) |
| **Xiaohongshu (小红书)** | ✅ Full Support | Dedicated downloader |
| **Others** | ⚠️ May Work | Depends on yt-dlp support |

## 🤖 Model Compatibility

| Model | Agent Mode | API Mode | Notes |
|-------|-----------|---------|-------|
| **Gemini 3.0 Flash** | ✅ Recommended | ✅ Recommended | Fast, strong vision |
| **Gemini 3.0 Pro** | ✅ Recommended | ✅ Supported | Best visual understanding |
| **Kimi 2.5** | ✅ Supported | ✅ Supported | Excellent for Chinese |
| **Claude (Sonnet/Opus)** | ✅ Supported | ❌ No | Has vision but no OpenAI-compatible API |
| **Text-only models** | ❌ No | ❌ No | Cannot score without vision |

> **Agent Mode** = AI assistant in IDE views frame images directly  
> **API Mode** = CLI calls vision model via OpenAI-compatible API

## 🚀 Quick Start

### Prerequisites

```bash
# System dependencies
brew install ffmpeg  # macOS

# Install all Python dependencies
pip3 install -r requirements.txt

# Check environment
python3 scripts/check_environment.py
```

### One-Command Analysis

```bash
# Setup (first time only)
python3 scripts/pipeline_enhanced.py --setup

# Analyze any video
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx
python3 scripts/pipeline_enhanced.py "https://www.douyin.com/video/xxxxx"

# AI scoring (choose one)
# Option A: Agent mode (in IDE, AI assistant scores visually)
# Option B: API mode
export VIDEO_ANALYZER_API_KEY="your-key"
python3 scripts/ai_analyzer.py scene_scores.json --mode api
```

## 📊 Scoring System

### Five Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Aesthetic Beauty** 美感 | 20% | Composition, lighting, color harmony |
| **Credibility** 可信度 | 20% | Authenticity, natural performance |
| **Impact** 冲击力 | 20% | Visual saliency, attention-grabbing |
| **Memorability** 记忆度 | 20% | Uniqueness, Von Restorff Effect |
| **Fun/Interest** 趣味度 | 20% | Engagement, entertainment, social currency |

### Scene Types & Dynamic Weights

| Type | Primary Weights | Use Cases |
|------|-----------------|-----------|
| **TYPE-A Hook** | Impact 40% + Memorability 30% | Opening hooks, high-energy moments |
| **TYPE-B Narrative** | Credibility 40% + Memorability 30% | Story segments, emotional scenes |
| **TYPE-C Aesthetic** | Aesthetics 50% + Sync 30% | B-roll, atmosphere shots |
| **TYPE-D Commercial** | Credibility 40% + Memorability 40% | Product showcases, ads |

### Selection Levels

| Level | Criteria | Usage |
|-------|----------|-------|
| 🌟 **MUST KEEP** | Score ≥ 8.5 or any dimension = 10 | Core material |
| 📁 **USABLE** | 7.0 ≤ Score < 8.5 | Supporting shots |
| 🗑️ **DISCARD** | Score < 7.0 | Not recommended |

## 📁 Output Structure

```
output-directory/
├── {video_id}.mp4              # Full video
├── {video_id}.m4a              # Audio
├── {video_id}.srt              # Subtitles (smart extraction)
├── scene_scores.json           # ⭐ AI scoring data
├── *_complete_analysis.md      # ⭐ Full analysis report
├── scenes/                     # Scene clips
│   └── best_shots/             # ⭐ Top-rated clips (auto-copied)
└── frames/                     # Preview frames
```

## 🔧 Configuration

### Pipeline Options

| Option | Description |
|--------|-------------|
| `--setup` | Configure output directory |
| `--scene-threshold` | Scene detection sensitivity (default: 27) |
| `--best-threshold` | Best shots threshold (default: 7.5) |
| `-o, --output` | Output directory |

### API Environment Variables

| Variable | Description |
|----------|-------------|
| `VIDEO_ANALYZER_API_KEY` | Vision model API key (required for API mode) |
| `VIDEO_ANALYZER_BASE_URL` | API endpoint (default: Gemini) |
| `VIDEO_ANALYZER_MODEL` | Model name (default: `gemini-2.0-flash`) |

## 📚 Theory Background

Based on **Walter Murch's Six Rules**:
> Emotion > Story > Rhythm > Eye-trace > 2D Plane > 3D Space

A shot with genuine emotion but slight shake is better than a perfect but empty frame.

## 🙏 Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Video download
- [FunASR](https://github.com/modelscope/FunASR) — Chinese speech recognition
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — Scene detection
- [FFmpeg](https://ffmpeg.org/) — Media processing
- [RapidOCR](https://github.com/RapidAI/RapidOCR) — Burned subtitle OCR

## 📖 References

### Core Theory

1. **Murch, W.** (2001). *In the Blink of an Eye* (2nd ed.). Silman-James Press.  
2. **Murch, W.** (1995). *The Conversations*. Knopf.  

### Psychology & Cognitive Science

3. **Von Restorff, H.** (1933). *Psychologische Forschung*, 18(1), 299-342.  
4. **Itti, L., & Koch, C.** (2001). *Nature Reviews Neuroscience*, 2(3), 194-203.  
5. **Kahneman, D.** (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.  

### Social Media & Virality

6. **Berger, J.** (2013). *Contagious*. Simon & Schuster.  
7. **Berger, J., & Milkman, K. L.** (2012). *Journal of Marketing Research*, 49(2), 192-205.  

### Video & Film Analysis

8. **Bordwell, D., & Thompson, K.** (2012). *Film Art* (10th ed.). McGraw-Hill.  
9. **Katz, S. D.** (1991). *Film Directing Shot by Shot*. Michael Wiese Productions.  
10. **Brown, B.** (2016). *Cinematography: Theory and Practice* (3rd ed.). Routledge.  

---

<a name="chinese"></a>
# 🎬 视频专家分析器

> 基于 **Walter Murch 剪辑六法则** 和 **真实 AI 视觉评分** 的专业视频分析工具

## ✨ 核心特性

- 🤖 **真实 AI 视觉评分** — 多模态大模型（Gemini/Kimi/GPT-4o）分析真实画面内容
- 🔀 **双路径评分** — Agent 模式（IDE 中 AI 直接看图）+ API 模式（远程 API 调用）
- 🎯 **动态权重系统** — 根据场景类型自动调整权重（Hook/叙事/氛围/商业）
- 🎬 **场景检测** — PySceneDetect `detect-content` 精准场景分割
- 🎤 **智能字幕提取** — 四级降级：B站API → 内嵌字幕 → RapidOCR → FunASR
- ⭐ **精选片段** — 自动复制高分片段到 `best_shots/`
- 📊 **五维评分** — 美感、可信度、冲击力、记忆度、趣味度
- 🌐 **中英双语** — 所有专业术语附中文释义

## 📱 支持平台

| 平台 | 支持状态 | 说明 |
|------|---------|------|
| **Bilibili** | ✅ 完全支持 | yt-dlp 下载 + B站API字幕 |
| **YouTube** | ✅ 完全支持 | yt-dlp 下载 |
| **抖音 (Douyin)** | ✅ 完全支持 | 专用下载器（公开/分享链接无需浏览器 cookie） |
| **小红书 (Xiaohongshu)** | ✅ 完全支持 | 专用下载器 |
| **其他平台** | ⚠️ 可能支持 | 取决于 yt-dlp |

## 🤖 模型兼容性

| 模型 | Agent 模式 | API 模式 | 说明 |
|------|-----------|---------|------|
| **Gemini 3.0 Flash** | ✅ 推荐 | ✅ 推荐 | 速度快、视觉能力强 |
| **Gemini 3.0 Pro** | ✅ 推荐 | ✅ 支持 | 最强视觉理解 |
| **Kimi 2.5** | ✅ 支持 | ✅ 支持 | 中文语境优秀 |
| **Claude (Sonnet/Opus)** | ✅ 支持 | ❌ 不支持 | 有视觉能力但无 OpenAI 兼容 API |
| **纯文本模型** | ❌ 不可用 | ❌ 不可用 | 无视觉能力 |

## 🚀 快速开始

### 环境准备

```bash
# 系统依赖
brew install ffmpeg

# 一键安装所有依赖
pip3 install -r requirements.txt

# 检查环境
python3 scripts/check_environment.py
```

### 一键分析

```bash
# 首次配置
python3 scripts/pipeline_enhanced.py --setup

# 分析视频
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx
python3 scripts/pipeline_enhanced.py "https://www.douyin.com/video/xxxxx"

# AI 评分（二选一）
# 方式 A：Agent 模式（IDE 中 AI 助手直接看图评分）
# 方式 B：API 模式
export VIDEO_ANALYZER_API_KEY="your-key"
python3 scripts/ai_analyzer.py scene_scores.json --mode api
```

### 抖音链接说明

- 公开可访问的抖音链接，优先直接交给本地脚本处理，不要先尝试网页登录或浏览器 cookie
- 推荐命令：

```bash
python3 scripts/pipeline_enhanced.py "<抖音链接>"
# 或只下载视频
python3 scripts/download_douyin.py "<抖音链接>" ./video.mp4
```

- 如果在 WSL、远程容器或无桌面浏览器环境里看到“cookie 无法读取”的报错，说明走错路线了，应切回上面的本地脚本
- 优先使用从抖音 App 复制的 `https://v.douyin.com/...` 分享短链；长链同样支持

## 📊 评分体系

### 五维评分维度

| 维度 | 权重 | 评估要点 |
|------|------|---------| 
| **美感 (Aesthetic)** | 20% | 构图(三分法)、光影质感、色彩和谐度 |
| **可信度 (Credibility)** | 20% | 表演自然度、物理逻辑、无出戏感 |
| **冲击力 (Impact)** | 20% | 视觉显著性、动态张力、第一眼吸引力 |
| **记忆度 (Memorability)** | 20% | 独特视觉符号、冯·雷斯托夫效应 |
| **趣味度 (Fun)** | 20% | 参与感、娱乐价值、社交货币潜力 |

### 筛选等级

| 等级 | 标准 | 用途 |
|------|------|------|
| 🌟 **MUST KEEP** | 加权总分 ≥ 8.5 或 单项 = 10 | 核心素材 |
| 📁 **USABLE** | 7.0 ≤ 加权总分 < 8.5 | 辅助素材 |
| 🗑️ **DISCARD** | 加权总分 < 7.0 | 建议舍弃 |

## 📁 输出结构

```
输出目录/
├── {video_id}.mp4              # 完整视频
├── {video_id}.m4a              # 音频
├── {video_id}.srt              # 字幕（智能提取）
├── scene_scores.json           # ⭐ AI 评分数据
├── *_complete_analysis.md      # ⭐ 完整分析报告
├── scenes/                     # 场景片段
│   └── best_shots/             # ⭐ 精选片段（自动复制）
└── frames/                     # 预览帧
```

## 🔧 配置选项

| 选项 | 说明 |
|------|------|
| `--setup` | 配置输出目录 |
| `--scene-threshold` | 场景检测阈值 (默认: 27) |
| `--best-threshold` | 精选阈值 (默认: 7.5) |

## 📚 理论背景

基于 **Walter Murch 剪辑六法则**：
> 情感 > 故事 > 节奏 > 视线追踪 > 2D平面 > 3D空间

一个情感真挚但画面略抖的镜头，优于一个画面完美但内容空洞的镜头。

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — 视频下载
- [FunASR](https://github.com/modelscope/FunASR) — 中文语音识别
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — 场景检测
- [FFmpeg](https://ffmpeg.org/) — 媒体处理
- [RapidOCR](https://github.com/RapidAI/RapidOCR) — 烧录字幕识别

---

## 📜 License

MIT License - 自由使用和修改
