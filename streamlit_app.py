# streamlit_app.py
# Streamlit Cloud 专用入口文件

import streamlit as st
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入主应用
from app.dashboard_app import main

if __name__ == "__main__":
    main()
