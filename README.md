<p align="center">
  <img src="https://img.shields.io/badge/version-1.3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-yellow" alt="Python">
</p>

<p align="center">
  <b>🌐 Language / 语言</b><br>
  <a href="#english">English</a> | <a href="#chinese">中文</a>
</p>

---

<a name="english"></a>
# 🎬 Video Expert Analyzer

> AI-powered professional video analysis tool based on **Walter Murch's Six Rules of Editing**

## ✨ Features

- 🤖 **AI Auto-Analysis** - Automatic scene scoring and comprehensive report generation
- 🎯 **Dynamic Weighting** - Smart weighting system adapts to scene types
- 🎬 **Scene Detection** - PySceneDetect-powered automatic scene splitting
- 🎤 **Transcription** - OpenAI Whisper speech-to-text
- ⭐ **Best Shots** - Auto-copy top-rated clips to `best_shots/`
- 📊 **5D Scoring** - Aesthetic, Credibility, Impact, Memorability, Fun
- 🌐 **Bilingual** - All terminology with Chinese translations

## 🚀 Quick Start

### Prerequisites

```bash
# System dependencies
brew install ffmpeg  # macOS
# or
apt-get install ffmpeg  # Linux

# Python packages
pip3 install yt-dlp openai-whisper scenedetect[opencv]
```

### One-Command Analysis

```bash
# Setup (first time only)
python3 scripts/pipeline_enhanced.py --setup

# Analyze any video
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

# Run AI analysis
cd ~/Downloads/video-analysis/BV1xxxxx
python3 path/to/scripts/ai_analyzer.py scene_scores.json
```

## 📊 Scoring System

### Five Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Aesthetic Beauty** | 20% | Composition, lighting, color harmony |
| **Credibility** | 20% | Authenticity, natural performance |
| **Impact** | 20% | Visual power, attention-grabbing |
| **Memorability** | 20% | Uniqueness, Von Restorff Effect |
| **Fun/Interest** | 20% | Engagement, entertainment value |

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
| 🌟 **MUST KEEP** | Score ≥ 8.5 or any 10 | Core material |
| 📁 **USABLE** | 7.0 ≤ Score < 8.5 | Supporting shots |
| 🗑️ **DISCARD** | Score < 7.0 | Not recommended |

## 📁 Output Structure

```
output-directory/
├── {video_id}.mp4              # Full video
├── {video_id}.srt              # Subtitles
├── scene_scores.json           # ⭐ Scoring data
├── *_complete_analysis.md      # ⭐ Full report
├── scenes/                     # Scene clips
│   └── best_shots/             # ⭐ Top-rated clips
└── frames/                     # Preview frames
```

## 🔧 Configuration

| Option | Description |
|--------|-------------|
| `--whisper-model` | tiny/base/small/medium/large |
| `--scene-threshold` | Scene detection sensitivity (default: 27) |
| `--best-threshold` | Best shots threshold (default: 7.5) |

## 📚 Theory Background

Based on **Walter Murch's Six Rules**:
> Emotion > Story > Rhythm > Eye-trace > 2D Plane > 3D Space

A shot with genuine emotion but slight shake is better than a perfect but empty frame.

## 🙏 Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect)
- [FFmpeg](https://ffmpeg.org/)

---

<a name="chinese"></a>
# 🎬 视频专家分析器

> 基于 **Walter Murch 剪辑六法则** 和 **AI 自动评分系统** 的专业视频分析工具

## ✨ 核心特性

- 🤖 **AI 自动分析** - 自动为场景评分并生成完整分析报告
- 🎯 **动态权重系统** - 根据场景类型自动调整评分权重
- 🎬 **场景检测** - 基于 PySceneDetect 的自动场景分割
- 🎤 **语音转录** - 使用 OpenAI Whisper 进行语音识别
- ⭐ **精选片段** - 自动复制高分片段到 `best_shots/`
- 📊 **五维评分** - 美感、可信度、冲击力、记忆度、趣味度
- 🌐 **中英双语** - 所有专业术语附中文释义

## 🚀 快速开始

### 环境准备

```bash
# 系统依赖
brew install ffmpeg  # macOS
# 或
apt-get install ffmpeg  # Linux

# Python 依赖
pip3 install yt-dlp openai-whisper scenedetect[opencv]
```

### 一键分析

```bash
# 首次配置
python3 scripts/pipeline_enhanced.py --setup

# 分析视频
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

# 运行 AI 分析
cd ~/Downloads/video-analysis/BV1xxxxx
python3 path/to/scripts/ai_analyzer.py scene_scores.json
```

## 📊 评分体系

### 五维评分维度

| 维度 | 权重 | 评估要点 |
|------|------|---------|
| **美感 (Aesthetic)** | 20% | 构图(三分法)、光影质感、色彩和谐度 |
| **可信度 (Credibility)** | 20% | 表演自然度、物理逻辑、无出戏感 |
| **冲击力 (Impact)** | 20% | 视觉显著性、动态张力、第一眼吸引力 |
| **记忆度 (Memorability)** | 20% | 独特视觉符号、冯·雷斯托夫效应、金句 |
| **趣味度 (Fun)** | 20% | 参与感、娱乐价值、社交货币潜力 |

### 场景类型与动态权重

| 类型 | 权重分配 | 适用场景 |
|------|---------|---------|
| **TYPE-A 钩子型** | 冲击力 40% + 记忆度 30% | 开场钩子、高能时刻 |
| **TYPE-B 叙事型** | 可信度 40% + 记忆度 30% | 叙事段落、情感表达 |
| **TYPE-C 氛围型** | 美感 50% + 节奏 30% | 空镜头、氛围营造 |
| **TYPE-D 商业型** | 可信度 40% + 记忆度 40% | 产品展示、商业广告 |

### 筛选等级

| 等级 | 标准 | 用途 |
|------|------|------|
| 🌟 **强烈推荐保留** | 加权总分 ≥ 8.5 或 单项 = 10 | 核心素材，极致长板 |
| 📁 **可用素材** | 7.0 ≤ 加权总分 < 8.5 | 过渡素材，辅助叙事 |
| 🗑️ **建议舍弃** | 加权总分 < 7.0 | 建议舍弃 |

## 📁 输出结构

```
output-directory/
├── {video_id}.mp4              # 完整视频
├── {video_id}.srt              # 字幕文件
├── scene_scores.json           # ⭐ 完整评分数据
├── *_complete_analysis.md      # ⭐ 完整分析报告
├── scenes/                     # 场景片段
│   └── best_shots/             # ⭐ 精选片段
└── frames/                     # 预览帧
```

## 🔧 配置选项

| 选项 | 说明 |
|------|------|
| `--whisper-model` | tiny/base/small/medium/large |
| `--scene-threshold` | 场景检测阈值 (默认: 27) |
| `--best-threshold` | 精选阈值 (默认: 7.5) |

## 📚 理论背景

基于 **Walter Murch 剪辑六法则**：
> 情感 > 故事 > 节奏 > 视线追踪 > 2D平面 > 3D空间

一个情感真挚但画面略抖的镜头，优于一个画面完美但内容空洞的镜头。

## 🙏 致谢

本项目构建于以下开源工具：
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载
- [OpenAI Whisper](https://github.com/openai/whisper) - 语音转录
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) - 场景检测
- [FFmpeg](https://ffmpeg.org/) - 媒体处理

---

## 📜 License

MIT License - 自由使用和修改
