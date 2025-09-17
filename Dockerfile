# Use the official Python runtime as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including tesseract
RUN apt update && apt install -y tesseract-ocr tesseract-ocr-eng

# Verify tesseract installation and create symbolic link if needed
RUN which tesseract || ln -s /usr/bin/tesseract /usr/local/bin/tesseract
RUN tesseract --version
RUN ls -la /usr/bin/tesseract*

# Set environment variable for tesseract
ENV TESSERACT_CMD="/usr/bin/tesseract"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --verbose
RUN pip install --no-cache-dir pytesseract==0.3.10 --verbose
RUN pip list | grep -E "(pytesseract|Pillow|google-generativeai)"

# Copy the application code
COPY . .

# Create uploads directory
RUN mkdir -p static/files

# Test Python imports to ensure everything is working
RUN python -c "import pytesseract; print('✅ pytesseract imported successfully')"
RUN python -c "from PIL import Image; print('✅ Pillow imported successfully')"  
RUN python -c "import google.generativeai; print('✅ google-generativeai imported successfully')"

# Expose the port that the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]