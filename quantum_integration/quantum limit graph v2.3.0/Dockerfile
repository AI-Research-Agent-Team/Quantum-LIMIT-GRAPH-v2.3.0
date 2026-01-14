# Base image: lightweight Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy repo files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port if dashboard is served
EXPOSE 7860

# Default command: run LIMIT-GRAPH app
CMD ["python", "app.py"]
