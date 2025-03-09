ARG PYTHON_VERSION=3.12
ARG DEBIAN_VERSION=bookworm

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-${DEBIAN_VERSION}-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
COPY pyproject.toml uv.lock /app/
COPY apeiron/ /app/apeiron/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Then, use a final image without uv
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION}

# Copy the application from the builder
WORKDIR /app
COPY --from=builder /app .

ENTRYPOINT ["/app/.venv/bin/python"]
CMD ["-m", "apeiron.agent"]
