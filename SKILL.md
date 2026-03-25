---
name: video-expert-analyzer
description: Advanced video analysis and selection skill with AI-powered automatic scoring. Integrates Walter Murch's rules and dynamic weighting for professional-grade curation. Supports Bilibili, YouTube, Douyin (抖音), and Xiaohongshu (小红书). Use this skill whenever the user wants to analyze videos, score or rate scenes, extract best shots/highlights, evaluate video quality, curate clips, do competitor video analysis, or mentions terms like "视频分析", "镜头筛选", "场景评分", "视频拆解", "精选片段", "视频质量", "镜头打分", "素材挑选" — even if they don't explicitly ask for "expert analysis".
---

# Video Expert Analyzer - 视频专家分析工具

基于 **Walter Murch 剪辑六法则** 和 **AI 自动评分系统** 的专业视频分析工具。

## 支持平台

| 平台 | 支持状态 | 说明 |
|------|---------|------|
| **Bilibili** | ✅ 完全支持 | yt-dlp 下载 + B站API字幕 |
| **YouTube** | ✅ 完全支持 | yt-dlp 下载 |
| **抖音 (Douyin)** | ✅ 完全支持 | 专用下载器（公开/分享链接无需浏览器 cookie） |
| **小红书 (Xiaohongshu)** | ✅ 完全支持 | 专用下载器 |
| **其他平台** | ⚠️ 可能支持 | 取决于 yt-dlp 支持情况 |

## 核心特性

✅ **真实 AI 视觉评分** - 调用多模态大模型（Gemini 3.0/Kimi 2.5）真实分析画面内容  
✅ **双路径评分** - 支持「Agent 模式」（宿主 AI 直接看图）和「API 模式」（远程 API 调用）  
✅ **中英双语术语** - 所有专业术语附中文释义  
✅ **可配置输出目录** - 首次使用设置，后续自动使用  
✅ **精选片段自动复制** - 自动复制到 `scenes/best_shots/`  
✅ **完整分析报告** - 包含理论依据、评分理由、整体评价（非模板）  
✅ **动态权重系统** - 根据场景类型自动调整评分权重  
✅ **智能文件夹命名** - 以视频标题（自动裁剪）命名输出文件夹，更直观易懂

> **⚠️ 重要提示：本 skill 的 AI 评分功能需要多模态（视觉理解）模型才能正常工作。**  
> 请确保使用 Gemini 3.0、Kimi 2.5 等具备视觉能力的模型来调用此 skill。  

## 模型兼容性

| 模型 | Agent 模式 | API 模式 | 说明 |
|------|-----------|---------|------|
| **Gemini 3.0 Flash** | ✅ 推荐 | ✅ 推荐 | 速度快、视觉能力强 |
| **Gemini 3.0 Pro** | ✅ 推荐 | ✅ 支持 | 最强视觉理解 |
| **Kimi 2.5** | ✅ 支持 | ✅ 支持 | 中文语境优秀 |
| **Claude (Sonnet/Opus)** | ✅ 支持 | ❌ 不支持 | 有视觉能力但无 OpenAI 兼容 API |
| **纯文本模型** | ❌ 不可用 | ❌ 不可用 | 无视觉能力，无法评分 |

> **Agent 模式** = 在 IDE（Cursor/VS Code/OpenClaw）中，AI 助手直接查看帧图片评分  
> **API 模式** = 在终端 CLI 中，通过 OpenAI 兼容 API 远程调用视觉模型

## 术语对照表 (Terminology)

### 五维评分维度 (Five Dimensions)

| 英文术语 | 中文释义 | 详细说明 |
|---------|---------|---------|
| **Aesthetic Beauty** | 美感 | 构图(三分法)、光影质感、色彩和谐度 |
| **Credibility** | 可信度 | 表演自然度、物理逻辑真实感、无出戏感 |
| **Impact** | 冲击力 | 视觉显著性(Visual Saliency)、动态张力、第一眼吸引力 |
| **Memorability** | 记忆度 | 独特视觉符号、冯·雷斯托夫效应(Von Restorff Effect)、金句 |
| **Fun/Interest** | 趣味度 | 参与感、娱乐价值、社交货币(Social Currency)潜力 |

### 场景类型 (Scene Types)

| 类型 | 中文释义 | 特点 |
|------|---------|------|
| **TYPE-A Hook** | 钩子/开场型 | 高冲击力、吸引注意力 |
| **TYPE-B Narrative** | 叙事/情感型 | 人物对话、情感表达 |
| **TYPE-C Aesthetic** | 氛围/空镜型 | 风景、慢动作、极简构图 |
| **TYPE-D Commercial** | 商业/展示型 | 产品特写、广告展示 |

### 筛选等级 (Selection Levels)

| 等级 | 中文释义 | 标准 |
|------|---------|------|
| **MUST KEEP** | 强烈推荐保留 | 加权总分 ≥ 8.5 或 单项 = 10 |
| **USABLE** | 可用素材 | 7.0 ≤ 加权总分 < 8.5 |
| **DISCARD** | 建议舍弃 | 加权总分 < 7.0 |

### 理论术语 (Theory Terms)

| 英文 | 中文 | 说明 |
|------|------|------|
| **Walter Murch's Six Rules** | 沃尔特·默奇六法则 | 情感>故事>节奏>视线追踪>2D平面>3D空间 |
| **Von Restorff Effect** | 冯·雷斯托夫效应 | 独特的项目更容易被记住 |
| **Visual Saliency** | 视觉显著性 | 吸引眼球的程度 |
| **Social Currency** | 社交货币 | 内容被分享的价值 |
| **CTA** | 行动号召 | Call to Action |
| **SYNC** | 节奏同步 | 画面与音频节拍的契合度 |

## 快速开始

### 第 1 步：数据处理 Pipeline

```bash
# 首次配置（只需一次）
python3 scripts/pipeline_enhanced.py --setup

# 分析视频
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx
python3 scripts/pipeline_enhanced.py "https://www.douyin.com/video/xxxxx"
```

### 第 2 步：AI 评分（二选一）

首次使用时，请选择评分模式：

#### 🅰️ Agent 模式（推荐，IDE/OpenClaw/Cursor 用户）

如果你正在 IDE 或 AI 编程助手中使用此 skill，**无需配置任何 API Key**。
宿主 AI 助手（如 Gemini、Kimi）本身就具备视觉理解能力，可以直接「看图打分」。

**流程：** 当你（AI 助手）拥有视觉理解能力时，在 pipeline 完成后执行以下步骤：

1. **统计场景总数**：先列出 `<output_dir>/frames/` 目录，确定总共有多少个场景帧。这决定了后续分批策略。
2. **分批查看帧画面**：每批 5-10 张帧图片为一个 batch（每批超过 10 张会降低单图分析质量，少于 5 张效率太低）。使用 `view_file` 工具批量查看 `.jpg` 文件。
3. **按以下维度为每个场景打分（1-10 整数）**：
   - **aesthetic_beauty**（美感）：构图、光影、色彩
   - **credibility**（可信度）：真实感、物理逻辑
   - **impact**（冲击力）：视觉显著性、第一眼吸引力
   - **memorability**（记忆度）：独特符号、冯·雷斯托夫效应
   - **fun_interest**（趣味度）：参与感、娱乐价值
4. **分类场景类型**：TYPE-A Hook / TYPE-B Narrative / TYPE-C Aesthetic / TYPE-D Commercial
5. **计算加权分并筛选**：加权 ≥ 8.5 → MUST KEEP，≥ 7.0 → USABLE，< 7.0 → DISCARD
6. **将评分结果更新到 `scene_scores.json` 中每个场景的字段**
7. **将精选片段（MUST KEEP + USABLE）对应的 mp4 复制到 `scenes/best_shots/` 并按排名命名**
8. **生成分析报告** `<video_id>_complete_analysis.md`

##### ⚡ 大规模场景分批处理协议（>10 个场景时启用）

当场景数量超过 10 个时，**必须**使用分批分析模式。这不是建议，而是硬性要求——因为一次性处理过多场景时，AI 容易因上下文疲劳而跳过、抽样或给出模板化评分，导致分析质量崩塌。

**🚫 反抽样声明（Anti-Sampling Policy）**

> 每一个场景都是用户花了真金白银下载和切分的素材。抽样分析意味着用户会错过可能的最佳镜头——想象一下，被跳过的那个场景恰好是整个视频的高光时刻。因此：
> - **禁止**抽样、跳过、合并或"代表性选取"任何场景
> - **禁止**对未查看的场景给出评分（不看图就打分等于捏造数据）
> - **禁止**对多个场景使用相同的描述文字（每个镜头的画面内容不同，描述必然不同）
> - 如果因为上下文限制确实无法继续，应当**明确告知用户**已完成到哪个场景，让用户决定如何继续，而不是悄悄跳过

**分批规则：**
- 每个 batch 包含 **5-10 个场景**（根据总数均匀划分）
- 按场景编号顺序处理：Batch 1 = Scene 001-010，Batch 2 = Scene 011-020，以此类推

**每个 batch 执行流程：**
1. 使用 `view_file` 查看本批次所有帧图片
2. 逐帧分析，**每个场景必须包含**：
   - 📝 **唯一视觉描述**（1-2 句）：描述该帧画面中实际看到的具体内容（人物/物体/动作/环境/色调）。这是证明你真正查看了图片的证据——如果描述不出画面内容，说明没有认真看图
   - 🎯 五维评分（1-10 整数）+ 场景类型 + 加权分 + 筛选等级
3. 立即将本批次评分写入 `scene_scores.json`
4. 输出子报告 `batch_N_report.md`（N = 批次号），包含：
   - 本批次场景编号范围
   - 每个场景的评分摘要表格（含视觉描述列）
   - 本批次 MUST KEEP / USABLE / DISCARD 数量统计
5. **向用户汇报进度**："✅ Batch N/M 完成（场景 XXX-YYY），MUST KEEP: X 个，USABLE: Y 个。继续处理下一批..."

**全部 batch 完成后：**
1. **🔍 覆盖率校验**（必须执行）：
   - 列出 `frames/` 目录中的所有 `.jpg` 文件数量 = **应分析总数**
   - 统计 `scene_scores.json` 中已有评分的场景数量 = **实际完成数**
   - 输出校验结果："覆盖率：实际完成数/应分析总数 = XX%"
   - **覆盖率必须 = 100%**。如果不足，列出遗漏的场景编号并补充分析
2. 汇总所有子报告，生成完整分析报告 `<video_id>_complete_analysis.md`
3. 复制精选片段到 `scenes/best_shots/`
4. 确认最终报告输出完成后，删除所有 `batch_N_report.md` 子报告
5. 向用户输出最终摘要：总场景数、各等级分布、Top 5 精选镜头

#### 🅱️ API 模式（独立 CLI 运行用户）

如果你直接在终端运行脚本，需要配置视觉大模型 API：

```bash
# 设置 API 密钥（必需）
export VIDEO_ANALYZER_API_KEY="your-api-key"

# 可选：自定义端点和模型
export VIDEO_ANALYZER_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
export VIDEO_ANALYZER_MODEL="gemini-2.0-flash"

# 运行 AI 分析
cd ~/Downloads/video-analysis/<视频文件夹>
python3 <skill_dir>/scripts/ai_analyzer.py scene_scores.json --mode api
```

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                   VIDEO EXPERT ANALYZER v2.0                 │
└─────────────────────────────────────────────────────────────┘

第 1 阶段: 数据处理 (pipeline_enhanced.py)
1. 📥 下载视频              → video.mp4
2. 🎵 提取音频              → video.m4a
3. 🎞️  场景检测 (detect-content) → scenes/*.mp4
4. 🎤 智能字幕提取           → video.srt
   (B站API → 内嵌字幕 → RapidOCR → FunASR 四级降级)
5. 🖼️  帧提取               → frames/*.jpg
6. 📊 生成评分模板          → scene_scores.json

第 2 阶段: AI 视觉评分 (选择一种模式)
┌────────────────────────┬────────────────────────┐
│   🅰️ Agent 模式         │   🅱️ API 模式           │
│   宿主 AI 直接看图评分  │   远程调用视觉大模型    │
│   无需 API Key         │   需要 API Key          │
│   IDE/OpenClaw/Cursor  │   独立 CLI 运行          │
└────────────────────────┴────────────────────────┘
                         ↓
7. 🤖 真实视觉分析评分     → 基于画面内容的真实评分
8. 🧮 动态权重计算         → 根据类型计算加权得分
9. ⭐ 精选镜头筛选         → 复制到 scenes/best_shots/
10. 📄 生成完整报告        → *_complete_analysis.md
```

## 分析方法论

### Walter Murch 剪辑六法则

> **情感 Emotion > 故事 Story > 节奏 Rhythm > 视线追踪 Eye-trace > 2D平面 2D Plane > 3D空间 3D Space**

一个情感真挚但画面略抖的镜头，优于一个画面完美但内容空洞的镜头。

### 五维评分体系 (Five-Dimension Scoring)

| 维度 (Dimension) | 基础权重 | 评估要点 |
|-----------------|---------|---------|
| **Aesthetic Beauty** 美感 | 20% | 构图(三分法)、光影质感、色彩和谐度 |
| **Credibility** 可信度 | 20% | 表演自然度、物理逻辑、无出戏感 |
| **Impact** 冲击力 | 20% | 视觉显著性(Visual Saliency)、动态张力 |
| **Memorability** 记忆度 | 20% | 独特符号(Von Restorff Effect)、金句 |
| **Fun/Interest** 趣味度 | 20% | 参与感、娱乐价值、社交货币 |

### 动态权重系统（根据场景类型自动调整）

| 类型 (Type) | 权重分配 (Weighting) | 适用场景 (Application) |
|------------|---------------------|----------------------|
| **TYPE-A Hook** | IMPACT 40% + MEMORABILITY 30% + SYNC 20% | 开场钩子、高能时刻 |
| **TYPE-B Narrative** | CREDIBILITY 40% + MEMORABILITY 30% + AESTHETICS 20% | 叙事段落、情感表达 |
| **TYPE-C Aesthetic** | AESTHETICS 50% + SYNC 30% + IMPACT 20% | 空镜头、氛围营造 |
| **TYPE-D Commercial** | CREDIBILITY 40% + MEMORABILITY 40% + AESTHETICS 20% | 产品展示、商业广告 |

### 筛选决策规则

| 等级 (Level) | 中文释义 | 标准 (Criteria) | 用途 (Usage) |
|-------------|---------|----------------|-------------|
| 🌟 **MUST KEEP** | 强烈推荐保留 | 加权总分 > 8.5 或 单项 = 10 | 核心素材，极致长板 |
| 📁 **USABLE** | 可用素材 | 7.0 ≤ 加权总分 < 8.5 | 过渡素材，辅助叙事 |
| 🗑️ **DISCARD** | 建议舍弃 | 加权总分 < 7.0 或有瑕疵 | 建议舍弃 |

## 输出文件结构

```
{output_dir}/
└── {video_id}/
    ├── {video_id}.mp4                      # 完整视频 (Full Video)
    ├── {video_id}.m4a                      # 音频文件 (Audio)
    ├── {video_id}.srt                      # 字幕文件 (Subtitles)
    ├── {video_id}_transcript.txt           # 转录文本 (Transcript)
    ├── scene_scores.json                   # 完整评分数据（AI已填写）⭐
    ├── {video_id}_complete_analysis.md     # ⭐ 完整分析报告（中英双语）
    ├── scenes/                             # 场景片段 (Scene Clips)
    │   ├── {video_id}-Scene-001.mp4
    │   ├── {video_id}-Scene-002.mp4
    │   ├── ...
    │   └── best_shots/                     # ⭐ 精选片段（已复制）
    │       ├── 01_USABLE_xxx.mp4
    │       ├── 02_MUST_KEEP_xxx.mp4
    │       └── README.md                   # 双语说明文件
    └── frames/                             # 场景预览帧 (Preview Frames)
        ├── {video_id}-Scene-001.jpg
        └── ...
```

## 完整分析报告内容

生成的 `*_complete_analysis.md` 包含中英双语术语对照：

### 1. 统计概览 (Statistics Overview)
- 各等级场景数量统计（带中文释义）
- 各维度平均分（英文术语 + 中文释义）

### 2. 场景排名表 (Scene Rankings)
- 按加权分数排序
- 显示类型（英文 + 中文）
- 筛选建议（英文 + 中文）
- 核心优势

### 3. 术语对照表 (Terminology Reference)
完整的专业术语中英对照表，包含：
- 英文术语
- 中文释义
- 详细说明

### 4. 各场景详细评估（每个场景包含）
- **基础信息**: 类型分类（双语）、加权得分、筛选建议（双语）
- **内容描述**: AI 自动生成的场景描述
- **五维评分表格**: 
  | 英文术语 | 中文释义 | 得分 | 权重贡献 |
- **入选/淘汰理由**: AI 生成的理论依据
- **剪辑建议**: AI 生成的使用建议

### 5. 精选片段推荐 (Best Shots Recommendations)
- 入选精选文件夹的片段列表（双语）
- 各类别最佳镜头：
  - 最佳 Hook 候选 (Best Hook Candidate)
  - 最佳视觉 (Best Visual)
  - 最佳可信度 (Best Credibility)
  - 最佳记忆度 (Best Memorability)

### 6. 整体影片评价 (Overall Assessment)
- 综合评分
- 评价结论（双语）
- 优势分析（各维度详细评价）
- 改进建议（专业术语 + 中文解释）
- 使用场景建议（社交媒体/产品展示/品牌宣传/广告投放）

## 使用示例

### 基础分析

```bash
# 配置输出目录（首次）
python3 scripts/pipeline_enhanced.py --setup

# 分析视频
python3 scripts/pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

# 进入输出目录运行 AI 分析
cd ~/Downloads/video-analysis/BV1xxxxx
python3 <skill_dir>/scripts/ai_analyzer.py scene_scores.json
```

### 快速分析（自定义场景检测阈值）

```bash
python3 scripts/pipeline_enhanced.py URL --scene-threshold 20
```

### 调整精选阈值

```bash
python3 scripts/ai_analyzer.py scene_scores.json 6.5  # 阈值 6.5
```

## 命令参考

### pipeline_enhanced.py

| 选项 | 说明 |
|------|------|
| `--setup` | 配置输出目录 |
| `-o, --output` | 指定输出目录 |
| `--scene-threshold` | 场景检测阈值 (默认27) |
| `--best-threshold` | 精选阈值 (默认7.5) |

### ai_analyzer.py

| 参数 | 说明 |
|------|------|
| `scene_scores.json` | 评分文件路径 |
| `--mode api` | API 模式（需设置 `VIDEO_ANALYZER_API_KEY`）|
| `--mode agent` | Agent 模式（生成模板供宿主 AI 填写）|

| 环境变量 | 说明 |
|------|------|
| `VIDEO_ANALYZER_API_KEY` | 视觉大模型 API 密钥（API 模式必需）|
| `VIDEO_ANALYZER_BASE_URL` | API 端点（默认 Gemini） |
| `VIDEO_ANALYZER_MODEL` | 模型名称（默认 `gemini-2.0-flash`）|

## 依赖要求

```bash
# 系统依赖（安装 ffmpeg）
brew install ffmpeg               # macOS
winget install ffmpeg             # Windows
sudo apt install ffmpeg           # Ubuntu/Debian

# 一键安装所有 Python 依赖
pip3 install -r requirements.txt

# 或手动安装核心依赖
pip3 install yt-dlp scenedetect[opencv] requests funasr modelscope torch torchaudio

# 可选依赖
pip3 install openai              # API 模式评分
pip3 install rapidocr-onnxruntime # 烧录字幕 OCR 检测
```

### 环境检测

```bash
# 一键检测所有依赖是否就绪
python3 scripts/check_environment.py
```

## 平台特定说明

### 抖音视频下载

由于抖音的反爬机制，yt-dlp 无法直接下载抖音视频。本工具集成了专用的抖音下载器，可以：

- ✅ 自动识别抖音链接（支持 `douyin.com` 和 `v.douyin.com` 短链接）
- ✅ 自动提取视频信息（标题、作者）
- ✅ 下载无水印视频
- ✅ 自动提取音频用于转录

**支持的抖音链接格式：**
- `https://www.douyin.com/video/xxxxx`
- `https://www.douyin.com/jingxuan?modal_id=xxxxx`
- `https://v.douyin.com/xxxxx` (短链接)

**抖音下载实现原理：**
1. 使用移动端 User-Agent 访问页面
2. 从页面 HTML 中提取 `RENDER_DATA` JSON 数据
3. 解析视频直链地址（自动替换 `playwm` 为 `play` 获取无水印版本）
4. 使用正确的 Referer 头下载视频

**给 Agent 的硬性规则：**
- 处理抖音链接时，**不要**先尝试网页登录、浏览器 cookie、WSL 读取宿主浏览器 cookie 这条路线
- 对公开可访问的抖音/分享链接，优先直接运行本地脚本：
  - `python3 scripts/pipeline_enhanced.py "<抖音链接>"`
  - 或 `python3 scripts/download_douyin.py "<抖音链接>" ./video.mp4`
- 如果 Agent 提示“抖音网页版需要登录”或“WSL 无法读取 cookie”，说明它走错路了，应切回本地下载脚本
- 优先使用用户从抖音 App 复制的分享短链（`https://v.douyin.com/...`）；长链也支持

## Troubleshooting

### 终端命令卡顿
如果在 IDE 中执行 `cp` 或 Python 脚本时终端无响应，这通常是 IDE 终端代理的问题。解决方案：
- **方案 A**: 打开 macOS 自带 Terminal.app 手动运行命令
- **方案 B**: 使用 `copy_by_index.py` 脚本通过 JSON 索引批量复制文件

### FunASR 首次下载慢
FunASR 首次运行需下载约 2-3GB 的 Paraformer 模型。如果下载缓慢：
- 设置镜像: `export MODELSCOPE_CACHE=~/.cache/modelscope`
- 或使用 B站 API 字幕（无需本地模型，速度极快）

### Agent 模式评分注意事项
- 必须使用**具备视觉能力**的多模态模型（参见「模型兼容性」表）
- 纯文本模型（如 GPT-3.5、Claude Haiku）**无法**执行 Agent 模式评分
- 建议每批查看 3-5 张帧图片，避免单次加载过多

### 抖音链接在 WSL / 远程环境报 cookie 错误
如果 Agent 在 WSL、远程容器或无桌面浏览器环境里说“无法读取抖音链接，因为网页版需要登录且 cookie 读不到”，按下面处理：
- 不要继续折腾网页登录
- 直接运行 `scripts/pipeline_enhanced.py` 或 `scripts/download_douyin.py`
- 如果用户给的是长链，优先让用户从抖音 App 重新复制一次分享链接，拿到 `v.douyin.com` 短链后再跑
- 只有私密、删除、地区受限或已失效内容，才可能真的无法直接下载

---

## 更新日志

### v2.2.0 (2026-03-24)
- ⚡ **大规模场景分批处理协议**：>10 个场景时强制分批（5-10个/batch），每批输出子报告 + 进度汇报，全部完成后汇总并清理
- 🚫 **反抽样策略**：禁止跳过/合并场景，强制输出唯一视觉描述作为查看证据
- 🔍 **100% 覆盖率校验**：完成后校验帧数 vs 已评分数，覆盖率必须 = 100%
- 📝 **重写 description 触发词**：增加 8 个中文关键词 + 小红书平台
- 🌐 补充 Windows/Linux 的 ffmpeg 安装说明
- 🗑️ 删除过时的 QUICKSTART.md、清理运行日志
- ⚠️ **模型兼容性发现**：Kimi 2.5 在 >30 镜头时出现偷懒行为（疑似服务端工具调用次数限制）；GPT 5.4 可完成 127 镜头连续分析（预热后 11 分 48 秒）；Gemini/Opus 尚未测试

### v2.1.0 (2026-02-27)
- ✅ **智能字幕提取**：对齐 video-copy-analyzer，支持 B站API→内嵌→RapidOCR→FunASR 四级降级
- ✅ **新增小红书支持**：集成 `xiaohongshu_downloader.py`
- ✅ **新增 `requirements.txt`**：一键安装所有依赖
- ✅ **新增模型兼容性矩阵**：明确不同模型的适用模式
- ✅ **重写 `check_environment.py`**：检测 v2.1 实际依赖
- ✅ **清理废弃文件**：移除旧版 pipeline、Whisper 转录等6个废弃脚本
- ✅ **新增 Troubleshooting 章节**

### v2.0.0 (2026-02-27)
- ✅ **重写 AI 评分系统**：移除假数据模拟，接入真实视觉大模型
- ✅ **双路径评分**：Agent 模式（宿主 AI 直接看图）+ API 模式（远程调用）
- ✅ **修复场景检测**：`detect-adaptive` → `detect-content`，镜头切分更精准
- ✅ 将语音转录引擎从 Whisper 替换为 FunASR (Paraformer-zh)
- ✅ 中文场景转录速度大幅提升（10分钟音频约22秒完成）
- ✅ 移除 `--whisper-model` 参数（FunASR 使用固定 paraformer-zh 模型）
- ✅ 内置 VAD 自动分段 + 标点恢复

### v1.4.0 (2026-02-06)
- ✅ 新增抖音视频下载支持
- ✅ 自动识别抖音链接并切换下载方式
- ✅ 支持抖音短链接和长链接
- ✅ 自动获取无水印视频

### v1.3.0 (2026-02-05)
- ✅ 新增中英双语术语对照
- ✅ 所有专业术语附中文释义
- ✅ 报告中的术语表格双语显示

### v1.2.0 (2026-02-05)
- ✅ 新增 AI 自动分析功能
- ✅ 动态权重评分系统
- ✅ 自动生成完整分析报告
- ✅ 自动复制精选镜头

### v1.1.0 (2026-02-05)
- ✅ 新增可配置输出目录功能
- ✅ 精选片段自动保存
- ✅ 生成详细分析报告模板

### v1.0.0 (2026-02-05)
- 初始版本
- 基础视频分析功能

---

*基于 Walter Murch 剪辑六法则 (Walter Murch's Six Rules of Editing)*  
*AI 自动评分系统 (AI Automatic Scoring System)*  
*动态权重算法 (Dynamic Weighting Algorithm)*  
*中英双语术语对照 (Bilingual Terminology Reference)*
