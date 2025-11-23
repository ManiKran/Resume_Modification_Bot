# ---------------------------
# 1. Base Image
# ---------------------------
FROM python:3.10-slim

# Prevent Python from buffering stdout
ENV PYTHONUNBUFFERED=1

# ---------------------------
# 2. Set Work Directory
# ---------------------------
WORKDIR /app

# ---------------------------
# 3. Install OS Dependencies
# ---------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# 4. Install Python Requirements
# ---------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# 5. Copy Application Code
# ---------------------------
COPY . .

# ---------------------------
# 6. Expose the port
# ---------------------------
EXPOSE 8000

# ---------------------------
# 7. Run the API
# ---------------------------
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'"]