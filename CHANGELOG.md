# Changelog

All notable changes to the Video Expert Analyzer skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-05

### Added
- Initial release of Video Expert Analyzer skill
- Master pipeline script (`pipeline.py`) for end-to-end video analysis
- Video and audio download from Bilibili/YouTube using yt-dlp
- Automatic scene detection and splitting using PySceneDetect
- Speech-to-text transcription using OpenAI Whisper
- Representative frame extraction from each scene
- Scene scoring system with 5 evaluation criteria
- Scoring helper utilities (`scoring_helper.py`)
- Transcription script (`transcribe_audio.py`)
- Environment check script (`check_environment.py`)
- Comprehensive report template
- Full documentation suite (README, SKILL, QUICKSTART, SUMMARY)
- Example configuration file (.env.example)
- Command-line interface with help text
- JSON export capability
- Ranking report generation
- Best shots identification and copying

### Features
- Supports Bilibili and YouTube videos
- Configurable Whisper models (tiny, base, small, medium, large)
- Adjustable scene detection threshold
- Optional scene extraction (speed optimization)
- Robust error handling and validation
- Cross-platform path management
- Progress tracking and status reporting
- Multiple output formats (MP4, M4A, SRT, TXT, JSON, MD, JPG)

### Documentation
- README.md: Full documentation (8.8KB)
- SKILL.md: Claude Code skill definition (10KB)
- QUICKSTART.md: Quick reference guide (6.7KB)
- SUMMARY.md: Project overview (8.3KB)
- Templates for analysis reports
- Inline code documentation

### Testing
- Tested with real Bilibili video (BV1v3zFBWEvj)
- Validated Chinese language transcription
- Confirmed scene detection (9 scenes)
- Verified scoring workflow
- Tested all CLI commands

### Known Limitations
- CUDA not available on macOS (CPU transcription only)
- Premium content may require authentication cookies
- Large videos can be memory-intensive
- Mixed-language content may confuse transcription

## [Unreleased]

### Planned for v1.1.0
- [ ] Batch processing for multiple videos
- [ ] Improved scoring automation
- [ ] Additional analysis frameworks
- [ ] Export formats for video editors
- [ ] API integration options

### Planned for v2.0.0
- [ ] Web interface
- [ ] Cloud storage integration
- [ ] Real-time processing
- [ ] Advanced analytics (sentiment, topics)
- [ ] Multi-language UI

---

## Version Guidelines

### Major Version (X.0.0)
- Breaking changes to API or CLI
- Major architectural changes
- Significant new features

### Minor Version (0.X.0)
- New features (backward compatible)
- Significant improvements
- New analysis frameworks

### Patch Version (0.0.X)
- Bug fixes
- Documentation updates
- Performance improvements
- Minor enhancements

---

## Contributing

To add entries:
1. Add changes under [Unreleased]
2. On release, move to new version section
3. Follow Keep a Changelog format
4. Include date in YYYY-MM-DD format

---

**Maintained by:** Claude Code Community
**Last Updated:** 2026-02-05
