# Use the official Python runtime as the base image
FROM python:3.9-slim-buster

# Install system dependencies including tesseract
RUN apt-get update && \
    echo "=== APT UPDATE COMPLETED ===" && \
    apt-get -qq -y install tesseract-ocr && \
    echo "=== TESSERACT-OCR INSTALLED ===" && \
    apt-get -qq -y install libtesseract-dev && \
    echo "=== LIBTESSERACT-DEV INSTALLED ===" && \
    which tesseract && \
    echo "=== TESSERACT LOCATION FOUND ===" && \
    tesseract --version && \
    echo "=== TESSERACT VERSION CHECK PASSED ===" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "=== BUILD CLEANUP COMPLETED ==="

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Command to run the application
CMD ["gunicorn", "app:app"]