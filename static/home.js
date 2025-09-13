document.addEventListener('alpine:init', () => {
    Alpine.data('authenticatedQuizApp', () => ({
        questions: [],
        error: null,
        quizzes: [],
        showQuizModal: false,
        selectedQuestionId: null,
        
        init() {
            this.fetchQuizzes();
        },

        fetchQuizzes() {
            fetch('/api/quizzes')
                .then(response => response.json())
                .then(data => {
                    this.quizzes = data;
                });
        },

        async parseQuestions(aiResponse) {
            try {
                const questionsArray = aiResponse.split('|').map(q => q.trim()).filter(q => q);
                
                this.questions = questionsArray.map((questionText, index) => {
                    // Split into question and answers
                    const parts = questionText.split(';').map(p => p.trim());
                    
                    if (parts.length !== 2) {
                        throw new Error(`Invalid question format at question ${index + 1}`);
                    }
                    
                    const question = parts[0];
                    
                    // Parse answers
                    const answersPart = parts[1];
                    const answers = answersPart.split(',').map(a => a.trim());
                    
                    if (answers.length !== 4) {
                        console.warn(`Question ${index + 1} has ${answers.length} answers and will be discarded.`);
                        return null;
                    }
                    
                    // Find which answer has the asterisk (correct answer)
                    let correctAnswerIndex = -1;
                    const cleanAnswers = answers.map((answer, i) => {
                        if (answer.endsWith('*')) {
                            correctAnswerIndex = i;
                            return answer.slice(0, -1);
                        }
                        return answer;
                    });
                    
                    if (correctAnswerIndex === -1) {
                        console.warn(`No correct answer marked for question ${index + 1} and it will be discarded.`);
                        return null;
                    }
                    
                    return {
                        id: index,
                        text: question,
                        answers: cleanAnswers,
                        correctAnswer: correctAnswerIndex,
                        saving: false,
                        saved: false
                    };
                }).filter(q => q !== null);
                
                console.log('Parsed questions:', this.questions);
                
            } catch (error) {
                console.error('Error parsing questions:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
                this.error = error.message;
            }
        },
        
        openQuizModal(questionId) {
            this.selectedQuestionId = questionId;
            this.showQuizModal = true;
        },

        async saveQuestion(quizId) {
            try {
                const question = this.questions.find(q => q.id === this.selectedQuestionId);
                if (!question || question.saved) return;
                
                question.saving = true;
                
                const response = await fetch('/save-question', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        quiz_id: quizId,
                        question: question.text,
                        answers: question.answers,
                        correct_index: question.correctAnswer
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    question.saved = true;
                    this.showQuizModal = false;
                } else {
                    throw new Error(data.message || 'Failed to save question');
                }
                
            } catch (error) {
                console.error('Error saving question:', error);
                this.error = error.message;
            } finally {
                const question = this.questions.find(q => q.id === this.selectedQuestionId);
                if (question) question.saving = false;
            }
        },
        
        async saveAllQuestions() {
            const unsavedQuestions = this.questions.filter(q => !q.saved);
            
            for (const question of unsavedQuestions) {
                await this.saveQuestion(null); // Save to default quiz
            }
        }
    }));
});

document.addEventListener('DOMContentLoaded', function() {
    // Handle study form submission
    const studyForm = document.getElementById('study-form');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (studyForm) {
        studyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading overlay
            loadingOverlay.classList.remove('d-none');
            loadingOverlay.classList.add('d-flex');
            
            try {
                const formData = new FormData(studyForm);
                
                const response = await fetch('/generate-questions', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Get Alpine component instance
                    const appEl = document.getElementById('quiz-container');
                    const app = Alpine.$data(appEl);

                    if (app) {
                        // Parse questions and update the UI
                        await app.parseQuestions(data.ai_response);
                        
                        // Hide welcome section, show questions
                        window.dispatchEvent(new CustomEvent('show-quiz'));
                    }
                    
                } else {
                    throw new Error(data.message || 'Failed to generate questions');
                }
                
            } catch (error) {
                console.error('Error generating questions:', error);
                alert('Error: ' + error.message);
            } finally {
                // Hide loading overlay
                loadingOverlay.classList.add('d-none');
                loadingOverlay.classList.remove('d-flex');
            }
        });
    }
    
    // File input handling
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');
    const fileUploadLabel = document.querySelector('.file-upload-label');
    
    if (fileInput && fileNameDisplay && fileUploadLabel) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                fileNameDisplay.textContent = fileName;
                fileUploadLabel.classList.add('file-selected');
            } else {
                fileNameDisplay.textContent = '';
                fileUploadLabel.classList.remove('file-selected');
            }
        });
    }
});
