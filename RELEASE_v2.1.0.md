# v2.1.0 Release Notes

## 🚀 What's New

### 🎤 Smart Subtitle Extraction (智能字幕提取)
Aligned with `video-copy-analyzer` skill — now supports **4-tier fallback**:
1. **Bilibili API** — Fastest, grabs platform subtitles directly
2. **Embedded Subtitles** — Extracts subtitle streams via FFmpeg
3. **Burned Subtitle OCR** — Detects and extracts burned-in subtitles via RapidOCR
4. **FunASR Speech-to-Text** — Local Chinese ASR with VAD + punctuation recovery

### 🤖 Model Compatibility Matrix (模型兼容性矩阵)
Clear guidance on which AI models work with each scoring mode:

| Model | Agent Mode | API Mode |
|-------|-----------|---------|
| Gemini 3.0 Flash | ✅ Recommended | ✅ Recommended |
| Gemini 3.0 Pro | ✅ Recommended | ✅ Supported |
| Kimi 2.5 | ✅ Supported | ✅ Supported |
| Claude (Sonnet/Opus) | ✅ Supported | ❌ |

### 📱 Xiaohongshu Support (小红书支持)
Added `xiaohongshu_downloader.py` for downloading videos from Xiaohongshu (Little Red Book).

### 📦 One-Click Dependencies (一键安装依赖)
New `requirements.txt` — install everything with:
```bash
pip3 install -r requirements.txt
```

### 🔍 Environment Check (环境检测)
Completely rewritten `check_environment.py` — now detects all v2.1 dependencies including FunASR, scenedetect, Apple MPS GPU support, etc.

### 🛠️ Troubleshooting Section
New troubleshooting guide in SKILL.md covering:
- IDE terminal freezing workarounds
- FunASR model download issues
- Agent mode scoring best practices

## 🧹 Cleanup

Removed 6 deprecated files:
- `scripts/pipeline.py` (replaced by `pipeline_enhanced.py`)
- `scripts/scoring_helper.py` (replaced by `scoring_helper_enhanced.py`)
- `scripts/transcribe_audio.py` (Whisper, replaced by FunASR)
- `scripts/douyin_downloader.py` (replaced by `download_douyin.py`)
- `xhs_debug.html` (debug artifact)
- `analyze.py` (unused entry point)

## 📝 Changed Files

| File | Change |
|------|--------|
| `SKILL.md` | +Model compatibility +Xiaohongshu +Troubleshooting +v2.1 changelog |
| `README.md` | Full rewrite from v1.3 to v2.1 |
| `requirements.txt` | **NEW** — all dependencies |
| `.env.example` | Rewritten (removed Whisper config) |
| `scripts/check_environment.py` | Rewritten for v2.1 deps |
| `scripts/pipeline_enhanced.py` | Transcription → smart subtitle extraction |
| `scripts/extract_subtitle_funasr.py` | **NEW** — 4-tier subtitle extraction |
| `scripts/fetch_bilibili_subtitle.py` | **NEW** — Bilibili API subtitles |
| `scripts/download_douyin.py` | **NEW** — cleaner Douyin downloader |

## ⬆️ Upgrade from v2.0

```bash
pip3 install -r requirements.txt
python3 scripts/check_environment.py
```

**Full Changelog**: v2.0.0...v2.1.0
