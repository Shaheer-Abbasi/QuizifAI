import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from google import genai
import logging
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

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
            contents="""Create quiz questions from the study material below. Follow these EXACT formatting rules:

            RULES:
            1. Generate 3-5 multiple choice questions
            2. Each question must have EXACTLY 4 answer choices
            3. Mark the correct answer with an asterisk (*) at the END
            4. Use this EXACT format: Question? ; answer1, answer2, answer3*, answer4
            5. Separate questions with the pipe symbol: |
            6. NO letter labels (A, B, C, D)
            7. NO numbering
            8. NO extra text or explanations

            EXAMPLE FORMAT:
            What is the capital of France? ; London, Berlin, Paris*, Rome | What is 2+2? ; 3, 4*, 5, 6

            STUDY MATERIAL:
            """ + (user_input if user_input else "No input provided"),
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