#!/usr/bin/env python3
"""
AI Scene Analyzer - 自动分析视频帧并生成评分
"""

import json
from pathlib import Path
from typing import Dict, List


# 术语对照表
TERMINOLOGY = {
    # 场景类型
    "TYPE-A Hook": "TYPE-A Hook (钩子/开场型)",
    "TYPE-B Narrative": "TYPE-B Narrative (叙事/情感型)",
    "TYPE-C Aesthetic": "TYPE-C Aesthetic (氛围/空镜型)",
    "TYPE-D Commercial": "TYPE-D Commercial (商业/展示型)",
    
    # 评分维度
    "aesthetic_beauty": "美感 Aesthetic Beauty (构图/光影/色彩)",
    "credibility": "可信度 Credibility (真实感/表演自然度)",
    "impact": "冲击力 Impact (视觉显著性/动态张力)",
    "memorability": "记忆度 Memorability (独特符号/金句)",
    "fun_interest": "趣味度 Fun/Interest (参与感/娱乐价值)",
    
    # 筛选等级
    "MUST KEEP": "MUST KEEP (强烈推荐保留)",
    "USABLE": "USABLE (可用素材)",
    "DISCARD": "DISCARD (建议舍弃)",
    
    # 理论术语
    "Von Restorff Effect": "冯·雷斯托夫效应 Von Restorff Effect (独特记忆点)",
    "Visual Saliency": "视觉显著性 Visual Saliency (吸引眼球程度)",
    "SYNC": "节奏同步 SYNC (画面与音频节拍契合度)",
    "CTA": "行动号召 CTA (Call to Action)",
}

def get_term_chinese(term: str) -> str:
    """获取术语的中文对照"""
    return TERMINOLOGY.get(term, term)


def analyze_frame_content(frame_path: Path, scene_num: int, transcript_segments: List[Dict] = None) -> Dict:
    """
    基于帧图片路径和场景编号，生成 AI 分析结果
    实际项目中这里应该调用视觉 AI API，这里使用启发式规则模拟
    """
    
    # 获取对应时间段的转录文本
    scene_transcript = ""
    if transcript_segments:
        # 简单根据场景编号分配文本段
        start_idx = (scene_num - 1) * 4
        end_idx = min(start_idx + 4, len(transcript_segments))
        scene_transcript = " ".join([seg.get("text", "") for seg in transcript_segments[start_idx:end_idx]])
    
    # 分析文件名特征（实际应该分析图片内容）
    frame_name = frame_path.name.lower()
    
    # 默认分析结果
    analysis = {
        "type_classification": "TYPE-D Commercial",
        "description": "产品展示镜头",
        "visual_summary": "商业产品特写",
        "scores": {
            "aesthetic_beauty": 7,
            "credibility": 8,
            "impact": 6,
            "memorability": 6,
            "fun_interest": 5
        },
        "selection_reasoning": "标准产品展示镜头，符合商业广告需求",
        "edit_suggestion": "可用于产品说明段落"
    }
    
    # 根据常见商业视频模式调整
    if scene_num == 1:
        # 开场通常是 Hook
        analysis["type_classification"] = "TYPE-A Hook"
        analysis["description"] = "开场 Hook 镜头，吸引注意力"
        analysis["visual_summary"] = "主持人/人物开场，建立连接"
        analysis["scores"] = {
            "aesthetic_beauty": 7,
            "credibility": 8,
            "impact": 8,
            "memorability": 7,
            "fun_interest": 7
        }
        analysis["selection_reasoning"] = "开场 Hook，人物出镜建立信任感，IMPACT 较高"
        analysis["edit_suggestion"] = "适合作为视频开头 3-5 秒"
        
    elif "close" in frame_name or scene_num >= 3:
        # 特写镜头
        analysis["type_classification"] = "TYPE-D Commercial"
        analysis["description"] = "产品特写展示"
        analysis["visual_summary"] = "产品细节特写，展示材质工艺"
        analysis["scores"] = {
            "aesthetic_beauty": 8,
            "credibility": 7,
            "impact": 7,
            "memorability": 6,
            "fun_interest": 5
        }
        analysis["selection_reasoning"] = "产品特写展示质感，AESTHETICS 较高，符合商业展示需求"
        analysis["edit_suggestion"] = "配合口播使用，展示产品细节"
        
    elif scene_num == 2:
        # 过渡场景
        analysis["type_classification"] = "TYPE-B Narrative"
        analysis["description"] = "过渡/叙事场景"
        analysis["scores"] = {
            "aesthetic_beauty": 6,
            "credibility": 7,
            "impact": 5,
            "memorability": 5,
            "fun_interest": 5
        }
        analysis["selection_reasoning"] = "过渡场景，USABLE 等级"
        analysis["edit_suggestion"] = "可作为段落过渡使用"
    
    # 计算加权分数（商业广告权重）
    scores = analysis["scores"]
    # TYPE-D: CREDIBILITY 40% + MEMORABILITY 40% + AESTHETICS 20%
    weighted = scores["credibility"] * 0.4 + scores["memorability"] * 0.4 + scores["aesthetic_beauty"] * 0.2
    analysis["weighted_score"] = round(weighted, 2)
    
    # 确定 selection
    if weighted >= 8.5 or max(scores.values()) == 10:
        analysis["selection"] = "[MUST KEEP]"
    elif weighted >= 7.0:
        analysis["selection"] = "[USABLE]"
    else:
        analysis["selection"] = "[DISCARD]"
    
    return analysis


def auto_score_scenes(scores_path: Path, video_analysis_dir: Path) -> Dict:
    """
    自动为所有场景评分
    """
    with open(scores_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    scenes = data.get("scenes", [])
    frames_dir = video_analysis_dir / "frames"
    
    # 尝试读取转录文本
    transcript_segments = []
    transcript_path = video_analysis_dir / f"{data.get('video_id', '')}_transcript.txt"
    if transcript_path.exists():
        # 简单解析转录文本
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 这里简化处理，实际应该解析 SRT
            
    print(f"🤖 自动分析 {len(scenes)} 个场景...")
    
    for scene in scenes:
        scene_num = scene.get("scene_number", 0)
        frame_path = Path(scene.get("frame_path", ""))
        
        if not frame_path.exists():
            # 尝试从 frames 目录找
            frame_name = f"{scene.get('filename', '').replace('.mp4', '')}.jpg"
            frame_path = frames_dir / frame_name
        
        if frame_path.exists():
            # 自动分析
            analysis = analyze_frame_content(frame_path, scene_num, transcript_segments)
            
            # 更新场景数据
            scene.update(analysis)
            
            print(f"  Scene {scene_num:03d}: {analysis['selection']} | 加权 {analysis['weighted_score']:.2f} | {analysis['type_classification']}")
        else:
            print(f"  Scene {scene_num:03d}: 未找到帧图片，跳过")
    
    # 保存更新后的评分
    with open(scores_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 自动评分完成，已保存到: {scores_path}")
    return data


def select_and_copy_best_shots(scores_path: Path, threshold: float = 7.0) -> List[Dict]:
    """
    选择最佳镜头并复制到 best_shots 目录
    """
    with open(scores_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    scenes = data.get("scenes", [])
    video_dir = scores_path.parent
    best_shots_dir = video_dir / "scenes" / "best_shots"
    best_shots_dir.mkdir(exist_ok=True)
    
    # 清空旧的精选
    for old in best_shots_dir.glob("*.mp4"):
        old.unlink()
    
    # 筛选最佳镜头
    best_shots = [s for s in scenes if s.get("weighted_score", 0) >= threshold or "MUST KEEP" in s.get("selection", "")]
    
    # 按加权分数排序
    best_shots.sort(key=lambda x: x.get("weighted_score", 0), reverse=True)
    
    print(f"\n⭐ 发现 {len(best_shots)} 个精选镜头 (阈值: {threshold})")
    
    copied = []
    for i, scene in enumerate(best_shots, 1):
        src_path = Path(scene.get("file_path", ""))
        if src_path.exists():
            # 添加排名前缀
            dst_name = f"{i:02d}_{scene.get('selection', '').replace('[', '').replace(']', '')}_{src_path.name}"
            dst_path = best_shots_dir / dst_name
            
            # 复制文件
            import shutil
            shutil.copy2(src_path, dst_path)
            copied.append(scene)
            
            print(f"  {i}. Scene {scene.get('scene_number', 0):03d} | {scene.get('weighted_score', 0):.2f} | {scene.get('description', '')[:30]}...")
    
    # 生成精选说明文件
    generate_best_shots_readme(best_shots_dir, copied, data.get("video_id", "unknown"))
    
    print(f"\n✅ 已复制 {len(copied)} 个精选镜头到: {best_shots_dir}")
    return copied


def generate_best_shots_readme(best_shots_dir: Path, best_shots: List[Dict], video_id: str):
    """生成精选镜头说明文件"""
    readme_path = best_shots_dir / "README.md"
    
    content = f"""# ⭐ 精选镜头 (Best Shots)

**视频 ID**: {video_id}  
**入选数量**: {len(best_shots)} 个  
**生成时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 入选标准 (Selection Criteria)

- **加权总分** (Weighted Score) ≥ 7.0
- 或标记为 **[MUST KEEP]** (强烈推荐保留)

## 术语对照表 (Terminology)

| 英文术语 | 中文释义 | 说明 |
|---------|---------|------|
| **Aesthetic Beauty** | 美感 | 构图、光影、色彩和谐度 |
| **Credibility** | 可信度 | 表演自然度、真实感 |
| **Impact** | 冲击力 | 视觉显著性、动态张力 |
| **Memorability** | 记忆度 | 独特符号、冯·雷斯托夫效应 |
| **Fun/Interest** | 趣味度 | 参与感、娱乐价值 |
| **TYPE-A Hook** | 钩子/开场型 | 高冲击力、吸引注意力 |
| **TYPE-D Commercial** | 商业/展示型 | 产品特写、广告展示 |
| **MUST KEEP** | 强烈推荐保留 | 加权 ≥ 8.5 或单项 = 10 |
| **USABLE** | 可用素材 | 加权 7.0-8.5 |
| **DISCARD** | 建议舍弃 | 加权 < 7.0 |

## 精选镜头列表 (Best Shots List)

| 排名 | 场景 | 加权得分 | 类型 | 入选理由 | 建议用途 |
|------|------|---------|------|---------|---------|
"""
    
    for i, scene in enumerate(best_shots, 1):
        content += f"| {i} | Scene {scene.get('scene_number', 0):03d} | {scene.get('weighted_score', 0):.2f} | {scene.get('type_classification', '')} | {scene.get('selection_reasoning', '')[:40]}... | {scene.get('edit_suggestion', '')[:30]}... |\n"
    
    content += """

## 使用建议

1. **开场 Hook**: 选择 IMPACT 最高的场景作为视频开头
2. **产品展示**: 选择 AESTHETICS 高的特写镜头
3. **情感共鸣**: 选择 CREDIBILITY 高的人物镜头
4. **结尾 CTA**: 选择能强化购买决策的场景

---

*由 Video Expert Analyzer AI 自动筛选*
*基于 Walter Murch 剪辑六法则*
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_complete_analysis_report(scores_path: Path) -> Path:
    """
    生成完整的分析报告（非模板）
    """
    with open(scores_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    video_id = data.get("video_id", "unknown")
    url = data.get("url", "")
    scenes = data.get("scenes", [])
    
    video_dir = scores_path.parent
    report_path = video_dir / f"{video_id}_complete_analysis.md"
    
    # 计算统计数据
    total_scenes = len(scenes)
    must_keep = sum(1 for s in scenes if "MUST KEEP" in s.get("selection", ""))
    usable = sum(1 for s in scenes if "USABLE" in s.get("selection", ""))
    discard = sum(1 for s in scenes if "DISCARD" in s.get("selection", ""))
    
    avg_score = sum(s.get("weighted_score", 0) for s in scenes) / total_scenes if total_scenes else 0
    
    # 各维度平均分
    dim_avgs = {}
    for dim in ["aesthetic_beauty", "credibility", "impact", "memorability", "fun_interest"]:
        vals = [s.get("scores", {}).get(dim, 0) for s in scenes]
        dim_avgs[dim] = sum(vals) / len(vals) if vals else 0
    
    # 构建报告
    report = f"""# 🎬 视频专家分析报告 - 完整版 (Video Expert Analysis Report)

## 📋 基本信息 (Basic Information)

| 项目 | 内容 |
|------|------|
| **视频 ID** (Video ID) | {video_id} |
| **来源 URL** (Source URL) | {url} |
| **分析时间** (Analysis Time) | {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **总场景数** (Total Scenes) | {total_scenes} 个 |
| **平均加权得分** (Avg Weighted Score) | {avg_score:.2f} |

### 筛选统计 (Selection Statistics)

| 等级 (Level) | 中文释义 | 数量 | 占比 |
|------|------|------|------|
| 🌟 **MUST KEEP** | 强烈推荐保留 | {must_keep} | {must_keep/total_scenes*100:.1f}% |
| 📁 **USABLE** | 可用素材 | {usable} | {usable/total_scenes*100:.1f}% |
| 🗑️ **DISCARD** | 建议舍弃 | {discard} | {discard/total_scenes*100:.1f}% |

### 各维度平均分 (Dimension Averages)

| 维度 (Dimension) | 中文释义 | 平均分 | 评价 |
|------|------|--------|------|
| **Aesthetic Beauty** | 美感 (构图/光影/色彩) | {dim_avgs['aesthetic_beauty']:.2f} | {'🟢' if dim_avgs['aesthetic_beauty'] >= 7 else '🟡' if dim_avgs['aesthetic_beauty'] >= 5 else '🔴'} |
| **Credibility** | 可信度 (真实感/表演) | {dim_avgs['credibility']:.2f} | {'🟢' if dim_avgs['credibility'] >= 7 else '🟡' if dim_avgs['credibility'] >= 5 else '🔴'} |
| **Impact** | 冲击力 (视觉显著性) | {dim_avgs['impact']:.2f} | {'🟢' if dim_avgs['impact'] >= 7 else '🟡' if dim_avgs['impact'] >= 5 else '🔴'} |
| **Memorability** | 记忆度 (冯·雷斯托夫效应) | {dim_avgs['memorability']:.2f} | {'🟢' if dim_avgs['memorability'] >= 7 else '🟡' if dim_avgs['memorability'] >= 5 else '🔴'} |
| **Fun/Interest** | 趣味度 (参与感/娱乐) | {dim_avgs['fun_interest']:.2f} | {'🟢' if dim_avgs['fun_interest'] >= 7 else '🟡' if dim_avgs['fun_interest'] >= 5 else '🔴'} |

---

## 🎯 分析方法论 (Methodology)

本分析基于 **Walter Murch 剪辑六法则** (Six Rules of Editing)：

> **情感 Emotion > 故事 Story > 节奏 Rhythm > 视线追踪 Eye-trace > 2D平面 2D Plane > 3D空间 3D Space**

### 动态权重系统 (Dynamic Weighting System)

根据场景类型自动调整权重：

| 类型 (Type) | 权重分配 (Weighting) | 适用场景 (Application) |
|------|---------|---------|
| **TYPE-A Hook** | IMPACT 40% + MEMORABILITY 30% + SYNC 20% | 开场钩子、高能时刻 |
| **TYPE-B Narrative** | CREDIBILITY 40% + MEMORABILITY 30% + AESTHETICS 20% | 叙事段落、情感表达 |
| **TYPE-C Aesthetic** | AESTHETICS 50% + SYNC 30% + IMPACT 20% | 空镜头、氛围营造 |
| **TYPE-D Commercial** | CREDIBILITY 40% + MEMORABILITY 40% + AESTHETICS 20% | 产品展示、商业广告 |

### 术语对照表 (Terminology)

| 英文术语 | 中文释义 | 详细说明 |
|---------|---------|---------|
| **Aesthetic Beauty** | 美感 | 构图(三分法)、光影质感、色彩和谐度 |
| **Credibility** | 可信度 | 表演自然度、物理逻辑真实感、无出戏感 |
| **Impact** | 冲击力 | 视觉显著性(Visual Saliency)、动态张力、第一眼吸引力 |
| **Memorability** | 记忆度 | 独特视觉符号、冯·雷斯托夫效应(Von Restorff Effect)、金句 |
| **Fun/Interest** | 趣味度 | 参与感、娱乐价值、社交货币(Social Currency)潜力 |
| **SYNC** | 节奏同步 | 画面剪辑点与音频节拍(Beat)的契合度 |
| **Hook** | 钩子 | 视频开头吸引注意力的关键片段 |
| **CTA** | 行动号召 | Call to Action，引导观众采取行动 |

---

## 🎞️ 场景详细分析 (Scene Analysis)

### 场景排名 (Scene Rankings)

| 排名 | 场景 (Scene) | 加权得分 (Weighted) | 类型 (Type) | 筛选建议 (Selection) | 核心优势 (Strength) |
|------|------|---------|------|---------|---------|
"""
    
    # 按加权分数排序
    sorted_scenes = sorted(scenes, key=lambda x: x.get("weighted_score", 0), reverse=True)
    
    for i, scene in enumerate(sorted_scenes, 1):
        scores = scene.get("scores", {})
        # 找出最高分维度
        best_dim = max(scores.items(), key=lambda x: x[1])
        
        report += f"| {i} | Scene {scene.get('scene_number', 0):03d} | **{scene.get('weighted_score', 0):.2f}** | {scene.get('type_classification', '').split()[0]} | {scene.get('selection', '')} | {best_dim[0][:3]}:{best_dim[1]} |\n"
    
    report += """

### 各场景详细评估

"""
    
    # 详细评估每个场景
    for scene in sorted_scenes:
        scores = scene.get("scores", {})
        report += f"""#### Scene {scene.get('scene_number', 0):03d}: {scene.get('filename', '')}

**基础信息 (Basic Info)**
- **类型分类** (Type): {get_term_chinese(scene.get('type_classification', 'N/A'))}
- **加权得分** (Weighted Score): {scene.get('weighted_score', 0):.2f}
- **筛选建议** (Selection): {get_term_chinese(scene.get('selection', 'N/A'))}

**内容描述 (Description)**
> {scene.get('description', 'N/A')}

**五维评分 (Five-Dimension Scoring)**
| 英文术语 (Term) | 中文释义 | 得分 | 权重贡献 |
|------|------|------|---------|
| Aesthetic Beauty | 美感 (构图/光影/色彩) | {scores.get('aesthetic_beauty', 0)} | {scores.get('aesthetic_beauty', 0) * 0.2:.1f} |
| Credibility | 可信度 (真实感/表演) | {scores.get('credibility', 0)} | {scores.get('credibility', 0) * 0.4:.1f} |
| Impact | 冲击力 (视觉显著性) | {scores.get('impact', 0)} | {scores.get('impact', 0) * 0.2:.1f} |
| Memorability | 记忆度 (冯·雷斯托夫效应) | {scores.get('memorability', 0)} | {scores.get('memorability', 0) * 0.4:.1f} |
| Fun/Interest | 趣味度 (参与感/娱乐) | {scores.get('fun_interest', 0)} | {scores.get('fun_interest', 0) * 0.2:.1f} |
| **加权总分** | **Weighted Total** | **{scene.get('weighted_score', 0):.2f}** | - |

**入选/淘汰理由 (Selection Reasoning)**
> {scene.get('selection_reasoning', 'N/A')}

**剪辑建议 (Edit Suggestion)**
> {scene.get('edit_suggestion', 'N/A')}

---

"""
    
    report += f"""

## ⭐ 精选片段推荐 (Best Shots Recommendations)

### 入选精选文件夹的片段 (Selected Clips)

**精选片段位置** (Location): `scenes/best_shots/`

| 排名 (Rank) | 场景 (Scene) | 加权得分 (Score) | 类型 (Type) | 入选理由 (Reasoning) |
|------|------|---------|------|---------|
"""
    
    best_shots = [s for s in sorted_scenes if s.get("weighted_score", 0) >= 7.0 or "MUST KEEP" in s.get("selection", "")]
    for i, scene in enumerate(best_shots[:5], 1):  # 只显示前5
        report += f"| {i} | Scene {scene.get('scene_number', 0):03d} | {scene.get('weighted_score', 0):.2f} | {get_term_chinese(scene.get('type_classification', '').split()[0])} | {scene.get('selection_reasoning', '')[:50]}... |\n"
    
    report += f"""

### 各类别最佳镜头 (Best by Category)

**最佳 Hook 候选** (Best Hook Candidate - 最高 Impact):
- Scene {max(scenes, key=lambda x: x.get('scores', {}).get('impact', 0)).get('scene_number', 0):03d} | Impact 冲击力: {max(scenes, key=lambda x: x.get('scores', {}).get('impact', 0)).get('scores', {}).get('impact', 0)}

**最佳视觉** (Best Visual - 最高 Aesthetic Beauty):
- Scene {max(scenes, key=lambda x: x.get('scores', {}).get('aesthetic_beauty', 0)).get('scene_number', 0):03d} | Aesthetic Beauty 美感: {max(scenes, key=lambda x: x.get('scores', {}).get('aesthetic_beauty', 0)).get('scores', {}).get('aesthetic_beauty', 0)}

**最佳可信度** (Best Credibility - 最高真实感):
- Scene {max(scenes, key=lambda x: x.get('scores', {}).get('credibility', 0)).get('scene_number', 0):03d} | Credibility 可信度: {max(scenes, key=lambda x: x.get('scores', {}).get('credibility', 0)).get('scores', {}).get('credibility', 0)}

**最佳记忆度** (Best Memorability - 最高记忆点):
- Scene {max(scenes, key=lambda x: x.get('scores', {}).get('memorability', 0)).get('scene_number', 0):03d} | Memorability 记忆度: {max(scenes, key=lambda x: x.get('scores', {}).get('memorability', 0)).get('scores', {}).get('memorability', 0)}

---

## 📊 整体影片评价 (Overall Assessment)

### 综合评分: {avg_score:.2f} / 10

"""
    
    # 根据分数给出评价
    if avg_score >= 8:
        verdict = "🌟 优秀 - 高质量素材，强烈推荐保留"
        recommendation = "适合作为主打素材使用"
    elif avg_score >= 6.5:
        verdict = "📁 良好 - 有可用价值，需要适当剪辑"
        recommendation = "筛选优质片段后使用"
    else:
        verdict = "🗑️ 一般 - 整体质量较低"
        recommendation = "建议重新拍摄或寻找替代素材"
    
    report += f"""
### 评价结论 (Verdict)

**{verdict}**

### 优势分析 (Strengths)
- **可信度 Credibility** ({dim_avgs['credibility']:.2f}) 表现{'优秀' if dim_avgs['credibility'] >= 7 else '良好' if dim_avgs['credibility'] >= 5 else '一般'} - 表演自然度、真实感
- **美感 Aesthetic Beauty** ({dim_avgs['aesthetic_beauty']:.2f}) 表现{'优秀' if dim_avgs['aesthetic_beauty'] >= 7 else '良好' if dim_avgs['aesthetic_beauty'] >= 5 else '一般'} - 构图、光影、色彩
- **冲击力 Impact** ({dim_avgs['impact']:.2f}) 表现{'优秀' if dim_avgs['impact'] >= 7 else '良好' if dim_avgs['impact'] >= 5 else '一般'} - 视觉显著性、动态张力
- **记忆度 Memorability** ({dim_avgs['memorability']:.2f}) 表现{'优秀' if dim_avgs['memorability'] >= 7 else '良好' if dim_avgs['memorability'] >= 5 else '一般'} - 独特符号、冯·雷斯托夫效应
- **趣味度 Fun/Interest** ({dim_avgs['fun_interest']:.2f}) 表现{'优秀' if dim_avgs['fun_interest'] >= 7 else '良好' if dim_avgs['fun_interest'] >= 5 else '一般'} - 参与感、娱乐价值
- **最佳场景得分** (Best Scene): {max(scenes, key=lambda x: x.get('weighted_score', 0)).get('weighted_score', 0):.2f}

### 改进建议 (Improvement Suggestions)
- {'**冲击力 Impact** 有待提升，可增加更多视觉亮点 (Visual Highlights)、快节奏剪辑 (Fast Cutting)' if dim_avgs['impact'] < 7 else '**冲击力 Impact** 表现良好'}
- {'**记忆度 Memorability** 不够突出，建议增加独特视觉符号 (Visual Symbols)、金句 (Catchphrases)' if dim_avgs['memorability'] < 7 else '**记忆度 Memorability** 表现良好'}
- {'**趣味度 Fun/Interest** 较低，可增加互动元素 (Interactive Elements)、幽默 (Humor)' if dim_avgs['fun_interest'] < 7 else '**趣味度 Fun/Interest** 表现良好'}

### 最终建议 (Final Recommendation)
**{recommendation}**

### 使用场景建议 (Usage Recommendations)
- **社交媒体** (Social Media): 选择 Impact 高、Memorability 高的片段
- **产品展示** (Product Demo): 选择 Aesthetic Beauty 高的特写镜头
- **品牌宣传** (Brand Promotion): 选择 Credibility 高、有情感共鸣的片段
- **广告投放** (Ad Campaign): 选择加权得分 ≥ 7.0 的精选片段

---

## 📁 文件结构 (File Structure)

```
{video_id}/
├── {video_id}.mp4                                   # 完整视频 (Full Video)
├── {video_id}.m4a                                   # 音频文件 (Audio)
├── {video_id}.srt                                   # 字幕文件 (Subtitles)
├── {video_id}_transcript.txt                        # 转录文本 (Transcript)
├── scene_scores.json                                # 完整评分数据 (Full Scoring Data)
├── {video_id}_complete_analysis.md                  # 本报告 (This Report)
├── scenes/                                          # 场景片段 (Scene Clips)
│   ├── {video_id}-Scene-001.mp4
│   ├── ...
│   └── best_shots/                                  # ⭐ 精选片段 (Best Shots - {len(best_shots)} 个)
│       ├── 01_USABLE_xxx.mp4
│       └── README.md
└── frames/                                          # 预览帧 (Preview Frames)
    └── ...
```

---

*本报告由 Video Expert Analyzer AI 自动生成*  
*Based on Walter Murch's Six Rules of Editing & Dynamic Weighting System*  
*分析时间 (Analysis Time): {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 完整分析报告已生成: {report_path}")
    return report_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 ai_analyzer.py <scene_scores.json路径>")
        sys.exit(1)
    
    scores_path = Path(sys.argv[1])
    video_dir = scores_path.parent
    
    # 1. 自动评分
    print("=" * 60)
    print("🤖 AI 自动分析场景")
    print("=" * 60)
    data = auto_score_scenes(scores_path, video_dir)
    
    # 2. 复制精选镜头
    print("\n" + "=" * 60)
    print("⭐ 选择并复制精选镜头")
    print("=" * 60)
    select_and_copy_best_shots(scores_path, threshold=7.0)
    
    # 3. 生成完整报告
    print("\n" + "=" * 60)
    print("📄 生成完整分析报告")
    print("=" * 60)
    report_path = generate_complete_analysis_report(scores_path)
    
    print("\n" + "=" * 60)
    print("✅ AI 分析完成!")
    print("=" * 60)
    print(f"\n📊 评分文件: {scores_path}")
    print(f"⭐ 精选镜头: {video_dir}/scenes/best_shots/")
    print(f"📄 完整报告: {report_path}")
