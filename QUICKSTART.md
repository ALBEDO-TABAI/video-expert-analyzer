# Video Expert Analyzer - Quick Reference

## One-Line Commands

```bash
# Basic analysis
python3 Skills/video-expert-analyzer/scripts/pipeline.py URL -o output/

# Fast mode (quick draft)
python3 Skills/video-expert-analyzer/scripts/pipeline.py URL -o output/ --whisper-model tiny

# High quality
python3 Skills/video-expert-analyzer/scripts/pipeline.py URL -o output/ --whisper-model large

# Check environment
python3 Skills/video-expert-analyzer/scripts/check_environment.py

# Score scenes (after manual scoring)
python3 Skills/video-expert-analyzer/scripts/scoring_helper.py output/scene_scores.json calculate

# Generate ranking report
python3 Skills/video-expert-analyzer/scripts/scoring_helper.py output/scene_scores.json rank

# Copy best shots
python3 Skills/video-expert-analyzer/scripts/scoring_helper.py output/scene_scores.json best 7.0
```

## Directory Structure

```
Skills/video-expert-analyzer/
├── README.md                      # Full documentation
├── SKILL.md                       # Claude skill definition
├── scripts/
│   ├── pipeline.py                # Main orchestration script
│   ├── transcribe_audio.py        # Standalone transcription
│   ├── check_environment.py       # Dependency checker
│   └── scoring_helper.py          # Scoring utilities
└── templates/
    └── report_template.md         # Analysis report template
```

## Typical Workflow

1. **Setup**
   ```bash
   python3 Skills/video-expert-analyzer/scripts/check_environment.py
   ```

2. **Run Pipeline**
   ```bash
   python3 Skills/video-expert-analyzer/scripts/pipeline.py \
     https://www.bilibili.com/video/BV1xxxxx \
     -o Folders/my-analysis/
   ```

3. **Review Outputs**
   - Video: `Folders/my-analysis/{video_id}.mp4`
   - Transcript: `Folders/my-analysis/{video_id}_transcript.txt`
   - Scenes: `Folders/my-analysis/scenes/*.mp4`
   - Frames: `Folders/my-analysis/frames/*.jpg`

4. **Score Scenes** (with Claude's help)
   ```
   Ask Claude: "Score all scenes in Folders/my-analysis/frames/
   using the 5 criteria and update scene_scores.json"
   ```

5. **Generate Reports**
   ```bash
   python3 Skills/video-expert-analyzer/scripts/scoring_helper.py \
     Folders/my-analysis/scene_scores.json rank
   ```

6. **Extract Best Shots**
   ```bash
   python3 Skills/video-expert-analyzer/scripts/scoring_helper.py \
     Folders/my-analysis/scene_scores.json best 7.0
   ```

## Common Use Cases

### Case 1: Competitor Analysis
```bash
# Download and analyze competitor video
python3 Skills/video-expert-analyzer/scripts/pipeline.py \
  COMPETITOR_URL -o analysis/competitor/

# Ask Claude to analyze
"Analyze the transcript and identify: 1) value propositions,
2) content strategy, 3) viral elements, 4) areas we can improve upon"
```

### Case 2: Content Quality Check
```bash
# Analyze your own video
python3 Skills/video-expert-analyzer/scripts/pipeline.py \
  YOUR_VIDEO_URL -o analysis/my-video/

# Score and identify improvements
"Score all scenes, identify the weakest ones, and suggest
specific improvements for composition, lighting, and impact"
```

### Case 3: Social Media Content Extraction
```bash
# Extract scenes
python3 Skills/video-expert-analyzer/scripts/pipeline.py \
  VIDEO_URL -o analysis/social-clips/

# Get best shots
python3 Skills/video-expert-analyzer/scripts/scoring_helper.py \
  analysis/social-clips/scene_scores.json best 8.0

# Best scenes are now in analysis/social-clips/best_shots/
```

### Case 4: Transcription Only
```bash
# Just transcribe (no scene analysis)
python3 Skills/video-expert-analyzer/scripts/transcribe_audio.py \
  video.mp4 output.srt medium auto cpu
```

## Scoring Quick Reference

| Criterion | 9-10 | 7-8 | 5-6 | 1-4 |
|-----------|------|-----|-----|-----|
| **Aesthetic** | Professional, striking | Well-composed | Acceptable | Poor quality |
| **Credibility** | Highly authentic | Believable | Somewhat staged | Fake |
| **Impact** | Stops you | Grabs attention | Noticeable | Bland |
| **Memorability** | Unforgettable | Distinctive | Somewhat memorable | Generic |
| **Fun/Interest** | Highly entertaining | Engaging | Mildly interesting | Boring |

## Parameters Cheat Sheet

### Whisper Models
- `tiny` - Fastest, lowest accuracy (good for quick preview)
- `base` - Fast, decent accuracy
- `small` - Balanced
- `medium` - **Recommended** - Best quality/speed tradeoff
- `large` - Slowest, highest accuracy

### Scene Thresholds
- `20-25` - High sensitivity (more scenes)
- `27` - **Default** - Balanced
- `35-40` - Low sensitivity (fewer scenes)

### Best Shot Thresholds
- `8.0+` - Exceptional scenes only
- `7.0` - **Recommended** - High quality scenes
- `6.0` - Include good scenes

## Integration with Claude

### Ask Claude to:

**Analyze transcript:**
> "Analyze the transcript at {path} and identify the key value propositions, emotional triggers, and narrative structure"

**Score scenes:**
> "Review all frames in {path}/frames/ and score each scene using the 5 criteria (1-10). Save results to scene_scores.json"

**Generate report:**
> "Create a comprehensive analysis report using the template, including scene scores, transcript insights, and recommendations"

**Strategy insights:**
> "Based on this video analysis, suggest 3 ways we could improve our own content strategy"

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Download fails | Check URL format, try `--cookies-from-browser` |
| No scenes detected | Lower `--scene-threshold` to 20-25 |
| Too many scenes | Raise `--scene-threshold` to 35-40 |
| Poor transcription | Use larger Whisper model |
| Out of memory | Use smaller Whisper model (tiny/base) |
| Slow transcription | Use GPU or smaller model |

## File Outputs Reference

| Extension | Purpose | Tool |
|-----------|---------|------|
| `.mp4` | Video files | yt-dlp / scenedetect |
| `.m4a` | Audio for transcription | yt-dlp |
| `.srt` | Subtitles with timestamps | whisper |
| `.txt` | Plain text transcript | whisper |
| `.json` | Scene scores and data | pipeline |
| `.md` | Reports and documentation | scoring_helper |
| `.jpg` | Scene preview frames | ffmpeg |

## Performance Tips

1. **Use smaller models for iteration** - Use `tiny` or `base` while testing
2. **Skip scene extraction if not needed** - Add `--no-extract-scenes`
3. **Process shorter videos first** - Test setup on 30-second clips
4. **Cache videos** - Keep downloaded videos for re-analysis
5. **Use GPU if available** - 5-10x faster transcription

## Next Steps After Analysis

1. ✅ Review transcript for key messages
2. ✅ Score all scenes (1-10 on each criterion)
3. ✅ Identify best shots (≥7.0 threshold)
4. ✅ Generate ranking report
5. ✅ Create content strategy document
6. ✅ Extract clips for social media
7. ✅ Share insights with team

---

**For detailed documentation, see README.md or SKILL.md**
