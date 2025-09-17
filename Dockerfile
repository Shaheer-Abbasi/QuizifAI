# Use the official Python runtime as the base image
FROM python:3.9-slim-buster

# Install system dependencies including tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "=== TESSERACT INSTALLATION DEBUG ===" && \
    which tesseract || echo "tesseract not found in PATH" && \
    ls -la /usr/bin/tesseract* || echo "no tesseract files in /usr/bin/" && \
    ls -la /usr/local/bin/tesseract* || echo "no tesseract files in /usr/local/bin/" && \
    find /usr -name "tesseract*" 2>/dev/null | head -10 && \
    tesseract --version || echo "tesseract command failed" && \
    echo "PATH: $PATH" && \
    echo "=== END TESSERACT DEBUG ==="

# Set environment variable for tesseract path
ENV TESSERACT_PATH=/usr/bin/tesseract

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Command to run the application
CMD ["gunicorn", "app:app"]