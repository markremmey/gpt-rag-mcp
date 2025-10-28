FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage layer caching
COPY requirements.txt /tmp/requirements.txt

# Install Python deps (removed spaCy/model logic)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy app source
COPY . /app
WORKDIR /app

EXPOSE 80
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]