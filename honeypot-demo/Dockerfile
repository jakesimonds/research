FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Create log directory
RUN mkdir -p /var/log/honeypot

# Expose port 80
EXPOSE 80

# Run as non-root user for production (optional, but good practice)
# RUN useradd -m -u 1000 honeypot
# USER honeypot

# Start the application
CMD ["python", "app.py"]
