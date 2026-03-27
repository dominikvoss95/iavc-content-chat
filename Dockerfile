# Use official Python lightweight image
FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies required for C-extensions (like sqlite-vec/SQLite)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "src.main"]
