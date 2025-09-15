# 量化回测系统前端 Dockerfile
FROM node:18-alpine

LABEL maintainer="Quant Ninja <ninja@example.com>"
LABEL description="量化回测系统前端服务"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=development

# 安装系统依赖
RUN apk add --no-cache curl

# 复制包配置文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖 (使用pnpm)
RUN npm install -g pnpm@8.15.5 && \
    pnpm install

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# 启动命令 (开发模式，支持热重载)
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]