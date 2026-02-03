FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port (Cloud Run defaults to 8080)
EXPOSE 8080

# Start the application
# Cloud Run injects the PORT environment variable, defaults to 8080 if missing
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
