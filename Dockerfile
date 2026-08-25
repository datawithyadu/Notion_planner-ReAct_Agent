# Base image with Python — matches your project's requires-python (>=3.14)
FROM python:3.14-slim
# Install uv (the package manager you've been using)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Set the working directory inside the container
WORKDIR /app
# Copy dependency files first — enables Docker's layer caching
# (dependencies only get reinstalled if these files change, not on every code edit)
COPY pyproject.toml uv.lock ./
# Install dependencies (no dev tools, no jupyter — this is a production build)
RUN uv sync --frozen --no-dev
# Now copy the rest of your actual project code
COPY Agent/ ./Agent/
COPY API/ ./API/
COPY tool/ ./tool/
COPY utils/ ./utils/
COPY static/ ./static/
# Tell Docker this container listens on port 8000
EXPOSE 8000
# The command that runs when the container starts
CMD ["uv", "run", "uvicorn", "API.server:app", "--host", "0.0.0.0", "--port", "8000"]