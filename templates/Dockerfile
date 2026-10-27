FROM python:${python}-slim

COPY --from=ghcr.io/astral-sh/uv:${uv_version} /uv /usr/local/bin/uv
COPY --from=dopplerhq/cli:${doppler_version} /bin/doppler /usr/local/bin/doppler

# Venv lives outside /app so a bind-mounted project dir can't hide it.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$$PATH" \
    DOPPLER_PROJECT=${doppler_project} \
    DOPPLER_CONFIG=${doppler_config}

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project
COPY . .

# DOPPLER_TOKEN (read-only service token for ${doppler_project}/${doppler_config}) is set at run time.
ENTRYPOINT ["doppler", "run", "--"]
CMD ["python", "-m", "${package}.handler"]
