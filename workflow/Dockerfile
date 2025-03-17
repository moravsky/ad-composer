FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy workflow code
COPY . .

# Set Python path to include the parent directory
ENV PYTHONPATH=/app

# Run the worker
CMD ["python", "/app/workflow/worker.py"]