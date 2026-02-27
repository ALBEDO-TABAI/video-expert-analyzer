#!/usr/bin/env python3
"""
XiaoHongShu Video Downloader
小红书视频下载模块 - 用于处理小红书视频笔记
"""

import requests
import re
import json
import sys
from urllib.parse import unquote, urlparse
from pathlib import Path
from typing import Optional, Tuple, Dict


class XiaohongshuDownloader:
    """小红书视频下载器"""
    
    def __init__(self):
        # 使用移动端UA更容易获取数据
        self.mobile_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        # PC端UA
        self.pc_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        self.session = requests.Session()
        
    @staticmethod
    def is_xiaohongshu_url(url: str) -> bool:
        """检查URL是否为小红书链接"""
        xhs_patterns = [
            'xiaohongshu.com',
            'xhslink.com',
        ]
        return any(pattern in url.lower() for pattern in xhs_patterns)
    
    @staticmethod
    def extract_note_id(url: str) -> Optional[str]:
        """从URL中提取笔记ID"""
        # 处理 /discovery/item/xxxx 格式
        match = re.search(r'/item/([a-f0-9]+)', url)
        if match:
            return match.group(1)
        
        # 处理 /explore/xxxx 格式
        match = re.search(r'/explore/([a-f0-9]+)', url)
        if match:
            return match.group(1)
        
        # 处理短链接 xhslink.com/xxxx
        if 'xhslink.com' in url:
            return None  # 短链接需要重定向获取
        
        return None
    
    def get_redirect_url(self, short_url: str) -> Tuple[Optional[str], str]:
        """获取短链接重定向后的完整URL"""
        try:
            self.session.headers.update({
                'User-Agent': self.mobile_user_agent,
            })
            response = self.session.get(short_url, allow_redirects=True, timeout=10)
            return response.url, self.mobile_user_agent
        except Exception as e:
            print(f"   ⚠️  获取重定向URL失败: {e}")
            return None, self.mobile_user_agent
    
    def get_note_info(self, url: str) -> Dict:
        """获取笔记信息（标题、作者、视频URL等）"""
        result = {
            "success": False,
            "title": "",
            "uploader": "",
            "video_url": None,
            "cover_url": None,
            "note_id": None,
            "platform": "xiaohongshu"
        }
        
        # 处理短链接
        if 'xhslink.com' in url:
            url, _ = self.get_redirect_url(url)
            if not url:
                return result
        
        # 提取笔记ID
        note_id = self.extract_note_id(url)
        result["note_id"] = note_id
        
        try:
            # 使用PC UA获取页面（通常内容更完整）
            self.session.headers.update({
                'User-Agent': self.pc_user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.xiaohongshu.com/',
            })
            
            response = self.session.get(url, timeout=15)
            html = response.text
            
            # 尝试多种方式提取数据
            
            # 方式1: 从 __INITIAL_STATE__ 提取
            state_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.+?\})\s*</script>', html, re.DOTALL)
            if state_match:
                try:
                    # 处理undefined等非标准JSON
                    state_str = state_match.group(1)
                    state_str = re.sub(r':undefined', ':null', state_str)
                    state_str = re.sub(r':NaN', ':null', state_str)
                    state = json.loads(state_str)
                    
                    # 提取笔记详情
                    note_data = state.get('note', {}).get('noteDetailMap', {})
                    if note_data:
                        for key, note in note_data.items():
                            note_info = note.get('note', {})
                            result["title"] = note_info.get('title', '') or note_info.get('desc', '')[:50]
                            result["uploader"] = note_info.get('user', {}).get('nickname', '')
                            
                            # 视频信息
                            video = note_info.get('video', {})
                            if video:
                                # 获取视频URL
                                media = video.get('media', {})
                                stream = media.get('stream', {})
                                
                                # 尝试多种格式
                                for quality in ['h264', 'h265', 'av1']:
                                    streams = stream.get(quality, [])
                                    if streams:
                                        for s in streams:
                                            backup_urls = s.get('backupUrls', [])
                                            if backup_urls:
                                                result["video_url"] = backup_urls[0]
                                                break
                                            master_url = s.get('masterUrl')
                                            if master_url:
                                                result["video_url"] = master_url
                                                break
                                    if result["video_url"]:
                                        break
                                
                                # 如果还没找到，尝试consumer
                                if not result["video_url"]:
                                    consumer = video.get('consumer', {})
                                    origin_url = consumer.get('originVideoKey')
                                    if origin_url:
                                        result["video_url"] = f"https://sns-video-bd.xhscdn.com/{origin_url}"
                            
                            # 封面
                            image_list = note_info.get('imageList', [])
                            if image_list:
                                result["cover_url"] = image_list[0].get('urlDefault')
                            
                            if result["title"] or result["uploader"]:
                                result["success"] = True
                                break
                except json.JSONDecodeError:
                    pass
            
            # 方式2: 从 meta 标签提取
            if not result["success"]:
                title_match = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', html)
                if title_match:
                    result["title"] = title_match.group(1)
                
                author_match = re.search(r'<meta[^>]+name="author"[^>]+content="([^"]+)"', html)
                if author_match:
                    result["uploader"] = author_match.group(1)
                
                video_match = re.search(r'<meta[^>]+property="og:video"[^>]+content="([^"]+)"', html)
                if video_match:
                    result["video_url"] = video_match.group(1)
                
                if result["title"]:
                    result["success"] = True
            
            # 方式3: 从页面HTML中直接搜索视频URL
            if not result["video_url"]:
                video_patterns = [
                    r'"originVideoKey":"([^"]+)"',
                    r'"masterUrl":"([^"]+)"',
                    r'https://sns-video[^"]+\.mp4[^"]*',
                ]
                for pattern in video_patterns:
                    match = re.search(pattern, html)
                    if match:
                        video_url = match.group(1) if '(' in pattern else match.group(0)
                        if not video_url.startswith('http'):
                            video_url = f"https://sns-video-bd.xhscdn.com/{video_url}"
                        result["video_url"] = video_url
                        break
            
            return result
            
        except Exception as e:
            print(f"   ⚠️  获取笔记信息失败: {e}")
            return result
    
    def download_video(self, video_url: str, output_path: Path, progress_callback=None) -> bool:
        """下载视频到指定路径"""
        headers = {
            'User-Agent': self.pc_user_agent,
            'Referer': 'https://www.xiaohongshu.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        try:
            response = requests.get(video_url, headers=headers, stream=True, timeout=60)
            
            if response.status_code in (200, 206):
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                progress_callback(downloaded, total_size)
                
                return True
            else:
                print(f"   ⚠️  下载失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️  下载视频时出错: {e}")
            return False
    
    def download(self, url: str, output_path: Path) -> bool:
        """
        下载小红书视频的完整流程
        
        Args:
            url: 小红书笔记URL
            output_path: 输出文件路径
            
        Returns:
            bool: 下载是否成功
        """
        print("   📕 检测到小红书链接，使用专用下载器...")
        
        # Step 1: 获取笔记信息
        note_info = self.get_note_info(url)
        
        if not note_info.get("success"):
            print("   ❌ 无法获取笔记信息")
            return False
        
        print(f"   📝 标题: {note_info.get('title', 'N/A')[:50]}...")
        print(f"   👤 作者: {note_info.get('uploader', 'N/A')}")
        
        video_url = note_info.get("video_url")
        if not video_url:
            print("   ❌ 这可能是图文笔记，不是视频笔记")
            return False
        
        # Step 2: 下载视频
        print(f"   📥 开始下载视频...")
        success = self.download_video(video_url, output_path)
        
        if success:
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✅ 视频下载成功: {file_size:.2f} MB")
        
        return success


def download_xiaohongshu_video(url: str, output_path: str) -> bool:
    """
    下载小红书视频的便捷函数
    
    Args:
        url: 小红书笔记URL
        output_path: 输出文件路径
        
    Returns:
        bool: 下载是否成功
    """
    downloader = XiaohongshuDownloader()
    return downloader.download(url, Path(output_path))


if __name__ == "__main__":
    # 测试代码
    if len(sys.argv) < 2:
        print("Usage: python xiaohongshu_downloader.py <xiaohongshu_url> [output_path]")
        sys.exit(1)
    
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./xiaohongshu_video.mp4"
    
    success = download_xiaohongshu_video(url, output)
    sys.exit(0 if success else 1)
