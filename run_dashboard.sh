#!/bin/bash

# 🐯 Tiger Group B - Alphabet估值分析系统启动脚本

echo "🐯 欢迎使用 Tiger Group B - Alphabet估值分析系统"
echo "=================================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 检查依赖安装是否成功
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请检查网络连接和requirements.txt文件"
    exit 1
fi

# 进入app目录
cd app

echo "🚀 启动仪表板..."
echo "📊 仪表板将在浏览器中打开：http://localhost:8501"
echo "🔄 按 Ctrl+C 停止服务"
echo ""

# 启动Streamlit应用
streamlit run dashboard_app.py --server.port 8501 --server.address 0.0.0.0 