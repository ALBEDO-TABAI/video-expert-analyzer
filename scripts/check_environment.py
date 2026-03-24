#!/usr/bin/env python3
"""
Video Expert Analyzer v2.1 环境检测和依赖安装脚本
检测所有必要和可选依赖
"""

import subprocess
import sys
import shutil

def check_command(cmd: str, version_arg: str = "--version") -> tuple:
    """检查命令行工具是否可用"""
    try:
        result = subprocess.run(
            [cmd, version_arg],
            capture_output=True,
            text=True,
            timeout=10
        )
        version = result.stdout.strip() or result.stderr.strip()
        return True, version.split('\n')[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""

def check_python_package(package: str) -> bool:
    """检查 Python 包是否已安装"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    print("=" * 55)
    print("🔍 Video Expert Analyzer v2.1 环境检测")
    print("=" * 55)
    print()
    
    all_ok = True
    missing_cmds = []
    missing_pips = []
    
    # ── 1. 系统工具 ──
    print("1️⃣  系统工具")
    
    # 检查 FFmpeg
    ok, version = check_command("ffmpeg", "-version")
    if ok:
        print(f"   ✅ ffmpeg: {version[:60]}")
    else:
        print(f"   ❌ ffmpeg 未安装 → brew install ffmpeg / 下载 FFmpeg")
        all_ok = False
    
    # 检查 yt-dlp (支持多种调用方式)
    ok, version = False, ""
    
    # 方法1: 直接命令
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ok, version = True, result.stdout.strip()
    except:
        pass
    
    # 方法2: 通过 py -m 调用
    if not ok:
        try:
            result = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                ok, version = True, result.stdout.strip()
        except:
            pass
    
    if ok:
        print(f"   ✅ yt-dlp: {version}")
    else:
        print(f"   ❌ yt-dlp 未安装 → pip3 install yt-dlp")
        all_ok = False
    
    # ── 2. 核心 Python 依赖（必需） ──
    print("\n2️⃣  核心 Python 依赖（必需）")
    
    core_packages = {
        "scenedetect": "scenedetect[opencv]",
        "requests": "requests",
        "torch": "torch",
    }
    
    for import_name, pip_name in core_packages.items():
        if check_python_package(import_name):
            print(f"   ✅ {pip_name}")
        else:
            print(f"   ❌ {pip_name} 未安装")
            missing_pips.append(pip_name)
            all_ok = False
    
    # ── 3. 语音转录依赖（FunASR） ──
    print("\n3️⃣  语音转录 (FunASR)")
    
    funasr_packages = {
        "funasr": "funasr",
        "modelscope": "modelscope",
        "torchaudio": "torchaudio",
    }
    
    for import_name, pip_name in funasr_packages.items():
        if check_python_package(import_name):
            print(f"   ✅ {pip_name}")
        else:
            print(f"   ❌ {pip_name} 未安装")
            missing_pips.append(pip_name)
            all_ok = False
    
    # ── 4. 可选依赖 ──
    print("\n4️⃣  可选依赖")
    
    optional = {
        "openai": ("openai", "API 模式评分"),
        "rapidocr_onnxruntime": ("rapidocr-onnxruntime", "烧录字幕 OCR 检测"),
    }
    
    for import_name, (pip_name, desc) in optional.items():
        if check_python_package(import_name):
            print(f"   ✅ {pip_name} ({desc})")
        else:
            print(f"   ⚠️  {pip_name} 未安装 ({desc}) → pip3 install {pip_name}")
    
    # ── 5. CUDA / MPS 检测 ──
    print("\n5️⃣  GPU 加速")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   ✅ CUDA: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print(f"   ✅ Apple MPS (Metal) 可用")
        else:
            print("   ⚠️  无 GPU 加速，将使用 CPU（FunASR 转录可能较慢）")
    except ImportError:
        print("   ⚠️  PyTorch 未安装，无法检测 GPU")
    
    # ── 结果汇总 ──
    print()
    print("=" * 55)
    
    if all_ok:
        print("✅ 所有核心依赖已满足！可以开始使用 Video Expert Analyzer。")
        print()
        print("快速开始：")
        print("  python3 scripts/pipeline_enhanced.py --setup")
        print("  python3 scripts/pipeline_enhanced.py <视频URL>")
    else:
        print("❌ 存在缺失依赖，请执行以下命令安装：")
        print()
        if missing_pips:
            print(f"  pip3 install {' '.join(missing_pips)}")
        for cmd in missing_cmds:
            print(f"  {cmd}")
        print()
        print("或一键安装所有依赖：")
        print("  pip3 install -r requirements.txt")
    
    print("=" * 55)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
