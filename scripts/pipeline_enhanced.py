#!/usr/bin/env python3
"""
Video Expert Analyzer Pipeline - Enhanced Version
支持：配置目录选择、精选片段子文件夹、详细分析报告
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import re
import requests
from urllib.parse import unquote
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import download_douyin as DouyinDownloader
except ImportError:
    # 如果直接运行脚本，添加当前目录到路径
    sys.path.insert(0, str(Path(__file__).parent))
    import download_douyin as DouyinDownloader


# 配置文件路径
CONFIG_DIR = Path.home() / ".config" / "video-expert-analyzer"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Dict:
    """加载用户配置，如果不存在则创建默认配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 默认配置
    default_config = {
        "output_base_dir": str(Path.home() / "Downloads" / "video-analysis"),
        "first_run": True,
        "default_scene_threshold": 27.0
    }
    
    save_config(default_config)
    return default_config


def save_config(config: Dict):
    """保存用户配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_video_info(url: str) -> Dict:
    """
    使用 yt-dlp 获取视频信息（标题、作者等）
    抖音链接使用专用方法获取
    """
    # 抖音链接使用专用方法
    if DouyinDownloader.is_douyin_url(url):
        return get_douyin_video_info(url)
    
    # 其他平台使用yt-dlp
    try:
        cmd = [
            "yt-dlp",
            "--print", "%(title)s",
            "--print", "%(uploader)s",
            "--print", "%(channel)s",
            "--print", "%(duration)s",
            "--print", "%(view_count)s",
            "--no-download",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {
                "title": lines[0] if len(lines) > 0 else "",
                "uploader": lines[1] if len(lines) > 1 else "",
                "channel": lines[2] if len(lines) > 2 else "",
                "duration": lines[3] if len(lines) > 3 else "",
                "view_count": lines[4] if len(lines) > 4 else "",
                "success": True
            }
    except Exception as e:
        print(f"   ⚠️  获取视频信息失败: {e}")
    
    return {"success": False, "title": "", "uploader": ""}


def get_douyin_video_info(url: str) -> Dict:
    """
    获取抖音视频信息
    """
    try:
        downloader = DouyinDownloader()
        
        # 获取重定向后的URL
        full_url, user_agent = downloader.get_redirect_url(url)
        if not full_url:
            return {"success": False, "title": "", "uploader": ""}
        
        # 获取页面HTML
        session = requests.Session()
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
        
        response = session.get(full_url, timeout=15)
        html = response.text
        
        # 提取RENDER_DATA
        render_data = downloader.extract_render_data(html)
        if not render_data:
            return {"success": False, "title": "", "uploader": ""}
        
        # 解析JSON获取视频信息
        if '%' in render_data:
            decoded = unquote(render_data)
        else:
            decoded = render_data
        
        data = json.loads(decoded)
        
        # 尝试提取标题和作者
        title = ""
        uploader = ""
        
        # 常见路径
        possible_title_paths = [
            ['loaderData', 'video_(id)/page', 'videoInfoRes', 'item_list', 0, 'desc'],
            ['loaderData', 'video_(id)/page', 'aweme_detail', 'desc'],
            ['app', 'videoDetail', 'desc'],
            ['app', 'videoInfoRes', 'item_list', 0, 'desc'],
        ]
        
        possible_author_paths = [
            ['loaderData', 'video_(id)/page', 'videoInfoRes', 'item_list', 0, 'author', 'nickname'],
            ['loaderData', 'video_(id)/page', 'aweme_detail', 'author', 'nickname'],
            ['app', 'videoDetail', 'author', 'nickname'],
            ['app', 'videoInfoRes', 'item_list', 0, 'author', 'nickname'],
        ]
        
        def get_nested(obj, path):
            current = obj
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                elif isinstance(current, list) and isinstance(key, int) and key < len(current):
                    current = current[key]
                else:
                    return None
            return current
        
        for path in possible_title_paths:
            title = get_nested(data, path)
            if title:
                break
        
        for path in possible_author_paths:
            uploader = get_nested(data, path)
            if uploader:
                break
        
        # 如果找不到标题，使用URL作为标题
        if not title:
            title = f"抖音视频_{url.split('/')[-1][:20]}"
        
        return {
            "success": True,
            "title": title or "抖音视频",
            "uploader": uploader or "未知作者",
            "channel": uploader or "",
            "duration": "",
            "view_count": "",
            "platform": "douyin"
        }
        
    except Exception as e:
        print(f"   ⚠️  获取抖音视频信息失败: {e}")
        return {"success": False, "title": "", "uploader": ""}


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    清理文件名，移除非法字符并限制长度
    """
    # 移除非法字符
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    # 移除多余空格
    name = re.sub(r'\s+', ' ', name).strip()
    
    # 如果超长，截取前max_length个字符
    if len(name) > max_length:
        name = name[:max_length].strip()
    
    return name


def generate_folder_name(video_info: Dict, video_id: str, max_length: int = 60) -> str:
    """
    生成视频文件夹名称
    格式: [作者] - [标题] 或 [标题]
    如果超长则提取关键字
    """
    title = video_info.get("title", "")
    uploader = video_info.get("uploader", "") or video_info.get("channel", "")
    
    if not title:
        return video_id
    
    # 清理标题
    title = sanitize_filename(title, max_length=100)
    uploader = sanitize_filename(uploader, max_length=30)
    
    # 生成文件夹名
    if uploader:
        folder_name = f"[{uploader}] {title}"
    else:
        folder_name = title
    
    # 如果超长，使用作者+简写标题
    if len(folder_name) > max_length:
        # 提取标题前30个字符
        short_title = title[:30].strip()
        if uploader:
            folder_name = f"[{uploader}] {short_title}"
        else:
            folder_name = short_title
    
    # 最终清理
    folder_name = folder_name.strip()
    if not folder_name:
        folder_name = video_id
    
    return folder_name


def setup_output_directory() -> str:
    """交互式设置输出目录"""
    config = load_config()
    
    print("=" * 60)
    print("📁 输出目录配置")
    print("=" * 60)
    
    if config.get("first_run", True):
        print("\n🎉 欢迎使用 Video Expert Analyzer!")
        print("请设置视频分析和输出的默认目录\n")
    else:
        print(f"\n当前默认输出目录: {config['output_base_dir']}")
    
    print("\n选项:")
    print("  1. 使用当前目录")
    print("  2. 使用默认目录 (~/Downloads/video-analysis)")
    print("  3. 自定义目录")
    
    if not config.get("first_run", True):
        print("  4. 修改当前默认目录")
    
    try:
        choice = input("\n请选择 [1-4]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return config['output_base_dir']
    
    if choice == "1":
        output_dir = config['output_base_dir']
    elif choice == "2":
        output_dir = str(Path.home() / "Downloads" / "video-analysis")
        config['output_base_dir'] = output_dir
        save_config(config)
    elif choice == "3":
        try:
            custom_dir = input("请输入自定义目录路径: ").strip()
            output_dir = custom_dir
            config['output_base_dir'] = output_dir
            config['first_run'] = False
            save_config(config)
        except (EOFError, KeyboardInterrupt):
            output_dir = config['output_base_dir']
    elif choice == "4" and not config.get("first_run", True):
        try:
            new_dir = input("请输入新的默认目录路径: ").strip()
            config['output_base_dir'] = new_dir
            save_config(config)
            output_dir = new_dir
        except (EOFError, KeyboardInterrupt):
            output_dir = config['output_base_dir']
    else:
        output_dir = config['output_base_dir']
    
    if config.get("first_run", True):
        config['first_run'] = False
        save_config(config)
    
    print(f"\n✅ 输出目录: {output_dir}")
    return output_dir


def get_output_directory() -> str:
    """获取当前配置的输出目录（非交互式）"""
    config = load_config()
    return config['output_base_dir']


class VideoAnalysisPipeline:
    """增强版视频分析管道"""

    def __init__(self, url: str, output_dir: str,
                 scene_threshold: float = 27.0,
                 extract_scenes: bool = True,
                 auto_select_best: bool = True,
                 best_threshold: float = 7.5):
        self.url = url
        self.output_dir = Path(output_dir).resolve()
        self.scene_threshold = scene_threshold
        self.extract_scenes = extract_scenes
        self.auto_select_best = auto_select_best
        self.best_threshold = best_threshold

        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 提取视频 ID
        self.video_id = self._extract_video_id(url)
        
        # 获取视频信息（标题、作者等）
        print("\n📋 正在获取视频信息...")
        self.video_info = get_video_info(url)
        
        if self.video_info.get("success"):
            print(f"   标题: {self.video_info.get('title', 'N/A')[:60]}...")
            print(f"   作者: {self.video_info.get('uploader', 'N/A')}")
            
            # 生成以标题命名的文件夹名
            self.folder_name = generate_folder_name(self.video_info, self.video_id)
            print(f"   文件夹: {self.folder_name}")
        else:
            print("   ⚠️  无法获取视频信息，使用视频 ID 作为文件夹名")
            self.folder_name = self.video_id
            self.video_info = {"title": self.video_id, "uploader": ""}
        
        # 创建视频专属子目录（使用标题命名）
        self.video_output_dir = self.output_dir / self.folder_name
        self.video_output_dir.mkdir(parents=True, exist_ok=True)

        # Define output paths
        self.video_path = self.video_output_dir / f"{self.video_id}.mp4"
        self.audio_path = self.video_output_dir / f"{self.video_id}.m4a"
        self.srt_path = self.video_output_dir / f"{self.video_id}.srt"
        self.transcript_path = self.video_output_dir / f"{self.video_id}_transcript.txt"
        self.scenes_dir = self.video_output_dir / "scenes"
        self.best_shots_dir = self.scenes_dir / "best_shots"
        self.frames_dir = self.video_output_dir / "frames"
        self.scores_path = self.video_output_dir / "scene_scores.json"
        self.report_path = self.video_output_dir / f"{self.video_id}_analysis_report.md"
        self.detailed_report_path = self.video_output_dir / f"{self.video_id}_detailed_analysis.md"

        # Results tracking
        self.results = {
            "video_id": self.video_id,
            "video_title": self.video_info.get("title", ""),
            "video_uploader": self.video_info.get("uploader", ""),
            "folder_name": self.folder_name,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "initialized",
            "steps_completed": [],
            "scene_analysis": [],
            "overall_assessment": {}
        }

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from URL"""
        if "bilibili.com" in url:
            if "/video/" in url:
                parts = url.split("/video/")[1].split("/")[0].split("?")[0]
                return parts
        if "youtube.com" in url or "youtu.be" in url:
            if "v=" in url:
                return url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]
        if "douyin.com" in url or "iesdouyin.com" in url:
            # 抖音视频ID提取
            if "modal_id=" in url:
                return url.split("modal_id=")[1].split("&")[0]
            if "/video/" in url:
                return url.split("/video/")[1].split("/")[0].split("?")[0]
            # 短链接使用URL的hash作为ID
            import hashlib
            return f"douyin_{hashlib.md5(url.encode()).hexdigest()[:12]}"
        return f"video_{int(datetime.now().timestamp())}"

    def run(self) -> Dict:
        """Execute the complete pipeline"""
        print("=" * 60)
        print("🎬 VIDEO EXPERT ANALYZER PIPELINE")
        print("=" * 60)
        print(f"📺 视频标题: {self.video_info.get('title', 'N/A')[:50]}...")
        print(f"👤 视频作者: {self.video_info.get('uploader', 'N/A')}")
        print(f"🔗 Video URL: {self.url}")
        print(f"📁 Output Dir: {self.video_output_dir}")
        print(f"🆔 Video ID: {self.video_id}")
        print("=" * 60)

        try:
            self._step_download_video()
            self._step_download_audio()
            scene_info = self._step_scene_detection()
            transcript_info = self._step_transcription()
            self._step_extract_frames(scene_info)
            self._step_prepare_scoring(scene_info)
            self._step_ai_scene_analysis(scene_info)
            if self.auto_select_best:
                self._step_auto_select_best_shots(scene_info)
            self._step_generate_detailed_report(scene_info, transcript_info)

            self.results["status"] = "completed"
            print("\n" + "=" * 60)
            print("✅ PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"\n📁 所有文件保存在: {self.video_output_dir}")
            print(f"📄 详细分析报告: {self.detailed_report_path}")
            return self.results

        except Exception as e:
            self.results["status"] = "failed"
            self.results["error"] = str(e)
            print(f"\n❌ PIPELINE FAILED: {e}")
            raise

    def _step_download_video(self):
        print("\n📥 Step 1: Downloading video...")
        if self.video_path.exists():
            print(f"   ⚠️  Video already exists: {self.video_path}")
            self.results["steps_completed"].append("download_video")
            return
        
        # 检查是否为抖音链接，使用专用下载器
        if DouyinDownloader.is_douyin_url(self.url):
            print("   🔍 检测到抖音视频链接")
            downloader = DouyinDownloader()
            success = downloader.download(self.url, self.video_path)
            if not success:
                raise RuntimeError("抖音视频下载失败")
        else:
            # 使用yt-dlp下载其他平台视频
            cmd = ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "-o", str(self.video_path), self.url]
            subprocess.run(cmd, check=True)
        
        if not self.video_path.exists():
            raise RuntimeError("Video download failed - file not found")
        file_size = self.video_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Video downloaded: {file_size:.2f} MB")
        self.results["video_path"] = str(self.video_path)
        self.results["video_size_mb"] = round(file_size, 2)
        self.results["steps_completed"].append("download_video")

    def _step_download_audio(self):
        print("\n🎵 Step 2: Downloading audio...")
        if self.audio_path.exists():
            print(f"   ⚠️  Audio already exists: {self.audio_path}")
            self.results["steps_completed"].append("download_audio")
            return
        
        # 抖音链接直接从视频提取音频（yt-dlp无法下载抖音音频）
        if DouyinDownloader.is_douyin_url(self.url):
            print("   📱 抖音视频，直接从视频提取音频...")
            if self.video_path.exists():
                try:
                    cmd = ["ffmpeg", "-i", str(self.video_path), "-vn", "-c:a", "copy", str(self.audio_path), "-y"]
                    subprocess.run(cmd, check=True, capture_output=True)
                    if self.audio_path.exists():
                        file_size = self.audio_path.stat().st_size / 1024
                        print(f"   ✅ Audio extracted from video: {file_size:.2f} KB")
                        self.results["audio_path"] = str(self.audio_path)
                        self.results["steps_completed"].append("download_audio")
                        return
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  Audio extraction failed: {e}")
            
            # 如果提取失败但视频存在，继续使用视频进行转录
            if self.video_path.exists():
                print("   ⚠️  Will use video directly for transcription")
                self.results["steps_completed"].append("download_audio")
                return
            
            raise RuntimeError("Audio extraction failed - file not found")
        
        # 其他平台：首先尝试从 URL 下载音频
        try:
            cmd = ["yt-dlp", "-f", "bestaudio[ext=m4a]/bestaudio", "--extract-audio", "--audio-format", "m4a", "-o", str(self.audio_path), self.url]
            subprocess.run(cmd, check=True, capture_output=True)
            if self.audio_path.exists():
                file_size = self.audio_path.stat().st_size / 1024
                print(f"   ✅ Audio downloaded: {file_size:.2f} KB")
                self.results["audio_path"] = str(self.audio_path)
                self.results["steps_completed"].append("download_audio")
                return
        except subprocess.CalledProcessError:
            print("   ⚠️  Audio download failed, extracting from video...")
        
        # 如果下载失败，从已下载的视频中提取音频
        if self.video_path.exists():
            try:
                cmd = ["ffmpeg", "-i", str(self.video_path), "-vn", "-c:a", "copy", str(self.audio_path), "-y"]
                subprocess.run(cmd, check=True, capture_output=True)
                if self.audio_path.exists():
                    file_size = self.audio_path.stat().st_size / 1024
                    print(f"   ✅ Audio extracted from video: {file_size:.2f} KB")
                    self.results["audio_path"] = str(self.audio_path)
                    self.results["steps_completed"].append("download_audio")
                    return
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  Audio extraction failed: {e}")
        
        # 如果都失败了，但视频存在，继续处理（使用视频进行转录）
        if self.video_path.exists():
            print("   ⚠️  Will use video directly for transcription")
            self.results["steps_completed"].append("download_audio")
            return
            
        raise RuntimeError("Audio download/extraction failed - file not found")

    def _step_scene_detection(self) -> Dict:
        print("\n🎞️  Step 3: Detecting scenes...")
        self.scenes_dir.mkdir(exist_ok=True)
        cmd = [sys.executable, "-m", "scenedetect", "-i", str(self.video_path), "-o", str(self.scenes_dir), "detect-content", "-t", str(self.scene_threshold)]
        if self.extract_scenes:
            cmd.append("split-video")
        result = subprocess.run(cmd, capture_output=True, text=True)
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
        if self.extract_scenes:
            scene_files = sorted(self.scenes_dir.glob("*.mp4"))
            scene_count = len(scene_files)
        print(f"   ✅ Detected {scene_count} scenes")
        scene_info = {"scene_count": scene_count, "scenes_dir": str(self.scenes_dir) if self.extract_scenes else None, "threshold": self.scene_threshold}
        self.results["scene_detection"] = scene_info
        self.results["steps_completed"].append("scene_detection")
        return scene_info

    def _step_transcription(self) -> Dict:
        print("\n🎤 Step 4: 智能字幕提取 (B站API → 内嵌 → RapidOCR → FunASR)...")
        if self.srt_path.exists():
            print(f"   ⚠️  Transcription already exists: {self.srt_path}")
            self.results["steps_completed"].append("transcription")
            return {"status": "skipped"}
        
        # 使用智能字幕提取（四级降级）
        try:
            from extract_subtitle_funasr import smart_subtitle_extraction
        except ImportError:
            # 如果导入失败，尝试从同目录加载
            script_dir = Path(__file__).parent
            sys.path.insert(0, str(script_dir))
            from extract_subtitle_funasr import smart_subtitle_extraction
        
        # 确定视频源
        video_source = str(self.video_path) if self.video_path.exists() else None
        if not video_source:
            print("   ❌ 视频文件不存在，无法转录")
            return {"status": "failed"}
        
        success, mode = smart_subtitle_extraction(
            video_path=video_source,
            output_srt=str(self.srt_path),
            video_url=self.url
        )
        
        if success:
            # 读取 SRT 生成 transcript 文本
            full_text = ""
            segment_count = 0
            try:
                with open(self.srt_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                texts = []
                for line in lines:
                    line = line.strip()
                    if line and not line.isdigit() and '-->' not in line:
                        texts.append(line)
                        segment_count += 1
                full_text = " ".join(texts)
            except Exception:
                pass
            
            # 写 transcript 文件
            if full_text:
                self._write_transcript_from_text(full_text, self.transcript_path)
            
            print(f"   ✅ 字幕提取完成 (模式: {mode})")
            transcript_info = {
                "language": "zh",
                "mode": mode,
                "segment_count": segment_count,
                "srt_path": str(self.srt_path),
                "transcript_path": str(self.transcript_path),
                "full_text": full_text
            }
            self.results["transcription"] = transcript_info
            self.results["steps_completed"].append("transcription")
            return transcript_info
        else:
            print("   ❌ 字幕提取失败")
            self.results["steps_completed"].append("transcription")
            return {"status": "failed"}
    
    def _write_transcript_from_text(self, text: str, output_path: Path):
        """将纯文本写入 transcript 文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"=== Video Transcript ===\n\n")
            f.write(f"=== Full Text ===\n\n{text}\n")

    @staticmethod
    def _funasr_to_segments(funasr_result) -> List[Dict]:
        """
        将 FunASR 返回结果转换为 Whisper 兼容的 segments 格式
        每个 segment: {"start": float_seconds, "end": float_seconds, "text": str}
        """
        segments = []
        for res in funasr_result:
            text = res.get('text', '').strip()
            sentence_info = res.get('sentence_info', [])
            timestamps = res.get('timestamp', [])
            
            if sentence_info:
                # 方案A: 使用句级时间戳（最佳）
                for sent in sentence_info:
                    sent_text = sent.get('text', '').strip()
                    if sent_text:
                        segments.append({
                            "start": sent.get('start', 0) / 1000.0,
                            "end": sent.get('end', 0) / 1000.0,
                            "text": sent_text
                        })
            elif timestamps and text:
                # 方案B: 按标点切分 + 字级时间戳映射
                sentence_endings = set('。！？!?；;…')
                clause_breaks = set('，,、')
                current_chars = []
                current_start_idx = 0
                ts_len = len(timestamps)
                text_len = len(text)
                
                for char_idx, char in enumerate(text):
                    current_chars.append(char)
                    ts_idx = min(int(char_idx / text_len * ts_len), ts_len - 1) if ts_len > 0 else 0
                    is_end = char in sentence_endings
                    is_clause = char in clause_breaks and len(current_chars) > 25
                    is_last = char_idx == text_len - 1
                    
                    if is_end or is_clause or is_last:
                        sent_text = ''.join(current_chars).strip()
                        if sent_text:
                            start_ts_idx = min(int(current_start_idx / text_len * ts_len), ts_len - 1) if ts_len > 0 else 0
                            start_ms = timestamps[start_ts_idx][0] if ts_len > 0 else 0
                            end_ms = timestamps[ts_idx][1] if ts_len > 0 else 0
                            segments.append({
                                "start": start_ms / 1000.0,
                                "end": end_ms / 1000.0,
                                "text": sent_text
                            })
                        current_chars = []
                        current_start_idx = char_idx + 1
            elif text:
                # 方案C: 无时间戳，仅文本
                segments.append({
                    "start": 0.0,
                    "end": 0.0,
                    "text": text
                })
        return segments

    def _write_srt(self, segments: List[Dict], output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\\n{start} --> {end}\\n{text}\\n\\n")

    def _write_transcript(self, segments: List[Dict], output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== Video Transcript ===\\n\\n")
            f.write("=== Full Text ===\\n\\n")
            full_text = " ".join([seg["text"].strip() for seg in segments])
            f.write(full_text + "\\n\\n")
            f.write("=== Timestamped Text ===\\n\\n")
            for seg in segments:
                start = self._format_timestamp(seg["start"])
                end = self._format_timestamp(seg["end"])
                f.write(f"[{start} --> {end}]\\n")
                f.write(f"{seg['text'].strip()}\\n\\n")

    def _format_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _step_extract_frames(self, scene_info: Dict):
        print("\\n🖼️  Step 5: Extracting frames from scenes...")
        if not self.extract_scenes or scene_info["scene_count"] == 0:
            print("   ⚠️  Scene extraction disabled or no scenes found")
            return
        self.frames_dir.mkdir(exist_ok=True)
        scene_files = sorted(self.scenes_dir.glob("*.mp4"))
        for scene_file in scene_files:
            scene_name = scene_file.stem
            # 使用 sanitize_filename 处理场景文件名，避免特殊字符导致 ffmpeg 错误
            safe_scene_name = sanitize_filename(scene_name)
            frame_path = self.frames_dir / f"{safe_scene_name}.jpg"
            if frame_path.exists():
                continue
            cmd = ["ffmpeg", "-i", str(scene_file), "-vf", "select=eq(n\\,0)", "-vframes", "1", str(frame_path), "-y"]
            subprocess.run(cmd, check=True, capture_output=True)
        frame_count = len(list(self.frames_dir.glob("*.jpg")))
        print(f"   ✅ Extracted {frame_count} frames")
        self.results["frames_dir"] = str(self.frames_dir)
        self.results["frame_count"] = frame_count
        self.results["steps_completed"].append("extract_frames")

    def _step_prepare_scoring(self, scene_info: Dict):
        print("\\n📊 Step 6: Preparing scene scoring structure...")
        if not self.extract_scenes or scene_info["scene_count"] == 0:
            print("   ⚠️  No scenes to score")
            return
        scene_files = sorted(self.scenes_dir.glob("*.mp4"))
        scoring_data = {
            "video_id": self.video_id,
            "url": self.url,
            "total_scenes": len(scene_files),
            "analysis_framework": {
                "philosophy": "Walter Murch's Six Rules: Emotion > Story > Rhythm > Eye-trace > 2D Plane > 3D Space",
                "scoring_criteria": {
                    "aesthetic_beauty": {"name": "美感 (Aesthetic Beauty)", "weight": "20%", "description": "构图(三分法)、光影质感、色彩和谐度", "scale": "1-10"},
                    "credibility": {"name": "可信度 (Credibility)", "weight": "20%", "description": "表演自然度、物理逻辑真实感、无出戏感", "scale": "1-10"},
                    "impact": {"name": "冲击力 (Impact)", "weight": "20%", "description": "视觉显著性、动态张力、第一眼冲击力", "scale": "1-10"},
                    "memorability": {"name": "记忆度 (Memorability)", "weight": "20%", "description": "独特视觉符号(Von Restorff效应)、金句、趣味性", "scale": "1-10"},
                    "fun_interest": {"name": "趣味度 (Fun/Interest)", "weight": "20%", "description": "参与感、娱乐价值、社交货币潜力", "scale": "1-10"}
                },
                "type_classification": {
                    "TYPE-A": "Hook/Kinetic - 视觉钩子/高能 (高饱和、奇观、快节奏)",
                    "TYPE-B": "Narrative/Emotion - 叙事/情感 (人物对话、细微表情)",
                    "TYPE-C": "Aesthetic/Vibe - 氛围/空镜 (风景、慢动作、极简)",
                    "TYPE-D": "Commercial/Info - 商业/展示 (产品特写、口播)"
                },
                "selection_rules": {
                    "MUST_KEEP": "加权总分 > 8.5 或 任意单项 = 10 (极致长板)",
                    "USABLE": "7.0 <= 加权总分 < 8.5 (过渡素材)",
                    "DISCARD": "加权总分 < 7.0 或存在致命瑕疵"
                }
            },
            "scenes": [],
            "instructions": "基于 Walter Murch 法则，对每个场景进行评分。考虑场景类型权重: Hook型侧重IMPACT, 叙事型侧重CREDIBILITY, 氛围型侧重AESTHETICS, 商业型侧重CREDIBILITY+MEMORABILITY"
        }
        for i, scene_file in enumerate(scene_files, 1):
            scene_data = {
                "scene_number": i,
                "filename": scene_file.name,
                "file_path": str(scene_file),
                "frame_path": str(self.frames_dir / f"{scene_file.stem}.jpg") if self.frames_dir.exists() else None,
                "type_classification": "TODO: 选择 TYPE-A/B/C/D",
                "description": "TODO: 一句话描述画面内容",
                "visual_summary": "TODO: 视觉内容摘要",
                "scores": {"aesthetic_beauty": 0, "credibility": 0, "impact": 0, "memorability": 0, "fun_interest": 0},
                "weighted_score": 0.0,
                "selection": "TODO: [MUST KEEP] / [USABLE] / [DISCARD]",
                "selection_reasoning": "TODO: 引用相关理论解释选择原因",
                "edit_suggestion": "TODO: 剪辑建议（保留几秒、是否需要静音等）",
                "notes": "TODO: 其他观察笔记"
            }
            scoring_data["scenes"].append(scene_data)
        with open(self.scores_path, "w", encoding="utf-8") as f:
            json.dump(scoring_data, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Scoring template created: {self.scores_path}")
        print(f"   📝 需要对 {len(scene_files)} 个场景进行评分")
        self.results["scoring_template"] = str(self.scores_path)
        self.results["steps_completed"].append("prepare_scoring")

    def _step_ai_scene_analysis(self, scene_info: Dict):
        print("\\n🤖 Step 7: Analyzing scenes with AI framework...")
        if not self.extract_scenes or scene_info["scene_count"] == 0:
            print("   ⚠️  No scenes to analyze")
            return
        scene_files = sorted(self.scenes_dir.glob("*.mp4"))
        for i, scene_file in enumerate(scene_files, 1):
            frame_path = self.frames_dir / f"{scene_file.stem}.jpg"
            analysis = {"scene_number": i, "filename": scene_file.name, "frame_path": str(frame_path) if frame_path.exists() else None, "ai_analysis_ready": True, "notes": "请查看帧图片后进行专业分析"}
            self.results["scene_analysis"].append(analysis)
        print(f"   ✅ 已为 {len(scene_files)} 个场景准备 AI 分析框架")
        self.results["steps_completed"].append("ai_scene_analysis")

    def _step_auto_select_best_shots(self, scene_info: Dict):
        print(f"\\n⭐ Step 8: Auto-selecting best shots (threshold: {self.best_threshold})...")
        self.best_shots_dir.mkdir(exist_ok=True)
        print(f"   ✅ 精选片段目录已创建: {self.best_shots_dir}")
        print(f"   📝 完成评分后运行: python3 scripts/scoring_helper_enhanced.py {self.scores_path} best")
        self.results["best_shots_dir"] = str(self.best_shots_dir)
        self.results["steps_completed"].append("auto_select_best_shots")

    def _step_generate_detailed_report(self, scene_info: Dict, transcript_info: Dict):
        print("\\n📄 Step 9: Generating detailed analysis report...")
        transcript_text = ""
        if self.transcript_path.exists():
            with open(self.transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
        # 读取详细报告模板
        template_path = Path(__file__).parent.parent / "templates" / "detailed_report_template.md"
        with open(template_path, 'r', encoding='utf-8') as f:
            report_template = f.read()
        # 构造场景列表表格
        scene_list_table_rows = []
        scene_files = sorted(self.scenes_dir.glob("*.mp4"))
        for i, scene_file in enumerate(scene_files, 1):
            scene_list_table_rows.append(f"| Scene {i:03d} | TODO | TODO | TODO | `{scene_file.name}` |")
        scene_list_table = "\\n".join(scene_list_table_rows)
        # 构造详细场景评估部分
        detailed_scene_evaluations_parts = []
        for i, scene_file in enumerate(scene_files, 1):
            frame_path = self.frames_dir / f"{scene_file.stem}.jpg"
            detailed_scene_evaluations_parts.append(f"""#### Scene {i:03d}: {scene_file.name}

**基础信息**
- **帧预览**: `{frame_path.name}` (见 frames/ 目录)
- **片段文件**: `scenes/{scene_file.name}`
- **类型分类**: TODO (TYPE-A/B/C/D)

**视觉内容描述**
> TODO: 详细描述画面内容、运镜方式、主体对象、色彩氛围等

**五维评分**
| 维度 | 得分 | 评分理由 |
|------|------|---------|
| 美感 | TODO | TODO |
| 可信度 | TODO | TODO |
| 冲击力 | TODO | TODO |
| 记忆度 | TODO | TODO |
| 趣味度 | TODO | TODO |
| **加权总分** | **TODO** | - |

**筛选决策**
- **建议等级**: TODO (MUST KEEP / USABLE / DISCARD)
- **决策理由**: 
  > TODO: 引用相关理论解释（如峰终定律、互补色原理、视觉显著性等）

**剪辑建议**
- **使用方式**: TODO (如：保留前3秒作为Hook，静音使用等)
- **适配场景**: TODO (如：适合作为开场、转场、结尾等)

---""")
        detailed_scene_evaluations = "\\n".join(detailed_scene_evaluations_parts)
        # 构造精选片段表格
        best_shots_table = """| 排名 | 场景 | 加权得分 | 入选理由 | 建议用途 |
|------|------|---------|---------|---------|
| 1 | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO |"""
        # 填充模板
        report = report_template.format(
            video_id=self.video_id,
            url=self.url,
            analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            video_size_mb=self.results.get('video_size_mb', 'N/A'),
            scene_count=scene_info.get('scene_count', 0),
            transcription_language=transcript_info.get('language', 'N/A'),
            transcription_segments=transcript_info.get('segment_count', 0),
            transcript_text=transcript_text[:500] if transcript_text else "(无转录内容)",
            scene_list_table=scene_list_table,
            detailed_scene_evaluations=detailed_scene_evaluations,
            best_threshold=self.best_threshold,
            best_shots_table=best_shots_table,
            video_output_dir_name=self.video_output_dir.name
        )
        with open(self.detailed_report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"   ✅ Detailed report generated: {self.detailed_report_path}")
        self.results["detailed_report_path"] = str(self.detailed_report_path)
        self.results["steps_completed"].append("generate_detailed_report")


def main():
    parser = argparse.ArgumentParser(
        description="Video Expert Analyzer - Enhanced Pipeline with Configurable Output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 首次运行，设置输出目录
  python3 pipeline_enhanced.py --setup

  # 分析视频
  python3 pipeline_enhanced.py https://www.bilibili.com/video/BV1xxxxx

  # 使用自定义输出目录
  python3 pipeline_enhanced.py URL -o /path/to/output

   # 使用自定义场景检测阈值
   python3 pipeline_enhanced.py URL --scene-threshold 20
        """
    )
    parser.add_argument("url", nargs="?", help="Video URL (Bilibili or YouTube)")
    parser.add_argument("-o", "--output", help="Output directory (default: from config)")
    parser.add_argument("--setup", action="store_true", help="Setup output directory configuration")
    parser.add_argument("--scene-threshold", type=float, default=27.0, help="Scene detection threshold (default: 27.0)")
    parser.add_argument("--no-extract-scenes", action="store_true", help="Skip extracting individual scene clips")
    parser.add_argument("--best-threshold", type=float, default=7.5, help="Threshold for best shots selection (default: 7.5)")
    parser.add_argument("--json-output", help="Save results as JSON to this file")
    args = parser.parse_args()
    if args.setup:
        setup_output_directory()
        return 0
    if args.output:
        output_dir = args.output
    else:
        output_dir = get_output_directory()
        print(f"📁 使用配置中的输出目录: {output_dir}")
    if not args.url:
        print("❌ Error: 请提供视频URL，或使用 --setup 配置输出目录")
        parser.print_help()
        return 1
    try:
        pipeline = VideoAnalysisPipeline(
            url=args.url,
            output_dir=output_dir,
            scene_threshold=args.scene_threshold,
            extract_scenes=not args.no_extract_scenes,
            best_threshold=args.best_threshold
        )
        results = pipeline.run()
        if args.json_output:
            with open(args.json_output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\\n📊 Results saved to: {args.json_output}")
        return 0
    except Exception as e:
        print(f"\\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
