#!/bin/bash

# 🚀 Tiger Group B - Alphabet估值分析系统部署脚本

echo "🚀 开始部署 Tiger Group B - Alphabet估值分析系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose未安装，请先安装docker-compose"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建新镜像
echo "🔨 构建Docker镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
    echo "✅ 部署成功！"
    echo "🌐 访问地址: http://localhost:8501"
    echo "🌐 公网访问: http://$(curl -s ifconfig.me):8501"
else
    echo "❌ 部署失败，请检查日志"
    docker-compose logs
    exit 1
fi

echo "📊 服务状态:"
docker-compose ps

echo "📝 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down" 