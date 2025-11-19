# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a valid home directory for the user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Create required directories for CrewAI / ChromaDB
RUN mkdir -p /home/appuser/.local/share && chown -R appuser:appuser /home/appuser

# Install requirements
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

USER appuser

COPY . .

EXPOSE 8000

CMD ["python", "crew.py"]
