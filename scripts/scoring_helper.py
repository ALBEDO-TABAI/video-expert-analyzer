#!/usr/bin/env python3
"""
Scene Scoring Helper
Assists with scoring scenes and identifying best shots
"""

import json
import sys
import shutil
from pathlib import Path
from typing import List, Dict


def load_scores(json_path: str) -> Dict:
    """Load scene scores from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_scores(data: Dict, json_path: str):
    """Save scene scores to JSON file"""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_averages(data: Dict) -> Dict:
    """Calculate overall averages for each scene"""
    for scene in data.get("scenes", []):
        scores = scene.get("scores", {})
        if scores and all(isinstance(v, (int, float)) for v in scores.values()):
            avg = sum(scores.values()) / len(scores)
            scene["overall_average"] = round(avg, 2)
        else:
            scene["overall_average"] = 0.0
    return data


def rank_scenes(data: Dict) -> List[Dict]:
    """Rank scenes by overall average"""
    scenes = data.get("scenes", [])
    return sorted(scenes, key=lambda x: x.get("overall_average", 0), reverse=True)


def identify_best_shots(data: Dict, threshold: float = 7.0) -> List[Dict]:
    """Identify scenes above threshold"""
    scenes = data.get("scenes", [])
    return [s for s in scenes if s.get("overall_average", 0) >= threshold]


def copy_best_shots(scenes: List[Dict], output_dir: Path):
    """Copy best scene files to best_shots directory"""
    best_shots_dir = output_dir / "best_shots"
    best_shots_dir.mkdir(exist_ok=True)

    copied = 0
    for scene in scenes:
        src_path = Path(scene.get("file_path", ""))
        if src_path.exists():
            dst_path = best_shots_dir / src_path.name
            shutil.copy2(src_path, dst_path)
            copied += 1

    return copied


def generate_ranking_report(data: Dict, output_path: Path):
    """Generate a markdown ranking report"""
    ranked = rank_scenes(data)

    report = f"""# Scene Ranking Report

**Video ID:** {data.get('video_id', 'N/A')}
**Total Scenes:** {data.get('total_scenes', 0)}
**Analysis Date:** {data.get('timestamp', 'N/A')}

## Overall Rankings

| Rank | Scene | Score | Description |
|------|-------|-------|-------------|
"""

    for i, scene in enumerate(ranked, 1):
        num = scene.get('scene_number', 'N/A')
        score = scene.get('overall_average', 0.0)
        desc = scene.get('description', 'No description')[:60]
        report += f"| {i} | Scene {num:03d} | {score:.2f} | {desc}... |\n"

    report += "\n## Detailed Scores\n\n"

    for scene in ranked:
        num = scene.get('scene_number', 'N/A')
        score = scene.get('overall_average', 0.0)
        scores = scene.get('scores', {})
        desc = scene.get('description', 'No description')
        notes = scene.get('notes', 'No notes')

        report += f"### Scene {num:03d} - Overall: {score:.2f}\n\n"
        report += f"**Description:** {desc}\n\n"
        report += "**Scores:**\n"
        for criterion, value in scores.items():
            report += f"- {criterion.replace('_', ' ').title()}: {value}/10\n"
        report += f"\n**Notes:** {notes}\n\n"
        report += "---\n\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def print_summary(data: Dict):
    """Print scoring summary"""
    scenes = data.get("scenes", [])
    total = len(scenes)
    scored = sum(1 for s in scenes if s.get("overall_average", 0) > 0)
    avg_scores = [s.get("overall_average", 0) for s in scenes if s.get("overall_average", 0) > 0]

    print(f"\n{'=' * 60}")
    print("SCENE SCORING SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Scenes: {total}")
    print(f"Scored Scenes: {scored}")
    print(f"Unscored Scenes: {total - scored}")

    if avg_scores:
        print(f"\nAverage Score: {sum(avg_scores) / len(avg_scores):.2f}")
        print(f"Highest Score: {max(avg_scores):.2f}")
        print(f"Lowest Score: {min(avg_scores):.2f}")

        best = identify_best_shots(data, threshold=7.0)
        print(f"\nBest Shots (≥7.0): {len(best)}")

    print(f"{'=' * 60}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scoring_helper.py <scene_scores.json> [command]")
        print("\nCommands:")
        print("  summary              - Display scoring summary (default)")
        print("  calculate            - Calculate overall averages")
        print("  rank                 - Generate ranking report")
        print("  best [threshold]     - Copy best shots (default threshold: 7.0)")
        print("  validate             - Check for incomplete scores")
        sys.exit(1)

    json_path = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "summary"

    # Load data
    try:
        data = load_scores(json_path)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {e}")
        sys.exit(1)

    # Calculate averages
    data = calculate_averages(data)

    # Execute command
    if command == "summary":
        print_summary(data)

    elif command == "calculate":
        save_scores(data, json_path)
        print(f"✅ Averages calculated and saved to {json_path}")
        print_summary(data)

    elif command == "rank":
        output_dir = Path(json_path).parent
        report_path = output_dir / "scene_rankings.md"
        generate_ranking_report(data, report_path)
        print(f"✅ Ranking report generated: {report_path}")
        print_summary(data)

    elif command == "best":
        threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 7.0
        output_dir = Path(json_path).parent
        best = identify_best_shots(data, threshold)

        if not best:
            print(f"⚠️  No scenes found with score ≥ {threshold}")
            sys.exit(0)

        print(f"\n📊 Found {len(best)} scenes with score ≥ {threshold}:")
        for scene in best:
            num = scene.get('scene_number', 'N/A')
            score = scene.get('overall_average', 0)
            desc = scene.get('description', 'No description')[:50]
            print(f"  • Scene {num:03d}: {score:.2f} - {desc}")

        print(f"\n📁 Copying to best_shots/...")
        copied = copy_best_shots(best, output_dir)
        print(f"✅ Copied {copied} scenes to {output_dir / 'best_shots'}/")

    elif command == "validate":
        incomplete = []
        for scene in data.get("scenes", []):
            scores = scene.get("scores", {})
            if not all(isinstance(v, (int, float)) and v > 0 for v in scores.values()):
                incomplete.append(scene.get("scene_number", "?"))

        if incomplete:
            print(f"⚠️  Found {len(incomplete)} incomplete scenes:")
            for num in incomplete:
                print(f"  • Scene {num:03d}")
        else:
            print("✅ All scenes have been scored!")

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
