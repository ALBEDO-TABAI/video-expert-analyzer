#!/usr/bin/env python3
"""
Video Expert Analyzer Pipeline
End-to-end video analysis: download, scene detection, transcription, and scoring preparation
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class VideoAnalysisPipeline:
    """Orchestrates the complete video analysis workflow"""

    def __init__(self, url: str, output_dir: str,
                 whisper_model: str = "medium",
                 scene_threshold: float = 27.0,
                 extract_scenes: bool = True):
        """
        Initialize the pipeline

        Args:
            url: Video URL (Bilibili/YouTube)
            output_dir: Directory to save all outputs
            whisper_model: Whisper model size (tiny/base/small/medium/large)
            scene_threshold: Scene detection threshold (lower=more scenes)
            extract_scenes: Whether to extract individual scene clips
        """
        self.url = url
        self.output_dir = Path(output_dir).resolve()
        self.whisper_model = whisper_model
        self.scene_threshold = scene_threshold
        self.extract_scenes = extract_scenes

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Extract video ID from URL
        self.video_id = self._extract_video_id(url)

        # Define output paths
        self.video_path = self.output_dir / f"{self.video_id}.mp4"
        self.audio_path = self.output_dir / f"{self.video_id}.m4a"
        self.srt_path = self.output_dir / f"{self.video_id}.srt"
        self.transcript_path = self.output_dir / f"{self.video_id}_transcript.txt"
        self.scenes_dir = self.output_dir / "scenes"
        self.frames_dir = self.output_dir / "frames"
        self.scores_path = self.output_dir / "scene_scores.json"
        self.report_path = self.output_dir / f"{self.video_id}_analysis_report.md"

        # Results tracking
        self.results = {
            "video_id": self.video_id,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "initialized",
            "steps_completed": []
        }

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from URL"""
        # Bilibili: BV number
        if "bilibili.com" in url:
            if "/video/" in url:
                parts = url.split("/video/")[1].split("/")[0].split("?")[0]
                return parts

        # YouTube: video ID
        if "youtube.com" in url or "youtu.be" in url:
            if "v=" in url:
                return url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]

        # Fallback: use timestamp
        return f"video_{int(datetime.now().timestamp())}"

    def run(self) -> Dict:
        """Execute the complete pipeline"""
        print("=" * 60)
        print("🎬 VIDEO EXPERT ANALYZER PIPELINE")
        print("=" * 60)
        print(f"Video URL: {self.url}")
        print(f"Output Dir: {self.output_dir}")
        print(f"Video ID: {self.video_id}")
        print("=" * 60)

        try:
            # Step 1: Download video
            self._step_download_video()

            # Step 2: Download audio (for transcription)
            self._step_download_audio()

            # Step 3: Scene detection
            scene_info = self._step_scene_detection()

            # Step 4: Transcription
            transcript_info = self._step_transcription()

            # Step 5: Extract frames for scoring
            self._step_extract_frames(scene_info)

            # Step 6: Prepare scoring structure
            self._step_prepare_scoring(scene_info)

            # Step 7: Generate report
            self._step_generate_report(scene_info, transcript_info)

            self.results["status"] = "completed"
            print("\n" + "=" * 60)
            print("✅ PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 60)

            return self.results

        except Exception as e:
            self.results["status"] = "failed"
            self.results["error"] = str(e)
            print(f"\n❌ PIPELINE FAILED: {e}")
            raise

    def _step_download_video(self):
        """Step 1: Download video using yt-dlp"""
        print("\n📥 Step 1: Downloading video...")

        if self.video_path.exists():
            print(f"   ⚠️  Video already exists: {self.video_path}")
            self.results["steps_completed"].append("download_video")
            return

        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", str(self.video_path),
            self.url
        ]

        subprocess.run(cmd, check=True)

        if not self.video_path.exists():
            raise RuntimeError("Video download failed - file not found")

        file_size = self.video_path.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ Video downloaded: {file_size:.2f} MB")

        self.results["video_path"] = str(self.video_path)
        self.results["video_size_mb"] = round(file_size, 2)
        self.results["steps_completed"].append("download_video")

    def _step_download_audio(self):
        """Step 2: Download audio for transcription"""
        print("\n🎵 Step 2: Downloading audio...")

        if self.audio_path.exists():
            print(f"   ⚠️  Audio already exists: {self.audio_path}")
            self.results["steps_completed"].append("download_audio")
            return

        cmd = [
            "yt-dlp",
            "-f", "bestaudio[ext=m4a]/bestaudio",
            "--extract-audio",
            "--audio-format", "m4a",
            "-o", str(self.audio_path),
            self.url
        ]

        subprocess.run(cmd, check=True)

        if not self.audio_path.exists():
            raise RuntimeError("Audio download failed - file not found")

        file_size = self.audio_path.stat().st_size / 1024  # KB
        print(f"   ✅ Audio downloaded: {file_size:.2f} KB")

        self.results["audio_path"] = str(self.audio_path)
        self.results["steps_completed"].append("download_audio")

    def _step_scene_detection(self) -> Dict:
        """Step 3: Detect and split scenes using PySceneDetect"""
        print("\n🎞️  Step 3: Detecting scenes...")

        self.scenes_dir.mkdir(exist_ok=True)

        # Run scene detection
        cmd = [
            "scenedetect",
            "-i", str(self.video_path),
            "-o", str(self.scenes_dir),
            "detect-adaptive",
            "-t", str(self.scene_threshold)
        ]

        if self.extract_scenes:
            cmd.append("split-video")

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse output to get scene count
        output = result.stdout + result.stderr
        scene_count = 0

        for line in output.split("\n"):
            if "Detected" in line and "scenes" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "Detected" and i + 1 < len(parts):
                        try:
                            scene_count = int(parts[i + 1])
                            break
                        except ValueError:
                            pass

        # Count actual scene files if extracted
        if self.extract_scenes:
            scene_files = sorted(self.scenes_dir.glob("*.mp4"))
            scene_count = len(scene_files)

        print(f"   ✅ Detected {scene_count} scenes")

        scene_info = {
            "scene_count": scene_count,
            "scenes_dir": str(self.scenes_dir) if self.extract_scenes else None,
            "threshold": self.scene_threshold
        }

        self.results["scene_detection"] = scene_info
        self.results["steps_completed"].append("scene_detection")

        return scene_info

    def _step_transcription(self) -> Dict:
        """Step 4: Transcribe audio using Whisper"""
        print("\n🎤 Step 4: Transcribing audio...")

        if self.srt_path.exists():
            print(f"   ⚠️  Transcription already exists: {self.srt_path}")
            self.results["steps_completed"].append("transcription")
            return {"status": "skipped"}

        import whisper
        import torch

        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            print(f"   🚀 Using CUDA acceleration")
        else:
            print(f"   ⚠️  Using CPU (slower)")

        # Load model
        print(f"   📥 Loading Whisper {self.whisper_model} model...")
        model = whisper.load_model(self.whisper_model, device=device)

        # Extract audio to WAV for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name

        try:
            # Convert to WAV
            cmd = [
                "ffmpeg", "-y", "-i", str(self.audio_path),
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                wav_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Transcribe
            print(f"   🎤 Transcribing...")
            result = model.transcribe(wav_path, task="transcribe")

            # Generate SRT
            self._write_srt(result["segments"], self.srt_path)

            # Generate plain text transcript
            self._write_transcript(result["segments"], self.transcript_path)

            print(f"   ✅ Transcription complete")
            print(f"      Language: {result.get('language', 'unknown')}")
            print(f"      Segments: {len(result['segments'])}")

            transcript_info = {
                "language": result.get("language", "unknown"),
                "segment_count": len(result["segments"]),
                "srt_path": str(self.srt_path),
                "transcript_path": str(self.transcript_path)
            }

            self.results["transcription"] = transcript_info
            self.results["steps_completed"].append("transcription")

            return transcript_info

        finally:
            # Cleanup temp file
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def _write_srt(self, segments: List[Dict], output_path: Path):
        """Write SRT subtitle file"""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    def _write_transcript(self, segments: List[Dict], output_path: Path):
        """Write plain text transcript"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== Video Transcript ===\n\n")
            f.write("=== Full Text ===\n\n")
            full_text = " ".join([seg["text"].strip() for seg in segments])
            f.write(full_text + "\n\n")
            f.write("=== Timestamped Text ===\n\n")
            for seg in segments:
                start = self._format_timestamp(seg["start"])
                end = self._format_timestamp(seg["end"])
                f.write(f"[{start} --> {end}]\n")
                f.write(f"{seg['text'].strip()}\n\n")

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _step_extract_frames(self, scene_info: Dict):
        """Step 5: Extract representative frames from each scene"""
        print("\n🖼️  Step 5: Extracting frames from scenes...")

        if not self.extract_scenes or scene_info["scene_count"] == 0:
            print("   ⚠️  Scene extraction disabled or no scenes found")
            return

        self.frames_dir.mkdir(exist_ok=True)

        scene_files = sorted(self.scenes_dir.glob("*.mp4"))

        for scene_file in scene_files:
            # Extract scene number from filename
            scene_name = scene_file.stem
            frame_path = self.frames_dir / f"{scene_name}.jpg"

            if frame_path.exists():
                continue

            # Extract first frame
            cmd = [
                "ffmpeg", "-i", str(scene_file),
                "-vf", "select=eq(n\\,0)",
                "-vframes", "1",
                str(frame_path),
                "-y"
            ]
            subprocess.run(cmd, check=True, capture_output=True)

        frame_count = len(list(self.frames_dir.glob("*.jpg")))
        print(f"   ✅ Extracted {frame_count} frames")

        self.results["frames_dir"] = str(self.frames_dir)
        self.results["frame_count"] = frame_count
        self.results["steps_completed"].append("extract_frames")

    def _step_prepare_scoring(self, scene_info: Dict):
        """Step 6: Prepare scene scoring structure"""
        print("\n📊 Step 6: Preparing scene scoring structure...")

        if not self.extract_scenes or scene_info["scene_count"] == 0:
            print("   ⚠️  No scenes to score")
            return

        scene_files = sorted(self.scenes_dir.glob("*.mp4"))

        # Create scoring template
        scoring_data = {
            "video_id": self.video_id,
            "url": self.url,
            "total_scenes": len(scene_files),
            "evaluation_criteria": {
                "aesthetic_beauty": "Composition, lighting, color harmony (1-10)",
                "credibility": "Realism, authenticity, believability (1-10)",
                "impact": "Visual power, attention-grabbing quality (1-10)",
                "memorability": "Uniqueness, striking elements (1-10)",
                "fun_interest": "Engagement level, entertainment value (1-10)"
            },
            "scenes": [],
            "instructions": "This file requires manual scoring. For each scene, view the video/frame and assign scores (1-10) for each criterion."
        }

        for i, scene_file in enumerate(scene_files, 1):
            scene_data = {
                "scene_number": i,
                "filename": scene_file.name,
                "file_path": str(scene_file),
                "frame_path": str(self.frames_dir / f"{scene_file.stem}.jpg") if self.frames_dir.exists() else None,
                "description": "TODO: Add description after viewing",
                "scores": {
                    "aesthetic_beauty": 0,
                    "credibility": 0,
                    "impact": 0,
                    "memorability": 0,
                    "fun_interest": 0
                },
                "notes": "TODO: Add notes"
            }
            scoring_data["scenes"].append(scene_data)

        # Save scoring template
        with open(self.scores_path, "w", encoding="utf-8") as f:
            json.dump(scoring_data, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Scoring template created: {self.scores_path}")
        print(f"   📝 Manual scoring required for {len(scene_files)} scenes")

        self.results["scoring_template"] = str(self.scores_path)
        self.results["steps_completed"].append("prepare_scoring")

    def _step_generate_report(self, scene_info: Dict, transcript_info: Dict):
        """Step 7: Generate analysis report"""
        print("\n📄 Step 7: Generating analysis report...")

        report = f"""# Video Analysis Report

## Video Information
- **Video ID**: {self.video_id}
- **URL**: {self.url}
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Pipeline Results

### 1. Video Download
- **Video Path**: `{self.video_path.name}`
- **Video Size**: {self.results.get('video_size_mb', 'N/A')} MB
- **Audio Path**: `{self.audio_path.name}`

### 2. Scene Detection
- **Total Scenes**: {scene_info.get('scene_count', 0)}
- **Detection Threshold**: {scene_info.get('threshold', 'N/A')}
- **Scenes Directory**: `{self.scenes_dir.name}/`

### 3. Transcription
- **Language**: {transcript_info.get('language', 'N/A')}
- **Segments**: {transcript_info.get('segment_count', 0)}
- **SRT File**: `{self.srt_path.name}`
- **Transcript File**: `{self.transcript_path.name}`

### 4. Frame Extraction
- **Frames Extracted**: {self.results.get('frame_count', 0)}
- **Frames Directory**: `{self.frames_dir.name}/`

### 5. Scene Scoring
- **Status**: Template created (requires manual scoring)
- **Scoring File**: `{self.scores_path.name}`

## Next Steps

1. **Review extracted frames** in `{self.frames_dir.name}/`
2. **Complete scene scoring** in `{self.scores_path.name}`
3. **Analyze transcript** in `{self.transcript_path.name}`
4. **Identify best scenes** based on scores
5. **Create final content analysis report**

## File Structure

```
{self.output_dir.name}/
├── {self.video_id}.mp4                    # Full video
├── {self.video_id}.m4a                    # Audio file
├── {self.video_id}.srt                    # Subtitles
├── {self.video_id}_transcript.txt         # Text transcript
├── scene_scores.json                      # Scoring template
├── {self.video_id}_analysis_report.md     # This report
├── scenes/                                # Individual scene clips
├── frames/                                # Scene preview frames
└── best_shots/                            # (To be created after scoring)
```

## Notes

This report was generated automatically by the Video Expert Analyzer Pipeline.
Manual review and scoring are required to complete the analysis.
"""

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"   ✅ Report generated: {self.report_path}")

        self.results["report_path"] = str(self.report_path)
        self.results["steps_completed"].append("generate_report")


def main():
    parser = argparse.ArgumentParser(
        description="Video Expert Analyzer - End-to-end video analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a Bilibili video
  python pipeline.py https://www.bilibili.com/video/BV1xxxxx -o output/

  # Analyze with custom settings
  python pipeline.py https://youtube.com/watch?v=xxxxx -o analysis/ --whisper-model base --no-extract-scenes

  # Quick analysis (faster)
  python pipeline.py URL -o dir/ --whisper-model tiny --scene-threshold 40
        """
    )

    parser.add_argument("url", help="Video URL (Bilibili or YouTube)")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("--whisper-model", default="medium",
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: medium)")
    parser.add_argument("--scene-threshold", type=float, default=27.0,
                       help="Scene detection threshold (default: 27.0)")
    parser.add_argument("--no-extract-scenes", action="store_true",
                       help="Skip extracting individual scene clips (faster)")
    parser.add_argument("--json-output", help="Save results as JSON to this file")

    args = parser.parse_args()

    try:
        pipeline = VideoAnalysisPipeline(
            url=args.url,
            output_dir=args.output,
            whisper_model=args.whisper_model,
            scene_threshold=args.scene_threshold,
            extract_scenes=not args.no_extract_scenes
        )

        results = pipeline.run()

        # Save results as JSON if requested
        if args.json_output:
            with open(args.json_output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n📊 Results saved to: {args.json_output}")

        print(f"\n📁 All outputs saved to: {pipeline.output_dir}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
