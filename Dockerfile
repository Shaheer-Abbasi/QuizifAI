# Use the official Python runtime as the base image
FROM python:3.9-slim-buster

# Install system dependencies including tesseract
RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr && \
    apt-get -qq -y install libtesseract-dev && \
    echo "=== TESSERACT INSTALLATION DEBUG ===" && \
    which tesseract || echo "tesseract not found in PATH" && \
    ls -la /usr/bin/tesseract* || echo "no tesseract files in /usr/bin/" && \
    ls -la /usr/local/bin/tesseract* || echo "no tesseract files in /usr/local/bin/" && \
    find /usr -name "tesseract*" 2>/dev/null | head -10 && \
    tesseract --version || echo "tesseract command failed" && \
    echo "=== END TESSERACT DEBUG ==="

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Command to run the application
CMD ["gunicorn", "app:app"]