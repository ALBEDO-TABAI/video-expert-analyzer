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

## 📖 References

### Core Theory

1. **Murch, W.** (2001). *In the Blink of an Eye: A Perspective on Film Editing* (2nd ed.). Silman-James Press.  
   — The foundational text for the "Six Rules of Editing" prioritizing emotion over technical perfection.

2. **Murch, W.** (1995). *The Conversations: Walter Murch and the Art of Editing Film*. Knopf.  
   — In-depth discussion of editing philosophy and the 51% rule.

### Psychology & Cognitive Science

3. **Von Restorff, H.** (1933). Über die Wirkung von Bereichsbildungen im Spurenfeld. *Psychologische Forschung*, 18(1), 299-342.  
   — Original research on the "isolation effect" (Von Restorff Effect) explaining why distinctive items are more memorable.

4. **Itti, L., & Koch, C.** (2001). Computational modelling of visual attention. *Nature Reviews Neuroscience*, 2(3), 194-203.  
   — Foundation for Visual Saliency theory used in Impact scoring.

5. **Kahneman, D.** (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.  
   — Cognitive basis for first-impression impact and attention mechanisms.

### Social Media & Virality

6. **Berger, J.** (2013). *Contagious: Why Things Catch On*. Simon & Schuster.  
   — Framework for "Social Currency" and viral content characteristics.

7. **Berger, J., & Milkman, K. L.** (2012). What makes online content viral? *Journal of Marketing Research*, 49(2), 192-205.  
   — Academic research on emotional triggers in shareable content.

### Video & Film Analysis

8. **Bordwell, D., & Thompson, K.** (2012). *Film Art: An Introduction* (10th ed.). McGraw-Hill.  
   — Comprehensive framework for visual composition and cinematography analysis.

9. **Katz, S. D.** (1991). *Film Directing Shot by Shot: Visualizing from Concept to Screen*. Michael Wiese Productions.  
   — Technical reference for shot composition and visual storytelling.

10. **Brown, B.** (2016). *Cinematography: Theory and Practice* (3rd ed.). Routledge.  
    — Practical guide to lighting, framing, and visual aesthetics.

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

## 📖 参考文献

### 核心理论

1. **Murch, W.** (2001). 《眨眼之间：电影剪辑的奥秘》(第2版). Silman-James Press.  
   — "剪辑六法则"的奠基之作，强调情感优先于技术完美。

2. **Murch, W.** (1995). 《对话录：沃尔特·默奇与电影剪辑艺术》. Knopf.  
   — 深入探讨剪辑哲学和51%法则。

### 心理学与认知科学

3. **Von Restorff, H.** (1933). 关于痕迹场中区域形成的作用. *心理学研究*, 18(1), 299-342.  
   — "孤立效应"(冯·雷斯托夫效应)的原始研究，解释为何独特的事物更容易被记住。

4. **Itti, L., & Koch, C.** (2001). 视觉注意力的计算建模. *自然神经科学评论*, 2(3), 194-203.  
   — 冲击力评分中使用的"视觉显著性"理论基础。

5. **Kahneman, D.** (2011). 《思考，快与慢》. Farrar, Straus and Giroux.  
   — 第一印象冲击力和注意力机制的认知基础。

### 社交媒体与病毒传播

6. **Berger, J.** (2013). 《疯传：让你的产品、思想、行为像病毒一样入侵》. Simon & Schuster.  
   — "社交货币"和病毒内容特征的理论框架。

7. **Berger, J., & Milkman, K. L.** (2012). 什么让在线内容病毒式传播？*市场营销研究杂志*, 49(2), 192-205.  
   — 关于可分享内容中情感触发因素的学术研究。

### 视频与电影分析

8. **Bordwell, D., & Thompson, K.** (2012). 《电影艺术：形式与风格》(第10版). McGraw-Hill.  
   — 视觉构图和电影摄影分析的综合框架。

9. **Katz, S. D.** (1991). 《电影导演：从概念到银幕的镜头可视化》. Michael Wiese Productions.  
   — 镜头构图和视觉叙事的技术参考。

10. **Brown, B.** (2016). 《电影摄影：理论与实践》(第3版). Routledge.  
    — 灯光、构图和视觉美学的实用指南。

---

## 📜 License

MIT License - 自由使用和修改
