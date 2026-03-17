# ---- Base Image ----
FROM python:3.11-slim

# ---- Install Chromium + dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-liberation \
    fonts-noto \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# ---- Set working directory ----
WORKDIR /app

# ---- Copy requirements first (for Docker layer caching) ----
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ---- Copy the rest of the project ----
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# ---- Expose port ----
EXPOSE 10000

# ---- Start with Gunicorn ----
CMD ["gunicorn", "--chdir", "backend", "app:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "120"]
