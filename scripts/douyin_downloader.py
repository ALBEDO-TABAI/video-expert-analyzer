#!/usr/bin/env python3
"""
Douyin Video Downloader
抖音视频下载模块 - 用于处理yt-dlp无法下载的抖音视频
"""

import requests
import re
import json
import sys
from urllib.parse import unquote
from pathlib import Path
from typing import Optional, Tuple


class DouyinDownloader:
    """抖音视频下载器"""
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
    
    @staticmethod
    def is_douyin_url(url: str) -> bool:
        """检查URL是否为抖音链接"""
        douyin_patterns = [
            'douyin.com',
            'iesdouyin.com',
            'v.douyin.com',
        ]
        return any(pattern in url.lower() for pattern in douyin_patterns)
    
    def get_redirect_url(self, short_url: str) -> Tuple[Optional[str], str]:
        """获取短链接重定向后的完整URL"""
        try:
            response = self.session.get(short_url, allow_redirects=True, timeout=10)
            return response.url, self.user_agent
        except Exception as e:
            print(f"   ⚠️  获取重定向URL失败: {e}")
            return None, self.user_agent
    
    def extract_render_data(self, html: str) -> Optional[str]:
        """从HTML中提取RENDER_DATA"""
        patterns = [
            r'<script id="RENDER_DATA" type="application/json">([^<]+)</script>',
            r'window\._ROUTER_DATA\s*=\s*(\{.+?\});?\s*</script>',
            r'window\._SSR_DATA\s*=\s*(\{.+?\});?\s*</script>',
            r'RENDER_DATA\s*=\s*"([^"]+)"',
            r'<script[^>]*>window\._SSR_HYDRATED_DATA\s*=\s*(.*?)</script>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                return matches[0]
        
        return None
    
    def parse_video_url(self, render_data: str) -> Optional[str]:
        """从RENDER_DATA中解析视频URL"""
        try:
            # URL解码
            if '%' in render_data:
                decoded = unquote(render_data)
            else:
                decoded = render_data
            
            # 解析JSON
            data = json.loads(decoded)
            
            # 搜索视频URL的常见路径
            possible_paths = [
                ['loaderData', 'video_(id)/page', 'videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
                ['loaderData', 'video_(id)/page', 'aweme_detail', 'video', 'play_addr', 'url_list'],
                ['data', 'videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
                ['app', 'videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
                ['app', 'videoDetail', 'video', 'play_addr', 'url_list'],
                ['videoInfoRes', 'item_list', 0, 'video', 'play_addr', 'url_list'],
                ['video', 'play_addr', 'url_list'],
                ['aweme_detail', 'video', 'play_addr', 'url_list'],
                ['app', 'videoDetail', 'video', 'playAddr'],
            ]
            
            def get_nested(obj, path):
                """安全获取嵌套字典/列表值"""
                current = obj
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    elif isinstance(current, list) and isinstance(key, int) and key < len(current):
                        current = current[key]
                    else:
                        return None
                return current
            
            video_url = None
            for path in possible_paths:
                url_list = get_nested(data, path)
                if url_list and isinstance(url_list, list) and len(url_list) > 0:
                    video_url = url_list[0]
                    break
            
            if not video_url:
                # 尝试在整个JSON中搜索视频URL
                json_str = json.dumps(data)
                play_patterns = [
                    r'"play_addr":\s*\{[^}]*"url_list":\s*\["([^"]+)"',
                    r'"playAddr":\s*\["([^"]+)"',
                    r'"download_addr":\s*\{[^}]*"url_list":\s*\["([^"]+)"',
                ]
                
                for pattern in play_patterns:
                    matches = re.findall(pattern, json_str)
                    if matches:
                        video_url = matches[0]
                        break
            
            if video_url:
                # 替换playwm为play获取无水印版本
                video_url = video_url.replace('playwm', 'play')
                return video_url
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  解析视频URL失败: {e}")
            return None
    
    def download_video(self, video_url: str, output_path: Path, progress_callback=None) -> bool:
        """下载视频到指定路径"""
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://www.douyin.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        try:
            response = requests.get(video_url, headers=headers, stream=True, timeout=30)
            
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
        下载抖音视频的完整流程
        
        Args:
            url: 抖音视频URL（支持短链接和长链接）
            output_path: 输出文件路径
            
        Returns:
            bool: 下载是否成功
        """
        print("   📱 检测到抖音链接，使用专用下载器...")
        
        # Step 1: 获取重定向后的URL
        full_url, _ = self.get_redirect_url(url)
        if not full_url:
            print("   ❌ 无法获取视频页面URL")
            return False
        
        # Step 2: 获取页面HTML
        try:
            response = self.session.get(full_url, timeout=15)
            html = response.text
        except Exception as e:
            print(f"   ❌ 获取页面失败: {e}")
            return False
        
        # Step 3: 提取RENDER_DATA
        render_data = self.extract_render_data(html)
        if not render_data:
            print("   ❌ 无法从页面提取视频数据")
            return False
        
        # Step 4: 解析视频URL
        video_url = self.parse_video_url(render_data)
        if not video_url:
            print("   ❌ 无法解析视频下载地址")
            return False
        
        # Step 5: 下载视频
        print(f"   📥 开始下载视频...")
        success = self.download_video(video_url, output_path)
        
        if success:
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✅ 视频下载成功: {file_size:.2f} MB")
        
        return success


def download_douyin_video(url: str, output_path: str) -> bool:
    """
    下载抖音视频的便捷函数
    
    Args:
        url: 抖音视频URL
        output_path: 输出文件路径
        
    Returns:
        bool: 下载是否成功
    """
    downloader = DouyinDownloader()
    return downloader.download(url, Path(output_path))


if __name__ == "__main__":
    # 测试代码
    if len(sys.argv) < 2:
        print("Usage: python douyin_downloader.py <douyin_url> [output_path]")
        sys.exit(1)
    
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./douyin_video.mp4"
    
    success = download_douyin_video(url, output)
    sys.exit(0 if success else 1)
