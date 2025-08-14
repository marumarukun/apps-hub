FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    ffmpeg && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

WORKDIR /workspace
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin/:${PATH}"

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-dev

COPY ./ ./
EXPOSE 8080

CMD ["uv", "run", "--no-sync", "python", "app.py"]
