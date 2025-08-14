FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /sgcc/

# Install uv
# 安装 uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Place executables in the environment at the front of the path
# 将环境中的可执行文件放在路径的最前面
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/sgcc/.venv/bin:$PATH"

# Compile bytecode
# 编译字节码
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# uv 缓存
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# 安装依赖
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# 安装mysqlclient依赖，celery mysql 后端需要
# Ref: https://pypi.org/project/mysqlclient/
# RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*


ENV PYTHONPATH=/sgcc

COPY ./ms_office /sgcc/ms_office

COPY ./script /sgcc/script

COPY ./pyproject.toml ./uv.lock ./alembic.ini /sgcc/

COPY ./mock_agent_data.py ./mock_agent_server.py ./mock_isc_auth.py /sgcc/

COPY ./app /sgcc/app

RUN chmod +x /sgcc/script/prestart.sh

# 暴露端口
EXPOSE 8000


# Sync the project
# 同步项目
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# 默认命令：先执行数据库迁移再启动服务
# CMD ["sh", "-c", "alembic upgrade head && fastapi run --workers 4 app/main.py --host 0.0.0.0 --port 8000"]
# CMD ["sh", "-c", "alembic check && alembic current && alembic upgrade head && fastapi run --workers 4 app/main.py --host 0.0.0.0 --port 8000"]
CMD ["sh", "-c", "script/prestart.sh && fastapi run --workers 4 app/main.py --host 0.0.0.0 --port 8000"]
# CMD ["sh", "-c", "alembic revision --autogenerate -m \"migration $(date +'%Y-%m-%d %H:%M:%S')\" && alembic upgrade head && fastapi run --workers 4 app/main.py --host 0.0.0.0 --port 8000"]