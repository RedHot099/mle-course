# Image of the freshcast command line. Build: docker build -t freshcast .
#
# Two stages: the first installs everything with uv, the second receives only
# the finished virtual environment. uv, the build cache and the source tree
# stay out of the image that ships.

FROM python:3.12-slim AS build

# uv comes from its own image, pinned, instead of being installed with curl.
COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /bin/uv

# Byte-compile at build time, and copy files out of the cache mount.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1

WORKDIR /app

# Dependencies first: this layer is rebuilt only when the lock file changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Then the project itself, installed as a package, not as a link to src/.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable


FROM python:3.12-slim

# LightGBM needs the OpenMP runtime, which the slim image lacks.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Run as an unprivileged user: nothing here needs root.
RUN useradd --create-home app
USER app
WORKDIR /work

COPY --from=build --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Data, settings and artifacts are mounted at /work, never baked in.
ENTRYPOINT ["freshcast"]
CMD ["--help"]
