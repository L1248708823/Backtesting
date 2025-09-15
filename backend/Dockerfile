# 量化回测系统后端 Dockerfile - 基于基础镜像
FROM quant-base

LABEL maintainer="Quant Ninja <ninja@example.com>"
LABEL description="量化回测系统后端服务"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖 (pip已在基础镜像中配置国内源)
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p /app/data /app/logs

# 健康检查端点
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /healthcheck.sh

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]