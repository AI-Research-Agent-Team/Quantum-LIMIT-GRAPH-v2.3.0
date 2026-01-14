# Use Python 3.11 slim image for optimal performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV AGENT_PORT=8000

# Expose the agent port
EXPOSE 8000

# Make run script executable
RUN chmod +x run.sh

# Set the entrypoint to run the agent via controller
ENTRYPOINT ["./run.sh"]
