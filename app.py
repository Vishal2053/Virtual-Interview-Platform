import os
import logging
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from groq_service import (generate_interview_questions, evaluate_answer, 
                          generate_performance_summary)
from speech_service import text_to_speech

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret-key")

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup_interview():
    """Handle interview setup and generate questions."""
    field = request.form.get('field')
    position = request.form.get('position')
    
    if not field or not position:
        return redirect(url_for('index'))
    
    try:
        # Generate interview questions based on field and position
        questions = generate_interview_questions(field, position)
        
        # Store interview data in session
        session['field'] = field
        session['position'] = position
        session['questions'] = questions
        session['current_question'] = 0
        session['answers'] = []
        session['evaluations'] = []
        
        return redirect(url_for('interview'))
    except Exception as e:
        logger.error(f"Error setting up interview: {str(e)}")
        return render_template('index.html', error=f"Error: {str(e)}")

@app.route('/interview')
def interview():
    """Render the interview page."""
    # Check if interview is set up
    if 'questions' not in session:
        return redirect(url_for('index'))
    
    questions = session.get('questions', [])
    current_idx = session.get('current_question', 0)
    field = session.get('field', '')
    position = session.get('position', '')
    
    # Check if interview is complete
    if current_idx >= len(questions):
        return redirect(url_for('results'))
    
    current_question = questions[current_idx]
    
    return render_template('interview.html', 
                          field=field,
                          position=position,
                          question=current_question,
                          question_number=current_idx + 1,
                          total_questions=len(questions))

@app.route('/get-speech', methods=['GET'])
def get_speech():
    """Generate speech for the current question."""
    questions = session.get('questions', [])
    current_idx = session.get('current_question', 0)
    
    if current_idx >= len(questions):
        return jsonify({"error": "No current question"}), 400
    
    current_question = questions[current_idx]
    
    try:
        # Generate speech audio for the question
        audio_data = text_to_speech(current_question)
        return jsonify({"audio": audio_data})
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    """Process user's answer and evaluate it."""
    if 'questions' not in session:
        return jsonify({"error": "No active interview"}), 400
    
    data = request.get_json()
    answer = data.get('answer')
    
    if not answer:
        return jsonify({"error": "Answer is required"}), 400
    
    questions = session.get('questions', [])
    current_idx = session.get('current_question', 0)
    field = session.get('field', '')
    position = session.get('position', '')
    
    if current_idx >= len(questions):
        return jsonify({"error": "Interview already complete"}), 400
    
    current_question = questions[current_idx]
    
    try:
        # Evaluate the answer
        evaluation = evaluate_answer(
            field=field,
            position=position,
            question=current_question,
            answer=answer
        )
        
        # Store answer and evaluation
        answers = session.get('answers', [])
        evaluations = session.get('evaluations', [])
        
        answers.append(answer)
        evaluations.append(evaluation)
        
        session['answers'] = answers
        session['evaluations'] = evaluations
        
        # Move to next question
        session['current_question'] = current_idx + 1
        
        # Check if interview is complete
        if current_idx + 1 >= len(questions):
            is_complete = True
        else:
            is_complete = False
            
        return jsonify({
            "success": True,
            "evaluation": evaluation,
            "is_complete": is_complete
        })
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def results():
    """Display interview results and performance summary."""
    # Check if interview data exists
    if 'questions' not in session or 'answers' not in session:
        return redirect(url_for('index'))
    
    field = session.get('field', '')
    position = session.get('position', '')
    questions = session.get('questions', [])
    answers = session.get('answers', [])
    evaluations = session.get('evaluations', [])
    
    # Check if all questions were answered
    if len(answers) < len(questions):
        return redirect(url_for('interview'))
    
    try:
        # Generate overall performance summary
        summary = generate_performance_summary(
            field=field,
            position=position,
            questions=questions,
            answers=answers,
            evaluations=evaluations
        )
        
        # Prepare results for template
        results_data = []
        for i in range(len(questions)):
            results_data.append({
                'question': questions[i],
                'answer': answers[i] if i < len(answers) else '',
                'evaluation': evaluations[i] if i < len(evaluations) else ''
            })
        
        return render_template('results.html',
                              field=field,
                              position=position,
                              results=results_data,
                              summary=summary)
    except Exception as e:
        logger.error(f"Error generating results: {str(e)}")
        return render_template('index.html', error=f"Error: {str(e)}")

@app.route('/download-report')
def download_report():
    """Generate and download interview report as JSON."""
    if 'questions' not in session or 'answers' not in session:
        return redirect(url_for('index'))
    
    field = session.get('field', '')
    position = session.get('position', '')
    questions = session.get('questions', [])
    answers = session.get('answers', [])
    evaluations = session.get('evaluations', [])
    
    # Prepare report data
    report = {
        'field': field,
        'position': position,
        'interview_data': []
    }
    
    for i in range(len(questions)):
        if i < len(answers):
            report['interview_data'].append({
                'question': questions[i],
                'answer': answers[i],
                'evaluation': evaluations[i] if i < len(evaluations) else ''
            })
    
    # Generate summary if available
    try:
        summary = generate_performance_summary(
            field=field,
            position=position,
            questions=questions,
            answers=answers,
            evaluations=evaluations
        )
        report['summary'] = summary
    except Exception as e:
        logger.error(f"Error generating summary for report: {str(e)}")
        report['summary'] = "Error generating summary"
    
    # Convert to JSON and return
    response = jsonify(report)
    response.headers.set('Content-Disposition', 'attachment', filename='interview_report.json')
    response.headers.set('Content-Type', 'application/json')
    return response

@app.route('/reset')
def reset():
    """Reset the interview session and return to home page."""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)