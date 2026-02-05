#!/usr/bin/env python3
"""
Video Expert Analyzer - Unified Entry Point
统一入口脚本，自动调用增强版 pipeline
"""

import sys
import os

# 将脚本目录添加到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# 导入增强版 pipeline
from pipeline_enhanced import main

if __name__ == "__main__":
    sys.exit(main())
