# 🚀 量化回测系统自动部署指南

> 从零开始，手把手教你设置GitHub自动部署到云服务器

## 📋 目录

- [前置准备](#前置准备)
- [Step 1: 服务器端配置](#step-1-服务器端配置)
- [Step 2: 本地SSH密钥配置](#step-2-本地ssh密钥配置)
- [Step 3: GitHub配置](#step-3-github配置)
- [Step 4: 测试部署](#step-4-测试部署)
- [常见问题](#常见问题)

---

## 前置准备

### 你需要有：
- ✅ 一台云服务器（阿里云/腾讯云/AWS等）
- ✅ 服务器已安装Docker和Docker Compose
- ✅ 代码已上传到GitHub
- ✅ 能SSH登录服务器

### 检查服务器环境：
```bash
# SSH登录服务器后执行
docker --version          # 应该显示Docker版本
docker-compose --version  # 应该显示Docker Compose版本
```

如果没安装，运行：
```bash
# Ubuntu/Debian系统
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```

---

## Step 1: 服务器端配置

### 1.1 克隆项目到服务器

```bash
# SSH登录你的服务器
ssh your-username@your-server-ip

# 选择项目目录（建议用/opt）
sudo mkdir -p /opt/quant-backtest
sudo chown $USER:$USER /opt/quant-backtest
cd /opt/quant-backtest

# 克隆项目（替换为你的GitHub仓库地址）
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git .

# 给部署脚本执行权限
chmod +x simple-deploy.sh
```

### 1.2 测试手动部署

```bash
# 测试部署脚本是否正常工作
./simple-deploy.sh

# 检查服务是否启动
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

**预期结果**：
- 前端服务：http://你的服务器IP:3001
- 后端服务：http://你的服务器IP:8008

---

## Step 2: 本地SSH密钥配置

### 2.1 生成SSH密钥对

**在你的本地电脑上执行**：

```bash
# 生成新的SSH密钥对（替换your-email@example.com为你的邮箱）
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# 提示输入文件名时，可以直接回车使用默认名称
# 提示设置密码时，可以直接回车（无密码）
```

### 2.2 复制公钥到服务器

```bash
# 查看生成的公钥内容
cat ~/.ssh/id_rsa.pub

# 复制这段内容，然后SSH登录服务器执行：
```

**在服务器上**：
```bash
# 创建.ssh目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 添加公钥到授权文件（将下面的内容替换为刚才复制的公钥）
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... your-email@example.com" >> ~/.ssh/authorized_keys

# 设置正确权限
chmod 600 ~/.ssh/authorized_keys
```

### 2.3 测试SSH连接

**在本地测试**：
```bash
# 测试无密码SSH登录（替换为你的服务器信息）
ssh your-username@your-server-ip

# 如果能直接登录不需要密码，说明配置成功！
```

---

## Step 3: GitHub配置

### 3.1 获取SSH私钥内容

**在本地电脑**：
```bash
# 查看私钥内容（注意是私钥，没有.pub后缀）
cat ~/.ssh/id_rsa

# 复制整个内容，从-----BEGIN开头到-----END结尾
```

### 3.2 设置GitHub Secrets

1. **打开GitHub仓库页面**
2. **点击Settings选项卡**
3. **左侧菜单找到"Secrets and variables" → "Actions"**
4. **点击"New repository secret"**

**创建以下3个密钥**：

| 名称 | 值 | 说明 |
|------|----|----|
| `HOST` | `123.456.78.90` | 你的服务器IP地址 |
| `USERNAME` | `ubuntu` | SSH登录用户名 |
| `KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | 完整的SSH私钥内容 |

**⚠️ 重要提示**：
- `KEY`的值要包含完整的私钥，包括开头和结尾的注释行
- 不要在私钥前后添加额外的空格或换行

### 3.3 修改部署脚本路径

编辑`.github/workflows/simple-deploy.yml`：

```yaml
# 修改这一行为你服务器上的实际项目路径
script: |
  cd /opt/quant-backtest  # 改为你的实际路径
  git pull origin main
  docker-compose restart
```

---

## Step 4: 测试部署

### 4.1 提交代码触发部署

```bash
# 在本地项目目录
git add .
git commit -m "设置自动部署"
git push origin main
```

### 4.2 查看部署状态

1. **GitHub网页上查看**：
   - 进入你的仓库
   - 点击"Actions"选项卡
   - 应该能看到正在运行的部署任务

2. **服务器上查看**：
```bash
# SSH登录服务器，查看是否有新的更新
cd /opt/quant-backtest
git log --oneline -5  # 查看最近5次提交

# 查看容器状态
docker-compose ps
```

### 4.3 验证部署结果

访问你的应用：
- 前端：`http://你的服务器IP:3001`
- 后端API文档：`http://你的服务器IP:8008/docs`

**成功标志**：
- ✅ GitHub Actions显示绿色✓
- ✅ 网站能正常访问
- ✅ 功能正常工作

---

## 常见问题

### ❌ SSH连接失败

**问题**: `Permission denied (publickey)`

**解决**:
```bash
# 1. 检查SSH服务状态
sudo systemctl status ssh

# 2. 检查authorized_keys权限
ls -la ~/.ssh/
# authorized_keys应该是600权限

# 3. 重启SSH服务
sudo systemctl restart ssh
```

### ❌ Git拉取失败

**问题**: `fatal: could not read Username for 'https://github.com'`

**解决**:
```bash
# 在服务器上配置Git（如果是私有仓库）
git config --global credential.helper store

# 或者使用SSH URL克隆
git remote set-url origin git@github.com:USERNAME/REPO.git
```

### ❌ Docker权限问题

**问题**: `permission denied while trying to connect to the Docker daemon socket`

**解决**:
```bash
# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

### ❌ 端口被占用

**问题**: 3001或8008端口被占用

**解决**:
```bash
# 查看端口占用
sudo netstat -tlnp | grep -E '(3001|8008)'

# 修改docker-compose.yml中的端口映射
ports:
  - "3002:3001"  # 改为其他端口
  - "8009:8008"  # 改为其他端口
```

### ❌ GitHub Actions失败

**问题**: 部署任务失败

**排查步骤**:
1. 检查GitHub Secrets是否正确设置
2. 检查服务器路径是否存在
3. 手动SSH到服务器测试命令是否能执行
4. 查看Actions日志的详细错误信息

---

## 🎉 部署成功后

### 日常工作流程：
1. 本地开发代码
2. `git add . && git commit -m "功能描述"`
3. `git push origin main`
4. 等待30秒，自动部署完成！

### 监控和维护：
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 手动重启服务
docker-compose restart

# 查看资源使用
docker stats
```

---

## 📞 需要帮助？

如果按照这个指南还有问题，可以：

1. **检查每一步是否严格按照说明执行**
2. **查看GitHub Actions的详细日志**
3. **SSH到服务器手动测试部署脚本**
4. **确认防火墙是否开放了3001和8008端口**

记住：第一次配置可能会遇到各种小问题，但一旦配置成功，后续就非常爽了！🚀