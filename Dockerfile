FROM node:20-bookworm

LABEL maintainer="Anh Cơ La (Ryan) <genesis.corp.os@gmail.com>"
LABEL description="Heo-Harness OS — V6 Executive Intelligence OS & Modular AI Agent Chassis"

# 1. Cài đặt Python 3, pip, curl và các công cụ hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    procps \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Sao chép và cài đặt các dependencies (nếu có)
COPY pyproject.toml ./
RUN pip3 install --no-cache-dir --break-system-packages -e . || true

# 3. Sao chép toàn bộ mã nguồn Heo-Harness
COPY heo_harness/ ./heo_harness/
COPY config/ ./config/
COPY docs/ ./docs/
COPY tests/ ./tests/
COPY doctor.sh ./
COPY start.sh ./
COPY stop.sh ./
COPY entrypoint.sh ./

RUN chmod +x doctor.sh start.sh stop.sh entrypoint.sh

# Cổng mặc định V6 Executive UI
EXPOSE 5088

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["run"]
