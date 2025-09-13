document.addEventListener('alpine:init', () => {
    Alpine.data('quizApp', () => ({
        questions: [],
        loading: false,
        error: null,
        
        async parseQuestions(aiResponse) {
            try {
                const questionsArray = aiResponse.split('|').map(q => q.trim()).filter(q => q);
                
                this.questions = questionsArray.map((questionText, index) => {
                    // Split into question and answers
                    const parts = questionText.split(';').map(p => p.trim());
                    
                    if (parts.length !== 2) {
                        console.warn(`Invalid question format at question ${index + 1} and it will be discarded.`);
                        return null;
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
                        selectedAnswer: null,
                        showResult: false
                    };
                }).filter(q => q !== null);
                
                console.log('Parsed questions:', this.questions);
                
            } catch (error) {
                console.error('Error parsing questions:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
                this.error = error.message;
            }
        },
        
        selectAnswer(questionId, answerIndex) {
            const question = this.questions.find(q => q.id === questionId);
            if (question && !question.showResult) {
                question.selectedAnswer = answerIndex;
            }
        },
        
        submitAnswer(questionId) {
            const question = this.questions.find(q => q.id === questionId);
            if (question && question.selectedAnswer !== null) {
                question.showResult = true;
            }
        },
        
        getAnswerClass(questionId, answerIndex) {
            const question = this.questions.find(q => q.id === questionId);
            if (!question) return {};
            
            if (question.selectedAnswer === answerIndex && !question.showResult) {
                return 'selected-answer';
            }
            
            if (question.showResult) {
                if (answerIndex === question.correctAnswer) {
                    return 'correct-answer';
                }
                if (answerIndex === question.selectedAnswer && answerIndex !== question.correctAnswer) {
                    return 'incorrect-answer';
                }
            }
            
            return {};
        },
        
        switchToQuizView() {
            // Dispatch a custom event to switch to the quiz view
            window.dispatchEvent(new CustomEvent('show-quiz'));
        }
    }));
});

document.addEventListener('DOMContentLoaded', function() {
    // Handle study form submission for guest users
    const studyForm = document.getElementById('study-form');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (studyForm) {
        studyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.remove('d-none');
                loadingOverlay.classList.add('d-flex');
                loadingOverlay.style.display = 'flex';
            }
            
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
                        app.switchToQuizView();
                    }
                    
                } else {
                    throw new Error(data.message || 'Failed to generate questions');
                }
                
            } catch (error) {
                console.error('Error generating questions:', error);
                alert('Error: ' + error.message);
            } finally {
                // Hide loading overlay
                if (loadingOverlay) {
                    loadingOverlay.classList.add('d-none');
                    loadingOverlay.classList.remove('d-flex');
                }
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
