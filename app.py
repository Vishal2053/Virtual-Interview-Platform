# app.py
import os
import logging
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from groq_service import (generate_interview_questions, evaluate_answer, 
                          generate_performance_summary)
from speech_service import text_to_speech, transcribe_audio
from flask import make_response

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret-key")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup_interview():
    field = request.form.get('field')
    position = request.form.get('position')

    if not field or not position:
        return redirect(url_for('index'))

    try:
        questions = generate_interview_questions(field, position)

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



from flask import make_response

@app.route('/interview')
def interview():
    if 'questions' not in session:
        return redirect(url_for('index'))

    questions = session.get('questions', [])
    current_idx = session.get('current_question', 0)
    field = session.get('field', '')
    position = session.get('position', '')

    if current_idx >= len(questions):
        return redirect(url_for('results'))

    current_question = questions[current_idx]

    logger.debug(f"Rendering question index: {current_idx}")

    response = make_response(render_template(
        'interview.html',
        field=field,
        position=position,
        question=current_question,
        question_number=current_idx + 1,
        total_questions=len(questions)
    ))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/get-speech', methods=['GET'])
def get_speech():
    questions = session.get('questions', [])
    current_idx = session.get('current_question', 0)

    if current_idx >= len(questions):
        return jsonify({"error": "No current question"}), 400

    current_question = questions[current_idx]

    try:
        audio_data = text_to_speech(current_question)
        return jsonify({"audio": audio_data})
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_audio_route():
    if 'audio' not in request.files:
        logger.error("No audio file provided in request")
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    try:
        transcript = transcribe_audio(audio_file)
        if transcript is None:
            logger.error("Transcription failed: No transcript returned")
            return jsonify({"error": "Failed to transcribe audio"}), 500
        return jsonify({"transcript": transcript})
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return jsonify({"error": f"Transcription error: {str(e)}"}), 500

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    try:
        data = request.get_json()
        answer = data.get("answer")

        idx = session.get("current_question", 0)
        questions = session.get("questions", [])
        if idx >= len(questions):
            return jsonify({"error": "No more questions."}), 400

        question = questions[idx]

        evaluation = evaluate_answer(session["field"], session["position"], question, answer)

        session["answers"].append(answer)
        session["evaluations"].append(evaluation)
        session["current_question"] = idx + 1

        is_complete = session["current_question"] >= len(questions)

        return jsonify({
            "evaluation": evaluation,
            "is_complete": is_complete
        })
    except Exception as e:
        logger.error(f"Submit answer failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def results():
    if 'questions' not in session or 'answers' not in session:
        return redirect(url_for('index'))

    field = session.get('field', '')
    position = session.get('position', '')
    questions = session.get('questions', [])
    answers = session.get('answers', [])
    evaluations = session.get('evaluations', [])

    if len(answers) < len(questions):
        return redirect(url_for('interview'))

    try:
        summary = generate_performance_summary(
            field=field,
            position=position,
            questions=questions,
            answers=answers,
            evaluations=evaluations
        )

        results_data = [
            {
                'question': questions[i],
                'answer': answers[i] if i < len(answers) else '',
                'evaluation': evaluations[i] if i < len(evaluations) else ''
            }
            for i in range(len(questions))
        ]

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
    if 'questions' not in session or 'answers' not in session:
        return redirect(url_for('index'))

    field = session.get('field', '')
    position = session.get('position', '')
    questions = session.get('questions', [])
    answers = session.get('answers', [])
    evaluations = session.get('evaluations', [])

    report = {
        'field': field,
        'position': position,
        'interview_data': [
            {
                'question': questions[i],
                'answer': answers[i],
                'evaluation': evaluations[i] if i < len(evaluations) else ''
            }
            for i in range(len(questions)) if i < len(answers)
        ]
    }

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

    response = jsonify(report)
    response.headers.set('Content-Disposition', 'attachment', filename='interview_report.json')
    response.headers.set('Content-Type', 'application/json')
    return response

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)