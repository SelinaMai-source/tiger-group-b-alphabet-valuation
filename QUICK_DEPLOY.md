# 🚀 快速部署指南

## 方法1：Streamlit Cloud（最简单，推荐）

### 步骤：
1. **将代码推送到GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **访问Streamlit Cloud**
   - 打开 https://share.streamlit.io
   - 使用GitHub账号登录

3. **部署应用**
   - 点击"New app"
   - 选择你的GitHub仓库
   - 设置路径：`app/dashboard_app.py`
   - 点击"Deploy"

4. **完成**
   - 等待部署完成
   - 获得公开访问链接

## 方法2：Docker部署（本地/服务器）

### 步骤：
1. **安装Docker**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **运行部署脚本**
   ```bash
   cd tiger_group_final
   ./deploy.sh
   ```

3. **手动部署（如果脚本失败）**
   ```bash
   # 构建镜像
   docker-compose build
   
   # 启动服务
   docker-compose up -d
   
   # 查看状态
   docker-compose ps
   ```

4. **访问应用**
   - 本地：http://localhost:8501
   - 公网：http://你的服务器IP:8501

## 方法3：云服务器部署

### 步骤：
1. **购买云服务器**（阿里云、腾讯云、AWS等）

2. **连接服务器**
   ```bash
   ssh root@你的服务器IP
   ```

3. **安装Docker**
   ```bash
   curl -fsSL https://get.docker.com | sh
   systemctl start docker
   systemctl enable docker
   ```

4. **上传代码**
   ```bash
   # 方法1：Git克隆
   git clone https://github.com/你的用户名/你的仓库名.git
   
   # 方法2：直接上传
   # 使用scp或SFTP上传代码
   ```

5. **部署**
   ```bash
   cd 你的项目目录
   ./deploy.sh
   ```

6. **配置防火墙**
   ```bash
   # Ubuntu
   ufw allow 8501
   
   # CentOS
   firewall-cmd --permanent --add-port=8501/tcp
   firewall-cmd --reload
   ```

## 方法4：使用Nginx反向代理

### 步骤：
1. **安装Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **配置Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/dashboard
   ```

   添加配置：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **启用配置**
   ```bash
   sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
netstat -tlnp | grep 8501

# 杀死进程
sudo kill -9 进程ID
```

### 2. 权限问题
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 给Docker权限
sudo usermod -aG docker $USER
```

### 3. 内存不足
```bash
# 查看内存使用
free -h

# 清理Docker缓存
docker system prune -a
```

### 4. 网络问题
```bash
# 检查防火墙
sudo ufw status

# 开放端口
sudo ufw allow 8501
```

## 监控和维护

### 1. 查看日志
```bash
# Docker日志
docker-compose logs -f

# 系统日志
journalctl -u docker
```

### 2. 更新应用
```bash
# 拉取最新代码
git pull

# 重新部署
./deploy.sh
```

### 3. 备份数据
```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

## 推荐方案

- **个人项目/演示**：Streamlit Cloud
- **小团队/测试**：Docker + 云服务器
- **生产环境**：Docker + 云服务器 + Nginx + SSL

## 联系支持

如果遇到问题，请：
1. 查看日志文件
2. 检查网络连接
3. 确认依赖安装
4. 查看官方文档 