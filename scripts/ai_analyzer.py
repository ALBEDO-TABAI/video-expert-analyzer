#!/usr/bin/env python3
"""
AI Scene Analyzer v2.0
支持三种评分模式：
  - API 模式：通过 OpenAI 兼容 API 调用 Gemini/Kimi 等视觉大模型（看单帧截图）
  - Agent 模式：由宿主 AI 助手（IDE/OpenClaw 中的多模态模型）直接看图评分
  - Pegasus 模式：通过 TwelveLabs Pegasus 分析完整场景视频片段（看动态视频，非单帧）

环境变量（API 模式）：
  VIDEO_ANALYZER_API_KEY   - API 密钥
  VIDEO_ANALYZER_BASE_URL  - API 端点 (默认 https://generativelanguage.googleapis.com/v1beta/openai)
  VIDEO_ANALYZER_MODEL     - 模型名称 (默认 gemini-2.0-flash)

环境变量（Pegasus 模式）：
  TWELVELABS_API_KEY       - TwelveLabs API 密钥（必需）
  TWELVELABS_PEGASUS_MODEL - Pegasus 模型名称 (默认 pegasus1.5)

Pegasus 模式与 API/Agent 模式的区别：API/Agent 只能看场景的一张静帧截图，
而 Pegasus 直接理解整段场景视频（含运镜、节奏、动态张力），更贴合 Walter Murch
剪辑六法则中对"节奏"与"冲击力"的时序判断。完全可选：未配置 TWELVELABS_API_KEY
时行为不变。免费 API key 见 https://twelvelabs.io 。
"""

import json
import base64
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# ============================================================
# 术语对照表
# ============================================================
TERMINOLOGY = {
    "TYPE-A Hook": "TYPE-A Hook (钩子/开场型)",
    "TYPE-B Narrative": "TYPE-B Narrative (叙事/情感型)",
    "TYPE-C Aesthetic": "TYPE-C Aesthetic (氛围/空镜型)",
    "TYPE-D Commercial": "TYPE-D Commercial (商业/展示型)",
    "aesthetic_beauty": "美感 Aesthetic Beauty (构图/光影/色彩)",
    "credibility": "可信度 Credibility (真实感/表演自然度)",
    "impact": "冲击力 Impact (视觉显著性/动态张力)",
    "memorability": "记忆度 Memorability (独特符号/金句)",
    "fun_interest": "趣味度 Fun/Interest (参与感/娱乐价值)",
    "MUST KEEP": "MUST KEEP (强烈推荐保留)",
    "USABLE": "USABLE (可用素材)",
    "DISCARD": "DISCARD (建议舍弃)",
}


def get_term_chinese(term: str) -> str:
    return TERMINOLOGY.get(term, term)


# ============================================================
# System Prompt for Vision LLM
# ============================================================
SCORING_SYSTEM_PROMPT = """你是一位专业的视频剪辑/镜头分析专家，精通 Walter Murch 剪辑六法则。

你需要分析一张视频截帧，按以下维度打分（1-10 整数）：

1. **aesthetic_beauty** (美感): 构图（如三分法/对称）、光影质感、色彩和谐度
2. **credibility** (可信度): 画面真实感、物理逻辑、AI生成痕迹程度（痕迹越少分越高）
3. **impact** (冲击力): 第一眼视觉显著性、动态张力、能否瞬间吸引观众
4. **memorability** (记忆度): 独特视觉符号、冯·雷斯托夫效应、过目不忘程度
5. **fun_interest** (趣味度): 参与感、娱乐价值、社交货币潜力

同时判断场景类型：
- TYPE-A Hook: 高冲击力开场/高能片段
- TYPE-B Narrative: 叙事/情感表达
- TYPE-C Aesthetic: 空镜/氛围/纯美学
- TYPE-D Commercial: 产品展示/商业广告

你必须严格按以下 JSON 格式返回结果，不要附加任何其他文字：
```json
{
  "type_classification": "TYPE-X ...",
  "description": "一句话中文描述画面内容",
  "visual_summary": "视觉元素概要",
  "scores": {
    "aesthetic_beauty": 8,
    "credibility": 7,
    "impact": 9,
    "memorability": 8,
    "fun_interest": 7
  },
  "selection_reasoning": "入选/淘汰理由（中文）",
  "edit_suggestion": "剪辑建议（中文）"
}
```"""


SCORING_USER_PROMPT_TEMPLATE = """请分析以下视频的第 {scene_num} 个场景截帧。

视频标题：{video_title}
视频总场景数：{total_scenes}
{transcript_info}

请严格按 JSON 格式返回分析结果。"""


# ============================================================
# API 模式：调用远程视觉大模型
# ============================================================
def call_vision_api(
    frame_path: Path,
    scene_num: int,
    video_title: str = "",
    total_scenes: int = 0,
    transcript_text: str = "",
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> Optional[Dict]:
    """通过 OpenAI 兼容 API 调用视觉大模型分析帧画面"""

    try:
        from openai import OpenAI
    except ImportError:
        print("   ⚠️  需要安装 openai 库: pip install openai")
        return None

    if not api_key:
        print("   ⚠️  未设置 VIDEO_ANALYZER_API_KEY 环境变量")
        return None

    # 读取图片并转 base64
    with open(frame_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    mime_type = "image/jpeg" if frame_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"

    transcript_info = f"对应转录文本片段：{transcript_text}" if transcript_text else "（该场景无转录文本）"

    user_prompt = SCORING_USER_PROMPT_TEMPLATE.format(
        scene_num=scene_num,
        video_title=video_title,
        total_scenes=total_scenes,
        transcript_info=transcript_info,
    )

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SCORING_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}",
                            },
                        },
                    ],
                },
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        content = response.choices[0].message.content.strip()

        # 提取 JSON（可能包裹在 ```json ... ``` 中）
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"   ⚠️  Scene {scene_num:03d}: 无法解析模型返回的 JSON")
            return None

    except Exception as e:
        print(f"   ⚠️  Scene {scene_num:03d}: API 调用失败 - {e}")
        return None


# ============================================================
# Pegasus 模式：调用 TwelveLabs Pegasus 分析完整场景视频片段
# ============================================================
# Pegasus 1.5 不接受裸 video_id，需要可访问的 URL 或已上传的 asset_id。
# 场景片段是本地 mp4，因此先用 direct 上传为 asset（<=200MB），再用 asset_id 分析。
PEGASUS_MAX_DIRECT_UPLOAD_MB = 200  # /v1.3/assets method=direct 上限；公网 URL 可至 4GB
PEGASUS_MIN_TOKENS = 512  # Pegasus max_tokens 下限（API 要求）


def call_pegasus_video(
    clip_path: Path,
    scene_num: int,
    video_title: str = "",
    total_scenes: int = 0,
    transcript_text: str = "",
    api_key: str = "",
    model: str = "pegasus1.5",
    client=None,
) -> Optional[Dict]:
    """通过 TwelveLabs Pegasus 分析整段场景视频片段并按五维度打分。

    与 call_vision_api 不同，Pegasus 看的是动态视频（含运镜/节奏），而非单帧截图。
    返回结构与 call_vision_api 一致（含 scores/type_classification 等），便于复用下游逻辑。
    """
    try:
        from twelvelabs import TwelveLabs
        from twelvelabs.types.video_context import VideoContext_AssetId
    except ImportError:
        print("   ⚠️  需要安装 twelvelabs 库: pip install 'twelvelabs>=1.2.8'")
        return None

    if not api_key:
        print("   ⚠️  未设置 TWELVELABS_API_KEY 环境变量")
        return None

    if not clip_path.exists():
        print(f"   ⚠️  Scene {scene_num:03d}: 未找到场景视频片段 {clip_path}")
        return None

    size_mb = clip_path.stat().st_size / (1024 * 1024)
    if size_mb > PEGASUS_MAX_DIRECT_UPLOAD_MB:
        print(
            f"   ⚠️  Scene {scene_num:03d}: 片段 {size_mb:.0f}MB 超过 direct 上传上限 "
            f"({PEGASUS_MAX_DIRECT_UPLOAD_MB}MB)，跳过（如需分析请改用公网 URL）"
        )
        return None

    transcript_info = f"对应转录文本片段：{transcript_text}" if transcript_text else "（该场景无转录文本）"
    user_prompt = SCORING_SYSTEM_PROMPT + "\n\n" + SCORING_USER_PROMPT_TEMPLATE.format(
        scene_num=scene_num,
        video_title=video_title,
        total_scenes=total_scenes,
        transcript_info=transcript_info,
    )

    if client is None:
        client = TwelveLabs(api_key=api_key)

    try:
        # 1. 上传场景片段为 asset
        with open(clip_path, "rb") as f:
            asset = client.assets.create(method="direct", file=f, filename=clip_path.name)

        # 2. 轮询 asset 直到 ready（上传后需短暂转码）
        for _ in range(60):
            current = client.assets.retrieve(asset_id=asset.id)
            status = getattr(current, "status", None)
            if status != "processing":
                break
            time.sleep(5)
        if status == "failed":
            print(f"   ⚠️  Scene {scene_num:03d}: asset 处理失败")
            return None

        # 3. Pegasus 分析整段视频
        response = client.analyze(
            model_name=model,
            video=VideoContext_AssetId(asset_id=asset.id),
            prompt=user_prompt,
            max_tokens=PEGASUS_MIN_TOKENS,
            temperature=0.3,
        )
        content = (response.data or "").strip()

        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            return json.loads(json_match.group())
        print(f"   ⚠️  Scene {scene_num:03d}: 无法解析 Pegasus 返回的 JSON")
        return None

    except Exception as e:
        print(f"   ⚠️  Scene {scene_num:03d}: Pegasus 调用失败 - {e}")
        return None


# ============================================================
# 加权评分计算
# ============================================================
def compute_weighted_score(analysis: Dict) -> Dict:
    """根据场景类型计算加权分数并确定筛选等级"""

    scores = analysis.get("scores", {})
    type_class = analysis.get("type_classification", "")

    # 根据类型动态调整权重
    if "TYPE-A" in type_class:
        weighted = (
            scores.get("impact", 5) * 0.40
            + scores.get("memorability", 5) * 0.30
            + scores.get("aesthetic_beauty", 5) * 0.20
            + scores.get("fun_interest", 5) * 0.10
        )
    elif "TYPE-B" in type_class:
        weighted = (
            scores.get("credibility", 5) * 0.40
            + scores.get("memorability", 5) * 0.30
            + scores.get("aesthetic_beauty", 5) * 0.20
            + scores.get("fun_interest", 5) * 0.10
        )
    elif "TYPE-C" in type_class:
        weighted = (
            scores.get("aesthetic_beauty", 5) * 0.50
            + scores.get("impact", 5) * 0.20
            + scores.get("memorability", 5) * 0.20
            + scores.get("credibility", 5) * 0.10
        )
    else:  # TYPE-D Commercial
        weighted = (
            scores.get("credibility", 5) * 0.40
            + scores.get("memorability", 5) * 0.40
            + scores.get("aesthetic_beauty", 5) * 0.20
        )

    analysis["weighted_score"] = round(weighted, 2)

    # 确定筛选等级
    if weighted >= 8.5 or any(v == 10 for v in scores.values()):
        analysis["selection"] = "[MUST KEEP]"
    elif weighted >= 7.0:
        analysis["selection"] = "[USABLE]"
    else:
        analysis["selection"] = "[DISCARD]"

    return analysis


# ============================================================
# Pegasus 评分主循环
# ============================================================
def _score_with_pegasus(
    data: Dict,
    scores_path: Path,
    scenes: List[Dict],
    video_title: str,
    total_scenes: int,
    transcript_text: str,
) -> Dict:
    """用 TwelveLabs Pegasus 逐场景分析完整视频片段并写回 scores_path。"""
    api_key = os.environ.get("TWELVELABS_API_KEY", "")
    model = os.environ.get("TWELVELABS_PEGASUS_MODEL", "pegasus1.5")

    if not api_key:
        print("\n❌ Pegasus 模式需要设置环境变量 TWELVELABS_API_KEY")
        print('   export TWELVELABS_API_KEY="your-api-key"')
        print("   免费 API key: https://twelvelabs.io")
        sys.exit(1)

    try:
        from twelvelabs import TwelveLabs
    except ImportError:
        print("\n❌ Pegasus 模式需要安装 twelvelabs: pip install 'twelvelabs>=1.2.8'")
        sys.exit(1)

    client = TwelveLabs(api_key=api_key)
    print(f"\n🐎 Pegasus 模式：使用 {model} 分析 {total_scenes} 个场景视频片段...")

    success_count = 0
    for scene in scenes:
        scene_num = scene.get("scene_number", 0)
        clip_path = Path(scene.get("file_path", ""))
        if not clip_path.exists():
            print(f"  Scene {scene_num:03d}: ⚠️ 未找到场景片段，跳过")
            continue

        analysis = call_pegasus_video(
            clip_path=clip_path,
            scene_num=scene_num,
            video_title=video_title,
            total_scenes=total_scenes,
            transcript_text=transcript_text[:500] if transcript_text else "",
            api_key=api_key,
            model=model,
            client=client,
        )

        if analysis:
            analysis = compute_weighted_score(analysis)
            scene.update(analysis)
            success_count += 1
            print(f"  Scene {scene_num:03d}: {analysis['selection']} | 加权 {analysis['weighted_score']:.2f} | {analysis.get('type_classification', 'N/A')}")
        else:
            print(f"  Scene {scene_num:03d}: ❌ 分析失败")

    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Pegasus 评分完成：{success_count}/{total_scenes} 个场景成功")
    print(f"   已保存到: {scores_path}")
    return data


# ============================================================
# 主流程：自动评分
# ============================================================
def auto_score_scenes(scores_path: Path, video_analysis_dir: Path, mode: str = "api") -> Dict:
    """自动为所有场景评分。
    mode='api'     远程视觉 API（看单帧）
    mode='agent'   生成模板供宿主 AI 填写
    mode='pegasus' TwelveLabs Pegasus（看完整场景视频片段）
    """

    with open(scores_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data.get("scenes", [])
    frames_dir = video_analysis_dir / "frames"
    video_title = data.get("title", data.get("video_id", ""))
    total_scenes = len(scenes)

    # 读取转录文本
    transcript_text = ""
    for ext in ["_transcript.txt", ".srt"]:
        transcript_file = video_analysis_dir / f"{data.get('video_id', '')}{ext}"
        if transcript_file.exists():
            transcript_text = transcript_file.read_text(encoding="utf-8")
            break

    if mode == "agent":
        print(f"\n📋 Agent 模式：已准备 {total_scenes} 个场景的评分模板")
        print(f"   帧图片目录: {frames_dir}")
        print(f"   请使用宿主 AI 的视觉能力逐帧查看并填写评分")
        print(f"   评分结果写入: {scores_path}")
        return data

    if mode == "pegasus":
        return _score_with_pegasus(data, scores_path, scenes, video_title, total_scenes, transcript_text)

    # API 模式
    api_key = os.environ.get("VIDEO_ANALYZER_API_KEY", "")
    base_url = os.environ.get("VIDEO_ANALYZER_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai")
    model = os.environ.get("VIDEO_ANALYZER_MODEL", "gemini-2.0-flash")

    if not api_key:
        print("\n❌ API 模式需要设置环境变量 VIDEO_ANALYZER_API_KEY")
        print("   export VIDEO_ANALYZER_API_KEY=\"your-api-key\"")
        print("   export VIDEO_ANALYZER_BASE_URL=\"https://...\"  # 可选")
        print("   export VIDEO_ANALYZER_MODEL=\"gemini-2.0-flash\"  # 可选")
        sys.exit(1)

    print(f"\n🤖 API 模式：使用 {model} 分析 {total_scenes} 个场景...")
    print(f"   API: {base_url}")

    success_count = 0
    for scene in scenes:
        scene_num = scene.get("scene_number", 0)
        frame_name = scene.get("filename", "").replace(".mp4", ".jpg")
        frame_path = frames_dir / frame_name

        if not frame_path.exists():
            # 尝试其他命名
            alt_name = f"{data.get('video_id', '')}-Scene-{scene_num:03d}.jpg"
            frame_path = frames_dir / alt_name

        if not frame_path.exists():
            print(f"  Scene {scene_num:03d}: ⚠️ 未找到帧图片，跳过")
            continue

        analysis = call_vision_api(
            frame_path=frame_path,
            scene_num=scene_num,
            video_title=video_title,
            total_scenes=total_scenes,
            transcript_text=transcript_text[:500] if transcript_text else "",
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        if analysis:
            analysis = compute_weighted_score(analysis)
            scene.update(analysis)
            success_count += 1
            print(f"  Scene {scene_num:03d}: {analysis['selection']} | 加权 {analysis['weighted_score']:.2f} | {analysis.get('type_classification', 'N/A')}")
        else:
            print(f"  Scene {scene_num:03d}: ❌ 分析失败")

        # 限流：每次请求间隔
        time.sleep(1.0)

    # 保存
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 评分完成：{success_count}/{total_scenes} 个场景成功")
    print(f"   已保存到: {scores_path}")
    return data


# ============================================================
# 精选镜头筛选与复制
# ============================================================
def select_and_copy_best_shots(scores_path: Path, threshold: float = 7.0) -> List[Dict]:
    """选择最佳镜头并复制到 best_shots 目录"""

    with open(scores_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data.get("scenes", [])
    video_dir = scores_path.parent
    best_shots_dir = video_dir / "scenes" / "best_shots"
    best_shots_dir.mkdir(exist_ok=True)

    # 清空旧的精选
    for old in best_shots_dir.glob("*.mp4"):
        old.unlink()

    # 筛选
    best_shots = [
        s for s in scenes
        if s.get("weighted_score", 0) >= threshold or "MUST KEEP" in s.get("selection", "")
    ]
    best_shots.sort(key=lambda x: x.get("weighted_score", 0), reverse=True)

    print(f"\n⭐ 发现 {len(best_shots)} 个精选镜头 (阈值: {threshold})")

    copied = []
    for i, scene in enumerate(best_shots, 1):
        src_path = Path(scene.get("file_path", ""))
        if src_path.exists():
            tag = scene.get("selection", "").replace("[", "").replace("]", "").replace(" ", "_")
            dst_name = f"{i:02d}_{tag}_{src_path.name}"
            dst_path = best_shots_dir / dst_name
            shutil.copy2(src_path, dst_path)
            copied.append(scene)
            desc = scene.get("description", "N/A")[:30]
            print(f"  {i}. Scene {scene.get('scene_number', 0):03d} | {scene.get('weighted_score', 0):.2f} | {desc}...")

    # 生成 README
    _generate_readme(best_shots_dir, copied, data.get("video_id", "unknown"))

    print(f"\n✅ 已复制 {len(copied)} 个精选镜头到: {best_shots_dir}")
    return copied


def _generate_readme(best_shots_dir: Path, best_shots: List[Dict], video_id: str):
    content = f"""# ⭐ 精选镜头 (Best Shots)

**视频 ID**: {video_id}
**入选数量**: {len(best_shots)} 个
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 精选列表

| 排名 | 场景 | 加权分 | 类型 | 描述 |
|------|------|--------|------|------|
"""
    for i, s in enumerate(best_shots, 1):
        content += f"| {i} | Scene {s.get('scene_number', 0):03d} | {s.get('weighted_score', 0):.2f} | {s.get('type_classification', 'N/A')} | {s.get('description', '')[:40]} |\n"

    content += f"\n---\n*由 Video Expert Analyzer v2.0 筛选*\n"

    (best_shots_dir / "README.md").write_text(content, encoding="utf-8")


# ============================================================
# 分析报告生成
# ============================================================
def generate_complete_report(scores_path: Path) -> Path:
    with open(scores_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    video_id = data.get("video_id", "unknown")
    url = data.get("url", "")
    scenes = data.get("scenes", [])
    total = len(scenes)

    if total == 0:
        print("⚠️ 没有场景数据")
        return scores_path

    # 统计
    scored_scenes = [s for s in scenes if "weighted_score" in s]
    if not scored_scenes:
        print("⚠️ 没有已评分的场景")
        return scores_path

    must_keep = sum(1 for s in scored_scenes if "MUST KEEP" in s.get("selection", ""))
    usable = sum(1 for s in scored_scenes if "USABLE" in s.get("selection", ""))
    discard = sum(1 for s in scored_scenes if "DISCARD" in s.get("selection", ""))
    avg = sum(s["weighted_score"] for s in scored_scenes) / len(scored_scenes)

    # 各维度平均
    dims = ["aesthetic_beauty", "credibility", "impact", "memorability", "fun_interest"]
    dim_avgs = {}
    for d in dims:
        vals = [s.get("scores", {}).get(d, 0) for s in scored_scenes if s.get("scores", {}).get(d)]
        dim_avgs[d] = sum(vals) / len(vals) if vals else 0

    report_path = scores_path.parent / f"{video_id}_complete_analysis.md"

    sorted_scenes = sorted(scored_scenes, key=lambda x: x.get("weighted_score", 0), reverse=True)

    # 构建报告
    report = f"""# 🎬 视频专家分析报告 (Video Expert Analysis Report)

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **视频 ID** | {video_id} |
| **来源 URL** | {url} |
| **分析时间** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **总场景数** | {total} |
| **已评分** | {len(scored_scenes)} |
| **平均加权得分** | {avg:.2f} |

### 筛选统计

| 等级 | 数量 | 占比 |
|------|------|------|
| 🌟 MUST KEEP | {must_keep} | {must_keep/len(scored_scenes)*100:.1f}% |
| 📁 USABLE | {usable} | {usable/len(scored_scenes)*100:.1f}% |
| 🗑️ DISCARD | {discard} | {discard/len(scored_scenes)*100:.1f}% |

### 各维度平均分

| 维度 | 平均分 |
|------|--------|
"""
    for d in dims:
        icon = "🟢" if dim_avgs[d] >= 7 else "🟡" if dim_avgs[d] >= 5 else "🔴"
        report += f"| {get_term_chinese(d)} | {dim_avgs[d]:.2f} {icon} |\n"

    report += f"""
---

## 🎞 场景排名

| 排名 | 场景 | 加权分 | 类型 | 等级 | 描述 |
|------|------|--------|------|------|------|
"""
    for i, s in enumerate(sorted_scenes, 1):
        desc = s.get("description", "N/A")[:30]
        report += f"| {i} | Scene {s.get('scene_number', 0):03d} | **{s.get('weighted_score', 0):.2f}** | {s.get('type_classification', 'N/A')} | {s.get('selection', '')} | {desc} |\n"

    report += f"""
---

## 📊 整体评价

### 综合评分: {avg:.2f} / 10

"""
    if avg >= 8:
        report += "🌟 **优秀** - 高质量素材，强烈推荐保留\n"
    elif avg >= 6.5:
        report += "📁 **良好** - 有可用价值，需要适当剪辑\n"
    else:
        report += "🗑️ **一般** - 整体质量较低\n"

    report += f"""
---
*本报告由 Video Expert Analyzer v2.0 自动生成*
*分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    report_path.write_text(report, encoding="utf-8")
    print(f"✅ 完整分析报告已生成: {report_path}")
    return report_path


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""用法: python3 ai_analyzer.py <scene_scores.json> [--mode api|agent|pegasus]

评分模式:
  --mode api      通过远程 API 调用视觉大模型评分（看单帧，需 VIDEO_ANALYZER_API_KEY）
  --mode agent    生成评分模板，由宿主 AI 助手（如 IDE 中的 Gemini/Kimi）直接看图评分
  --mode pegasus  通过 TwelveLabs Pegasus 分析完整场景视频片段（看动态视频，需 TWELVELABS_API_KEY）

环境变量 (API 模式):
  VIDEO_ANALYZER_API_KEY    API 密钥（必需）
  VIDEO_ANALYZER_BASE_URL   API 端点（默认 Gemini）
  VIDEO_ANALYZER_MODEL      模型名称（默认 gemini-2.0-flash）

环境变量 (Pegasus 模式):
  TWELVELABS_API_KEY        TwelveLabs API 密钥（必需，免费 key: https://twelvelabs.io）
  TWELVELABS_PEGASUS_MODEL  Pegasus 模型名称（默认 pegasus1.5）
""")
        sys.exit(1)

    scores_path = Path(sys.argv[1])
    video_dir = scores_path.parent

    # 解析模式
    mode = "api"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    print("=" * 60)
    print(f"🤖 AI Scene Analyzer v2.0 ({mode.upper()} 模式)")
    print("=" * 60)

    # 1. 自动评分
    data = auto_score_scenes(scores_path, video_dir, mode=mode)

    if mode == "agent":
        print("\n" + "=" * 60)
        print("📝 Agent 模式说明")
        print("=" * 60)
        print(f"\n请使用宿主 AI 助手的视觉能力完成以下步骤：")
        print(f"  1. 查看 {video_dir}/frames/ 中的每张截帧")
        print(f"  2. 按 Walter Murch 法则五维度打分")
        print(f"  3. 将结果更新到 {scores_path}")
        print(f"  4. 再次运行本脚本（不带 --mode agent）生成报告")
        sys.exit(0)

    # 2. 复制精选镜头
    print("\n" + "=" * 60)
    print("⭐ 选择并复制精选镜头")
    print("=" * 60)
    select_and_copy_best_shots(scores_path, threshold=7.0)

    # 3. 生成完整报告
    print("\n" + "=" * 60)
    print("📄 生成完整分析报告")
    print("=" * 60)
    report_path = generate_complete_report(scores_path)

    print("\n" + "=" * 60)
    print("✅ AI 分析完成!")
    print("=" * 60)
    print(f"\n📊 评分文件: {scores_path}")
    print(f"⭐ 精选镜头: {video_dir}/scenes/best_shots/")
    print(f"📄 完整报告: {report_path}")
