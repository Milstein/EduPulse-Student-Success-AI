# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run expects port 8080
ENV PORT=8080
EXPOSE 8080

# Run the ADK web server
CMD ["adk", "web", "edupulse", "--host", "0.0.0.0", "--port", "8080"]
