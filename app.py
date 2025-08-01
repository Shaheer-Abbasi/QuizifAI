import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from openai import OpenAI
from google import genai
import logging
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)
    
load_dotenv()

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path):
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return None
    
def extract_text_from_image(image_path):
    print(f"Extracting text from image: {image_path}")
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return None


@app.route("/", methods=["POST", "GET"])
@app.route("/upload", methods=["POST", "GET"])
def index():
    ai_response = None
    user_input = None
     
    if request.method == "POST":
        app.logger.info(f"Request files: {request.files}")
        app.logger.info(f"Request form: {request.form}")
        app.logger.info(f"File in request.files: {'file' in request.files}")
        if 'file' in request.files:
            app.logger.info("File upload detected")
            file = request.files['file']
            if file.filename != '':
                app.logger.info(f"File received: {file.filename}")
                file_ext = file.filename.split('.')[1].lower()

                if file_ext == 'pdf':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    user_input = extract_text_from_pdf(file_path)
                    print(f"Extracted text from PDF: {user_input}")
                elif file_ext in ['png', 'jpg', 'jpeg']:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    user_input = extract_text_from_image(file_path)
                    print(f"Extracted text from image: {user_input}")
                else:
                    return jsonify({"status": "error", "message": "Unsupported file type"}), 400
        else:
            app.logger.info("No file upload detected, checking for user input")
            user_input = request.form.get("study_material")
            app.logger.info(f"User entered: {user_input}")

        response = client.models.generate_content(
            model="gemma-3n-e2b-it",
            contents="Give me a few questions about the following study material with 4 answer choices per question. " \
                     "Format your response by providing only the question (with a ; after the question mark) followed by its answers seperated by commas. " \
                     "Please separate each question with a | symbol." \
                     "Make sure to include the correct answer in the choices marked with an asterisk. " \
                     "Do NOT label the answers with A. B. C., etc:" \
                     "For example: question1? answer1, answer2, answer3, answer4* | question2? answer1, answer2*, answer3, answer4" \
                     "Here is the study material: " \
                     + user_input if user_input else "say 'No input provided'",
        )
        
        logging.basicConfig(level=logging.INFO)
        logging.info(response.text)

        ai_response = response.text if response and hasattr(response, 'text') else "No response from AI"
        logging.info(f"AI response: {ai_response}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "success", "input" : user_input}, {"status": "success", "ai_response": ai_response})
        else:
            return render_template("index.html")
   
    return render_template("index.html", user_input=user_input, ai_response=ai_response)

if __name__ == "__main__":
    app.run(debug=True)