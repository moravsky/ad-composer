FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy notification service code
COPY . .

# Expose the port for WebSocket connections
EXPOSE 8765

# Run the notification service
CMD ["python", "main.py"]