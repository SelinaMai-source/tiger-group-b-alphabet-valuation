# 🚀 Tiger Group B - Alphabet估值分析系统部署指南

## 方法1：使用Streamlit Cloud（推荐）

### 步骤1：准备代码
1. 确保你的代码在GitHub上
2. 确保`requirements.txt`文件包含所有依赖
3. 确保主应用文件名为`dashboard_app.py`或在`app/dashboard_app.py`

### 步骤2：部署到Streamlit Cloud
1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用GitHub账号登录
3. 点击"New app"
4. 选择你的GitHub仓库
5. 设置路径：
   - 如果是`dashboard_app.py`在根目录：`dashboard_app.py`
   - 如果是`app/dashboard_app.py`：`app/dashboard_app.py`
6. 点击"Deploy"

### 步骤3：配置环境变量（如果需要）
在Streamlit Cloud的设置中添加环境变量：
- `GOOGLE_APPLICATION_CREDENTIALS`（如果需要Google API）
- 其他API密钥

## 方法2：使用Heroku

### 步骤1：创建Heroku应用
```bash
# 安装Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 登录Heroku
heroku login

# 创建应用
heroku create your-app-name
```

### 步骤2：创建Procfile
创建`Procfile`文件：
```
web: streamlit run app/dashboard_app.py --server.port=$PORT --server.address=0.0.0.0
```

### 步骤3：创建runtime.txt
创建`runtime.txt`文件：
```
python-3.11.0
```

### 步骤4：部署
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## 方法3：使用Vercel

### 步骤1：安装Vercel CLI
```bash
npm i -g vercel
```

### 步骤2：创建vercel.json
```json
{
  "builds": [
    {
      "src": "app/dashboard_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/dashboard_app.py"
    }
  ]
}
```

### 步骤3：部署
```bash
vercel
```

## 方法4：使用Docker + 云服务器

### 步骤1：创建Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app/dashboard_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 步骤2：创建docker-compose.yml
```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 步骤3：部署到云服务器
```bash
# 构建镜像
docker build -t tiger-group-dashboard .

# 运行容器
docker run -d -p 8501:8501 --name dashboard-app tiger-group-dashboard
```

## 方法5：使用Google Cloud Run

### 步骤1：创建Dockerfile（同上）

### 步骤2：部署到Google Cloud Run
```bash
# 构建镜像
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/tiger-group-dashboard

# 部署到Cloud Run
gcloud run deploy tiger-group-dashboard \
  --image gcr.io/YOUR_PROJECT_ID/tiger-group-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 方法6：使用AWS Elastic Beanstalk

### 步骤1：创建.ebextensions配置
创建`.ebextensions/01_streamlit.config`：
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app/dashboard_app.py
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
    STREAMLIT_SERVER_ADDRESS: 0.0.0.0
```

### 步骤2：部署
```bash
eb init
eb create tiger-group-dashboard
eb deploy
```

## 注意事项

### 1. 安全性考虑
- 确保不暴露敏感信息（API密钥等）
- 使用环境变量存储敏感数据
- 考虑添加身份验证（如果需要）

### 2. 性能优化
- 使用`@st.cache_data`缓存数据
- 优化数据加载和处理
- 考虑使用CDN加速静态资源

### 3. 监控和维护
- 设置日志记录
- 监控应用性能
- 定期更新依赖

### 4. 域名和SSL
- 购买域名（可选）
- 配置SSL证书
- 设置自定义域名

## 推荐方案

**对于初学者：** 使用Streamlit Cloud
- 免费
- 简单易用
- 自动部署
- 无需服务器管理

**对于生产环境：** 使用Docker + 云服务器
- 完全控制
- 可扩展性强
- 成本可控
- 适合企业级应用

## 快速部署命令

### Streamlit Cloud（最简单）
1. 将代码推送到GitHub
2. 访问 https://share.streamlit.io
3. 连接GitHub仓库
4. 设置路径：`app/dashboard_app.py`
5. 点击Deploy

### 本地测试
```bash
cd tiger_group_final/app
streamlit run dashboard_app.py --server.port 8501 --server.address 0.0.0.0
```

访问：http://localhost:8501 