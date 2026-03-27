ARG REGISTRY_PREFIX_DOCKER_HUB=
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY --from=workspace pyproject.toml /app/pyproject.toml
COPY --from=workspace mcp/ /app/mcp/
COPY --from=workspace nanobot-websocket-channel/ /app/nanobot-websocket-channel/
COPY . /app/nanobot/
RUN uv sync --no-dev --package nanobot

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm
WORKDIR /app/nanobot
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "entrypoint.py"]
