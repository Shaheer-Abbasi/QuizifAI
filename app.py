import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import google.generativeai as genai
import logging
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from datetime import datetime

app = Flask(__name__)
load_dotenv()

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quiz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Handle PostgreSQL URL format for production
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

with app.app_context():
    db.create_all()

# AI Client setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure tesseract if available
if TESSERACT_AVAILABLE:
    # Try to find tesseract in common locations
    import shutil
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

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
    if not TESSERACT_AVAILABLE:
        logging.warning("Tesseract not available - cannot extract text from images")
        return "Image text extraction not available in this deployment. Please use PDF files or copy/paste text directly."
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return None

# ============ AUTHENTICATION ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ============ MAIN PAGES ============

@app.route('/')
def index():
    # Guest mode - current quiz generation functionality
    return render_template('guest/index.html')

@app.route('/home')
@login_required
def home():
    # Authenticated home - question generation + selection
    return render_template('home.html')

# ============ QUIZ MANAGEMENT ROUTES ============

@app.route('/quizzes')
@login_required
def quizzes():
    # User's saved quizzes
    user_quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    return render_template('quizzes.html', quizzes=user_quizzes)

@app.route('/create-quiz', methods=['POST'])
@login_required
def create_quiz():
    # Create a new quiz
    title = request.form.get('title')
    if not title:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({"status": "error", "message": "Quiz title is required"}), 400
        flash('Quiz title is required')
        return redirect(url_for('quizzes'))
    
    new_quiz = Quiz(title=title, user_id=current_user.id)
    db.session.add(new_quiz)
    db.session.commit()
    
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        return jsonify({"status": "success", "message": "Quiz created successfully!", "quiz_id": new_quiz.id})
    
    flash('Quiz created successfully!')
    return redirect(url_for('quizzes'))

@app.route('/delete-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    # Delete a quiz and all its questions
    quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully!')
    return redirect(url_for('quizzes'))

@app.route('/take-quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    # Load a quiz for the user to take
    quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user.id).first_or_404()
    
    return render_template('take_quiz.html', quiz=quiz)

@app.route('/api/quiz/<int:quiz_id>')
@login_required
def get_quiz_data(quiz_id):
    # API endpoint to get quiz data
    quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user.id).first_or_404()
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        return jsonify({"error": "This quiz has no questions yet!"}), 404
    
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "id": q.id,
            "question_text": q.question_text,
            "options": [q.option_a, q.option_b, q.option_c, q.option_d],
            "correct_answer": ord(q.correct_answer) - 65  # Convert A,B,C,D to 0,1,2,3
        })
    
    return jsonify({
        "quiz_id": quiz.id,
        "title": quiz.title,
        "questions": formatted_questions
    })

@app.route('/api/quizzes')
@login_required
def get_quizzes():
    user_quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    quizzes_data = []
    for quiz in user_quizzes:
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        quizzes_data.append({
            'id': quiz.id, 
            'title': quiz.title,
            'question_count': question_count
        })
    return jsonify(quizzes_data)

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    # Save quiz attempt results
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers')
    
    # Validate quiz belongs to user
    quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user.id).first_or_404()
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        return jsonify({"error": "This quiz has no questions"}), 404
    
    # Calculate score
    score = 0
    for i, question in enumerate(questions):
        # Skip unanswered questions
        if i < len(answers) and answers[i] is not None:
            user_answer = answers[i]
            correct_answer = ord(question.correct_answer) - 65  # Convert A,B,C,D to 0,1,2,3
            if user_answer == correct_answer:
                score += 1
    
    # Create attempt record
    new_attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total_questions=len(questions)
    )
    
    db.session.add(new_attempt)
    db.session.commit()
    
    return jsonify({
        "status": "success", 
        "message": "Quiz results saved!",
        "score": score,
        "total": len(questions)
    })

@app.route('/analytics')
@login_required
def analytics():
    # Get selected quiz filter from query parameter
    selected_quiz_id = request.args.get('quiz_id', type=int)
    
    # Get all user's quizzes for the dropdown
    user_quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    
    # Filter attempts based on selected quiz
    if selected_quiz_id:
        attempts = QuizAttempt.query.filter_by(
            user_id=current_user.id, 
            quiz_id=selected_quiz_id
        ).order_by(QuizAttempt.completed_at.asc()).all()
        selected_quiz = Quiz.query.get(selected_quiz_id)
        filter_title = selected_quiz.title if selected_quiz else f"Quiz {selected_quiz_id}"
    else:
        # Show all attempts
        attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.completed_at.asc()).all()
        filter_title = "All Quizzes"
    
    # Prepare data for Chart.js
    chart_data = []
    quiz_names = {}
    
    # Get quiz names
    for attempt in attempts:
        if attempt.quiz_id not in quiz_names:
            quiz = Quiz.query.get(attempt.quiz_id)
            quiz_names[attempt.quiz_id] = quiz.title if quiz else f"Quiz {attempt.quiz_id}"
    
    # Prepare time series data
    for attempt in attempts:
        chart_data.append({
            'date': attempt.completed_at.strftime('%Y-%m-%d'),
            'score': round((attempt.score / attempt.total_questions) * 100, 2),
            'quiz_name': quiz_names[attempt.quiz_id],
            'raw_score': f"{attempt.score}/{attempt.total_questions}"
        })
    
    # Calculate statistics
    total_attempts = len(attempts)
    if total_attempts > 0:
        avg_score = sum(attempt.score / attempt.total_questions for attempt in attempts) / total_attempts * 100
        best_score = max(attempt.score / attempt.total_questions for attempt in attempts) * 100
        recent_attempts = attempts[-5:] if len(attempts) >= 5 else attempts
    else:
        avg_score = 0
        best_score = 0
        recent_attempts = []
    
    stats = {
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 2),
        'best_score': round(best_score, 2),
        'recent_attempts': recent_attempts
    }
    
    return render_template('analytics.html', 
                         attempts=attempts, 
                         chart_data=chart_data, 
                         stats=stats,
                         user_quizzes=user_quizzes,
                         selected_quiz_id=selected_quiz_id,
                         filter_title=filter_title)

@app.route('/settings')
@login_required
def settings():
    # User account settings
    return render_template('settings.html')

# ============ API ROUTES ============

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    # Question generation API (works for both guest and authenticated users)
    user_input = None
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            file_ext = file.filename.split('.')[1].lower()
            if file_ext == 'pdf':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user_input = extract_text_from_pdf(file_path)
            elif file_ext in ['png', 'jpg', 'jpeg']:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user_input = extract_text_from_image(file_path)
            else:
                return jsonify({"status": "error", "message": "Unsupported file type"}), 400
    else:
        user_input = request.form.get("study_material")

    if not user_input:
        return jsonify({"status": "error", "message": "No input provided"}), 400

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("""Create quiz questions from the study material below. Follow these EXACT formatting rules:

                RULES:
                1. Generate 4-5 multiple choice questions
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
                """ + user_input)
        
        ai_response = response.text if response and hasattr(response, 'text') else "No response from AI"
        return jsonify({"status": "success", "ai_response": ai_response})
        
    except Exception as e:
        logging.error(f"Error generating questions: {e}")
        return jsonify({"status": "error", "message": f"Failed to generate questions: {e}"}), 500

@app.route('/save-question', methods=['POST'])
@login_required
def save_question():
    # Save a selected question to user's default quiz
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    question_text = data.get('question')
    answers = data.get('answers')
    correct_index = data.get('correct_index')
    
    # Get or create user's default quiz
    if not quiz_id:
        default_quiz = Quiz.query.filter_by(user_id=current_user.id, title='My Questions').first()
        if not default_quiz:
            default_quiz = Quiz(title='My Questions', user_id=current_user.id)
            db.session.add(default_quiz)
            db.session.flush()
        quiz_id = default_quiz.id
    
    # Create question
    new_question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        option_a=answers[0],
        option_b=answers[1],
        option_c=answers[2],
        option_d=answers[3],
        correct_answer=chr(65 + correct_index)  # Convert 0,1,2,3 to A,B,C,D
    )
    
    db.session.add(new_question)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Question saved!"})

# ============ LEGACY ROUTE (for backward compatibility) ============

@app.route("/upload", methods=["POST", "GET"])
def upload():
    # Redirect old upload route to generate-questions API
    if request.method == "POST":
        return generate_questions()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run in development mode
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')