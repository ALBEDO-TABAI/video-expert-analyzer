#!/usr/bin/env python3
"""
Scene Scoring Helper - Enhanced Version
支持：精选片段复制到 scenes/best_shots/ 子文件夹、详细分析报告生成
"""

import json
import sys
import shutil
from pathlib import Path
from typing import Dict, List


def load_scores(json_path: str) -> Dict:
    """Load scene scores from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_scores(data: Dict, json_path: str):
    """Save scene scores to JSON file"""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_weighted_score(scene: Dict) -> float:
    """
    根据场景类型计算动态权重分数
    
    权重矩阵:
    - TYPE-A Hook/Kinetic: IMPACT 40%, MEMORABILITY 30%, SYNC 20%, AESTHETICS 10%
    - TYPE-B Narrative/Emotion: CREDIBILITY 40%, MEMORABILITY 30%, AESTHETICS 20%, IMPACT 10%
    - TYPE-C Aesthetic/Vibe: AESTHETICS 50%, SYNC 30%, IMPACT 20%
    - TYPE-D Commercial/Info: CREDIBILITY 40%, MEMORABILITY 40%, AESTHETICS 20%
    """
    scores = scene.get("scores", {})
    scene_type = scene.get("type_classification", "")
    
    # 获取各维度得分，默认为0
    aes = scores.get("aesthetic_beauty", 0)
    cred = scores.get("credibility", 0)
    imp = scores.get("impact", 0)
    mem = scores.get("memorability", 0)
    fun = scores.get("fun_interest", 0)
    
    # 根据类型计算加权得分
    if "TYPE-A" in scene_type or "Hook" in scene_type or "Kinetic" in scene_type:
        # Hook型: 冲击力最重要
        weighted = imp * 0.4 + mem * 0.3 + fun * 0.2 + aes * 0.1
    elif "TYPE-B" in scene_type or "Narrative" in scene_type or "Emotion" in scene_type:
        # 叙事型: 可信度最重要
        weighted = cred * 0.4 + mem * 0.3 + aes * 0.2 + imp * 0.1
    elif "TYPE-C" in scene_type or "Aesthetic" in scene_type or "Vibe" in scene_type:
        # 氛围型: 美感最重要
        weighted = aes * 0.5 + fun * 0.3 + imp * 0.2
    elif "TYPE-D" in scene_type or "Commercial" in scene_type or "Info" in scene_type:
        # 商业型: 可信度+记忆度
        weighted = cred * 0.4 + mem * 0.4 + aes * 0.2
    else:
        # 默认均匀权重
        weighted = (aes + cred + imp + mem + fun) / 5
    
    return round(weighted, 2)


def calculate_averages(data: Dict) -> Dict:
    """Calculate overall averages for each scene with dynamic weighting"""
    for scene in data.get("scenes", []):
        # 计算动态加权分数
        weighted = calculate_weighted_score(scene)
        scene["weighted_score"] = weighted
        
        # 同时计算简单平均分
        scores = scene.get("scores", {})
        if scores and all(isinstance(v, (int, float)) for v in scores.values()):
            avg = sum(scores.values()) / len(scores)
            scene["overall_average"] = round(avg, 2)
        else:
            scene["overall_average"] = 0.0
            
        # 根据分数自动确定 selection
        if weighted > 8.5 or any(v == 10 for v in scores.values()):
            scene["selection"] = "[MUST KEEP]"
        elif weighted >= 7.0:
            scene["selection"] = "[USABLE]"
        else:
            scene["selection"] = "[DISCARD]"
            
    return data


def rank_scenes(data: Dict) -> List[Dict]:
    """Rank scenes by weighted score"""
    scenes = data.get("scenes", [])
    return sorted(scenes, key=lambda x: x.get("weighted_score", 0), reverse=True)


def identify_best_shots(data: Dict, threshold: float = 7.5) -> List[Dict]:
    """Identify scenes above threshold"""
    scenes = data.get("scenes", [])
    return [s for s in scenes if s.get("weighted_score", 0) >= threshold]


def get_best_shots_dir(scores_path: Path) -> Path:
    """获取精选片段目录: scenes/best_shots/"""
    scenes_dir = scores_path.parent / "scenes"
    best_shots_dir = scenes_dir / "best_shots"
    best_shots_dir.mkdir(exist_ok=True)
    return best_shots_dir


def copy_best_shots(scenes: List[Dict], scores_path: str) -> int:
    """
    复制精选片段到 scenes/best_shots/ 子文件夹
    并生成精选片段说明文件
    """
    scores_path_obj = Path(scores_path)
    best_shots_dir = get_best_shots_dir(scores_path_obj)
    
    # 清空旧的精选片段
    for old_file in best_shots_dir.glob("*.mp4"):
        old_file.unlink()
    
    copied = 0
    best_shots_info = []
    
    for i, scene in enumerate(scenes, 1):
        src_path = Path(scene.get("file_path", ""))
        if src_path.exists():
            dst_path = best_shots_dir / f"{i:02d}_{src_path.name}"
            shutil.copy2(src_path, dst_path)
            copied += 1
            
            # 记录精选片段信息
            best_shots_info.append({
                "rank": i,
                "scene_number": scene.get("scene_number", "N/A"),
                "filename": src_path.name,
                "weighted_score": scene.get("weighted_score", 0),
                "selection": scene.get("selection", ""),
                "reasoning": scene.get("selection_reasoning", "")
            })
    
    # 生成精选片段说明文件
    generate_best_shots_readme(best_shots_dir, best_shots_info)
    
    return copied


def generate_best_shots_readme(best_shots_dir: Path, best_shots_info: List[Dict]):
    """生成精选片段说明文件"""
    readme_path = best_shots_dir / "README.md"
    
    content = """# ⭐ 精选片段 (Best Shots)

本文件夹包含根据 Walter Murch 剪辑法则和动态权重评分系统筛选出的高质量片段。

## 入选标准

- 加权总分 ≥ 7.5
- 或任意单项得分 = 10 (极致长板)

## 精选片段列表

| 排名 | 场景编号 | 文件名 | 加权得分 | 入选理由 |
|------|---------|--------|---------|---------|
"""
    
    for info in best_shots_info:
        content += f"| {info['rank']} | Scene {info['scene_number']:03d} | `{info['filename']}` | {info['weighted_score']:.2f} | {info['reasoning'][:50]}... |\n"
    
    content += """

## 使用建议

这些片段可直接用于：
- 社交媒体短视频
- 宣传片高光时刻
- 作品集展示
- 二次创作素材

---

*由 Video Expert Analyzer 自动筛选*
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_ranking_report(data: Dict, output_path: Path):
    """Generate a markdown ranking report with detailed analysis"""
    ranked = rank_scenes(data)
    
    # 获取框架信息
    framework = data.get("analysis_framework", {})
    philosophy = framework.get("philosophy", "Walter Murch's Six Rules")
    
    report = f"""# 📊 场景评分排名报告

**视频 ID:** {data.get('video_id', 'N/A')}  
**总场景数:** {data.get('total_scenes', 0)}  
**分析框架:** {philosophy}

---

## 🏆 综合排名

| 排名 | 场景 | 加权得分 | 平均分 | 筛选建议 | 类型分类 |
|------|------|---------|--------|---------|---------|
"""

    for i, scene in enumerate(ranked, 1):
        num = scene.get('scene_number', 'N/A')
        weighted = scene.get('weighted_score', 0.0)
        avg = scene.get('overall_average', 0.0)
        selection = scene.get('selection', 'TODO')
        scene_type = scene.get('type_classification', 'TODO')
        
        # 简化类型显示
        type_short = scene_type[:20] + "..." if len(scene_type) > 20 else scene_type
        
        report += f"| {i} | Scene {num:03d} | **{weighted:.2f}** | {avg:.2f} | {selection} | {type_short} |\n"

    report += """

---

## 📋 详细评分分析

"""

    for scene in ranked:
        num = scene.get('scene_number', 'N/A')
        weighted = scene.get('weighted_score', 0.0)
        avg = scene.get('overall_average', 0.0)
        scores = scene.get('scores', {})
        desc = scene.get('description', '无描述')
        reasoning = scene.get('selection_reasoning', '无理由')
        edit_suggestion = scene.get('edit_suggestion', '无建议')
        scene_type = scene.get('type_classification', '未分类')
        
        report += f"""### Scene {num:03d}

**基础信息**
- **类型分类**: {scene_type}
- **加权得分**: {weighted:.2f}
- **简单平均**: {avg:.2f}
- **筛选建议**: {scene.get('selection', 'TODO')}

**场景描述**: {desc}

**五维评分**
| 维度 | 得分 | 权重 | 说明 |
|------|------|------|------|
| 美感 | {scores.get('aesthetic_beauty', 0)} | 20% | {get_score_interpretation(scores.get('aesthetic_beauty', 0))} |
| 可信度 | {scores.get('credibility', 0)} | 20% | {get_score_interpretation(scores.get('credibility', 0))} |
| 冲击力 | {scores.get('impact', 0)} | 20% | {get_score_interpretation(scores.get('impact', 0))} |
| 记忆度 | {scores.get('memorability', 0)} | 20% | {get_score_interpretation(scores.get('memorability', 0))} |
| 趣味度 | {scores.get('fun_interest', 0)} | 20% | {get_score_interpretation(scores.get('fun_interest', 0))} |

**入选/淘汰理由**
> {reasoning}

**剪辑建议**
> {edit_suggestion}

---

"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def get_score_interpretation(score: int) -> str:
    """获取分数解读"""
    if score >= 9:
        return "⭐⭐⭐ 极致"
    elif score >= 7:
        return "⭐⭐ 优秀"
    elif score >= 5:
        return "⭐ 良好"
    elif score >= 3:
        return "⚠️ 一般"
    else:
        return "❌ 较差"


def generate_detailed_summary(data: Dict, output_path: Path):
    """生成整体影片评价摘要"""
    scenes = data.get("scenes", [])
    total = len(scenes)
    
    if total == 0:
        return
    
    # 统计
    must_keep = sum(1 for s in scenes if "MUST KEEP" in s.get("selection", ""))
    usable = sum(1 for s in scenes if "USABLE" in s.get("selection", ""))
    discard = sum(1 for s in scenes if "DISCARD" in s.get("selection", ""))
    
    weighted_scores = [s.get("weighted_score", 0) for s in scenes if s.get("weighted_score", 0) > 0]
    avg_weighted = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0
    
    # 各维度平均分
    dim_avgs = {}
    for dim in ["aesthetic_beauty", "credibility", "impact", "memorability", "fun_interest"]:
        vals = [s.get("scores", {}).get(dim, 0) for s in scenes]
        dim_avgs[dim] = sum(vals) / len(vals) if vals else 0
    
    summary = f"""# 📈 整体影片评价摘要

## 统计概览

| 指标 | 数值 |
|------|------|
| **总场景数** | {total} |
| 🌟 MUST KEEP | {must_keep} ({must_keep/total*100:.1f}%) |
| 📁 USABLE | {usable} ({usable/total*100:.1f}%) |
| 🗑️ DISCARD | {discard} ({discard/total*100:.1f}%) |
| **平均加权得分** | {avg_weighted:.2f} |

## 各维度平均分

| 维度 | 平均分 | 评价 |
|------|--------|------|
| 美感 | {dim_avgs['aesthetic_beauty']:.2f} | {get_dimension_rating(dim_avgs['aesthetic_beauty'])} |
| 可信度 | {dim_avgs['credibility']:.2f} | {get_dimension_rating(dim_avgs['credibility'])} |
| 冲击力 | {dim_avgs['impact']:.2f} | {get_dimension_rating(dim_avgs['impact'])} |
| 记忆度 | {dim_avgs['memorability']:.2f} | {get_dimension_rating(dim_avgs['memorability'])} |
| 趣味度 | {dim_avgs['fun_interest']:.2f} | {get_dimension_rating(dim_avgs['fun_interest'])} |

## 评价总结

### 整体印象
*(根据上述数据自动生成的初步评价)*

"""
    
    # 自动生成评价
    strengths = []
    weaknesses = []
    
    if dim_avgs['aesthetic_beauty'] >= 7:
        strengths.append("画面美感出色")
    elif dim_avgs['aesthetic_beauty'] < 5:
        weaknesses.append("画面美感有待提升")
        
    if dim_avgs['impact'] >= 7:
        strengths.append("视觉冲击力强")
    elif dim_avgs['impact'] < 5:
        weaknesses.append("缺乏视觉冲击力")
        
    if dim_avgs['memorability'] >= 7:
        strengths.append("具备良好记忆点")
    elif dim_avgs['memorability'] < 5:
        weaknesses.append("记忆点不够突出")
    
    if strengths:
        summary += "**优势**: " + "、".join(strengths) + "\n\n"
    if weaknesses:
        summary += "**待改进**: " + "、".join(weaknesses) + "\n\n"
    
    summary += f"""
### 基于 Walter Murch 法则的评价

根据 **情感 > 故事 > 节奏** 的核心原则：

- **情感层面**: {get_emotion_assessment(dim_avgs['credibility'], dim_avgs['memorability'])}
- **故事层面**: {get_story_assessment(dim_avgs['impact'], dim_avgs['fun_interest'])}
- **节奏层面**: 建议根据 IMPACT 得分 ({dim_avgs['impact']:.2f}) 调整剪辑节奏

### 最终建议

"""
    
    if avg_weighted >= 8:
        summary += "✅ **强烈推荐保留** - 这是一部高质量的视频素材\n"
    elif avg_weighted >= 6:
        summary += "📁 **建议保留** - 虽有不足，但仍有可用价值\n"
    else:
        summary += "🗑️ **建议舍弃** - 整体质量较低，不建议使用\n"
    
    summary += f"""
---

*基于 {total} 个场景的动态权重评分*
*分析框架: Walter Murch's Six Rules*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)


def get_dimension_rating(score: float) -> str:
    """获取维度评价"""
    if score >= 8:
        return "🟢 优秀"
    elif score >= 6:
        return "🟡 良好"
    elif score >= 4:
        return "🟠 一般"
    else:
        return "🔴 较差"


def get_emotion_assessment(cred: float, mem: float) -> str:
    """情感层面评估"""
    avg = (cred + mem) / 2
    if avg >= 8:
        return "情感真挚、极具感染力，能建立强烈的观众共情"
    elif avg >= 6:
        return "情感表达自然，具备一定的共情能力"
    elif avg >= 4:
        return "情感表达尚可，但缺乏深度共鸣"
    else:
        return "情感表达较弱，难以引起观众共鸣"


def get_story_assessment(impact: float, fun: float) -> str:
    """故事层面评估"""
    avg = (impact + fun) / 2
    if avg >= 8:
        return "故事性强，能有效吸引并保持观众注意力"
    elif avg >= 6:
        return "具备一定的叙事吸引力"
    elif avg >= 4:
        return "故事性一般，吸引力有限"
    else:
        return "故事性弱，难以吸引观众"


def print_summary(data: Dict):
    """Print scoring summary"""
    scenes = data.get("scenes", [])
    total = len(scenes)
    scored = sum(1 for s in scenes if s.get("weighted_score", 0) > 0)
    weighted_scores = [s.get("weighted_score", 0) for s in scenes if s.get("weighted_score", 0) > 0]
    
    print(f"\n{'=' * 60}")
    print("📊 场景评分汇总")
    print(f"{'=' * 60}")
    print(f"总场景数: {total}")
    print(f"已评分: {scored}")
    print(f"未评分: {total - scored}")

    if weighted_scores:
        print(f"\n平均加权得分: {sum(weighted_scores) / len(weighted_scores):.2f}")
        print(f"最高加权得分: {max(weighted_scores):.2f}")
        print(f"最低加权得分: {min(weighted_scores):.2f}")

        must_keep = sum(1 for s in scenes if "MUST KEEP" in s.get("selection", ""))
        usable = sum(1 for s in scenes if "USABLE" in s.get("selection", ""))
        discard = sum(1 for s in scenes if "DISCARD" in s.get("selection", ""))
        
        print(f"\n🌟 MUST KEEP: {must_keep}")
        print(f"📁 USABLE: {usable}")
        print(f"🗑️ DISCARD: {discard}")

    print(f"{'=' * 60}\n")


def validate_scenes(data: Dict) -> List[int]:
    """检查未完成的评分"""
    incomplete = []
    for scene in data.get("scenes", []):
        scores = scene.get("scores", {})
        if not all(isinstance(v, (int, float)) and v > 0 for v in scores.values()):
            incomplete.append(scene.get("scene_number", "?"))
    return incomplete


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scoring_helper.py <scene_scores.json> [命令] [参数]")
        print("\n命令:")
        print("  summary [阈值]       - 显示评分汇总 (默认阈值: 7.5)")
        print("  calculate            - 计算加权得分和平均分")
        print("  rank                 - 生成排名报告")
        print("  best [阈值]          - 复制精选片段到 scenes/best_shots/ (默认阈值: 7.5)")
        print("  validate             - 检查未完成的评分")
        print("  full                 - 执行 calculate + rank + best + summary")
        sys.exit(1)

    json_path = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "summary"

    # Load data
    try:
        data = load_scores(json_path)
    except FileNotFoundError:
        print(f"❌ Error: 文件不存在: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON 格式错误: {e}")
        sys.exit(1)

    output_dir = Path(json_path).parent

    # Execute command
    if command == "summary":
        threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 7.5
        data = calculate_averages(data)
        print_summary(data)
        
        best = identify_best_shots(data, threshold)
        print(f"📊 阈值 {threshold} 以上的精选片段: {len(best)} 个")
        
    elif command == "calculate":
        data = calculate_averages(data)
        save_scores(data, json_path)
        print(f"✅ 加权得分已计算并保存到 {json_path}")
        print_summary(data)

    elif command == "rank":
        data = calculate_averages(data)
        report_path = output_dir / "scene_rankings.md"
        generate_ranking_report(data, report_path)
        print(f"✅ 排名报告已生成: {report_path}")
        
        # 同时生成整体评价
        summary_path = output_dir / "overall_assessment.md"
        generate_detailed_summary(data, summary_path)
        print(f"✅ 整体评价已生成: {summary_path}")
        
        print_summary(data)

    elif command == "best":
        threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 7.5
        
        # 确保已计算加权得分
        data = calculate_averages(data)
        save_scores(data, json_path)
        
        best = identify_best_shots(data, threshold)

        if not best:
            print(f"⚠️  没有找到加权得分 ≥ {threshold} 的场景")
            sys.exit(0)

        print(f"\n📊 找到 {len(best)} 个精选场景 (≥ {threshold}):")
        for scene in best:
            num = scene.get('scene_number', 'N/A')
            score = scene.get('weighted_score', 0)
            desc = scene.get('description', '无描述')[:50]
            print(f"  • Scene {num:03d}: {score:.2f} - {desc}")

        print(f"\n📁 复制到 scenes/best_shots/...")
        copied = copy_best_shots(best, json_path)
        best_shots_dir = get_best_shots_dir(Path(json_path))
        print(f"✅ 已复制 {copied} 个场景到 {best_shots_dir}/")
        print(f"📝 说明文件: {best_shots_dir}/README.md")

    elif command == "validate":
        incomplete = validate_scenes(data)
        if incomplete:
            print(f"⚠️  发现 {len(incomplete)} 个未完成评分的场景:")
            for num in incomplete:
                print(f"  • Scene {num:03d}")
        else:
            print("✅ 所有场景已完成评分！")
            
    elif command == "full":
        threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 7.5
        
        print("🔄 执行完整分析流程...\n")
        
        # 1. Calculate
        data = calculate_averages(data)
        save_scores(data, json_path)
        print("✅ 步骤 1/4: 加权得分计算完成")
        
        # 2. Rank
        report_path = output_dir / "scene_rankings.md"
        generate_ranking_report(data, report_path)
        summary_path = output_dir / "overall_assessment.md"
        generate_detailed_summary(data, summary_path)
        print(f"✅ 步骤 2/4: 排名报告生成完成")
        print(f"   📄 {report_path}")
        print(f"   📄 {summary_path}")
        
        # 3. Best shots
        best = identify_best_shots(data, threshold)
        if best:
            copied = copy_best_shots(best, json_path)
            best_shots_dir = get_best_shots_dir(Path(json_path))
            print(f"✅ 步骤 3/4: 精选片段已复制 ({len(best)} 个)")
            print(f"   📁 {best_shots_dir}/")
        else:
            print(f"⚠️  步骤 3/4: 无精选片段 (阈值 {threshold})")
        
        # 4. Summary
        print("\n" + "=" * 60)
        print("✅ 步骤 4/4: 分析完成")
        print("=" * 60)
        print_summary(data)

    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
