document.addEventListener('alpine:init', () => {
    Alpine.data('quizApp', () => ({
        questions: [],
        currentQuestionIndex: 0,
        userAnswers: [],
        quizSubmitted: false,
        score: 0,
        loading: true,
        quizId: null,
        
        init() {
            // Get quiz ID from URL
            const pathParts = window.location.pathname.split('/');
            this.quizId = pathParts[pathParts.length - 1];
            
            if (!this.quizId) {
                console.error('Quiz ID not found in URL');
                return;
            }
            
            this.fetchQuizData();
        },
        
        fetchQuizData() {
            this.loading = true;
            fetch(`/api/quiz/${this.quizId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch quiz data');
                    }
                    return response.json();
                })
                .then(data => {
                    this.questions = data.questions;
                    
                    // Initialize userAnswers array with null values
                    this.userAnswers = new Array(this.questions.length).fill(null);
                    
                    this.loading = false;
                })
                .catch(error => {
                    console.error('Error fetching quiz data:', error);
                    this.loading = false;
                });
        },
        
        selectAnswer(questionIndex, answerIndex) {
            if (this.quizSubmitted) return;
            
            this.userAnswers[questionIndex] = answerIndex;
        },
        
        isSelected(questionIndex, answerIndex) {
            return this.userAnswers[questionIndex] === answerIndex;
        },
        
        previousQuestion() {
            if (this.currentQuestionIndex > 0) {
                this.currentQuestionIndex--;
            }
        },
        
        nextQuestion() {
            if (this.currentQuestionIndex < this.questions.length - 1) {
                this.currentQuestionIndex++;
            }
        },
        
        submitQuiz() {
            // Check if all questions are answered
            const unansweredQuestions = this.userAnswers.filter(answer => answer === null).length;
            
            if (unansweredQuestions > 0) {
                if (!confirm(`You have ${unansweredQuestions} unanswered question(s). Do you want to submit anyway?`)) {
                    return;
                }
            }
            
            this.loading = true;
            
            const submission = {
                quiz_id: this.quizId,
                answers: this.userAnswers
            };
            
            fetch('/submit_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(submission)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to submit quiz');
                }
                return response.json();
            })
                            .then(data => {
                                this.score = data.score;
                                this.quizSubmitted = true;
                                this.loading = false;
                            })            .catch(error => {
                console.error('Error submitting quiz:', error);
                this.loading = false;
                alert('Failed to submit quiz. Please try again.');
            });
        },
        
        getProgressPercentage() {
            const answeredCount = this.userAnswers.filter(answer => answer !== null).length;
            return (answeredCount / this.questions.length) * 100;
        },
        
        getFeedbackMessage() {
            const percentage = (this.score / this.questions.length) * 100;
            
            if (percentage >= 90) {
                return "Excellent! You've mastered this material!";
            } else if (percentage >= 80) {
                return "Great job! You have a strong understanding of the material.";
            } else if (percentage >= 70) {
                return "Good work! You're on the right track.";
            } else if (percentage >= 60) {
                return "Not bad! With a bit more study, you'll improve your score.";
            } else {
                return "Keep studying! Review the material and try again.";
            }
        }
    }));
});
