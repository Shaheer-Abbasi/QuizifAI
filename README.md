# QuizifAI: AI-Powered Quiz Generator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-lightgrey)](https://flask.palletsprojects.com/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow)](https://huggingface.co/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

**QuizifAI** automatically generates quizzes from textbooks, notes, or images! Upload a PDF/image or paste text, and let AI create practice questions. Perfect for students and educators.

**Key Features**:
- 📄 **PDF/Image Processing**: Extracts text using PyPDF2 and pytesseract (OCR)
- 🤖 **AI Question Generation**: Uses HuggingFace LLMs to generate MCQs
- 📊 **Quiz Dashboard**: Save, organize, and track quiz scores
- 🚀 **Flask Backend**: Lightweight and scalable

*Note: Currently in active development. Contributions welcome!*

---

## 🛠️ Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy
- **AI/NLP**: Google Gemini API, pytesseract (OCR)
- **Database**: SQLite (dev), PostgreSQL (planned)
- **Frontend**: HTML, Bootstrap CSS
- **Deployment**: PythonAnywhere (coming soon)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Tesseract OCR ([Installation Guide](https://github.com/tesseract-ocr/tesseract))
- HuggingFace API key (optional)

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/QuizifAI.git
   cd QuizifAI
   ```
2. Install dependencies:
    ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
Visit http://localhost:5000 in your browser.
