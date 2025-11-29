# LLM Analysis Quiz - Simple Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser (optional - will skip if fails)
RUN playwright install chromium --with-deps || echo "Playwright install skipped"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p downloads temp logs

# Expose port
EXPOSE 5000

# Run the application (matches Procfile for consistency)
CMD ["python", "run.py"]
