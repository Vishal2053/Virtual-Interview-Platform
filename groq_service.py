import os
import logging
from typing import List, Dict, Any
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Groq API configuration
GROQ_API_KEY = "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"  # Update this if needed
GROQ_MODEL = "llama-3.3-70b-versatile"  # Default model
client = Groq(api_key=GROQ_API_KEY)

def check_api_key() -> None:
    """Check if the Groq API key is configured."""
    if not GROQ_API_KEY:
        raise ValueError("Groq API key is missing. Please set the GROQ_API_KEY environment variable.")

def call_groq_api(messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
    """
    Make an API call to Groq.
    
    Args:
        messages: List of message dictionaries with role and content
        temperature: Sampling temperature (0-1)
        
    Returns:
        Parsed JSON response from the Groq API
    """
    check_api_key()
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=temperature
        )
        # Parse the JSON string returned in the content
        content = response.choices[0].message.content
        return json.loads(content)  # Parse and return the JSON object
    except Exception as e:
        logger.error(f"Error in Groq API call: {str(e)}")
        raise

def generate_interview_questions(field: str, position: str) -> List[str]:
    """
    Generate interview questions based on field and position.
    
    Args:
        field: The field or domain (e.g., Data Science, Software Engineering)
        position: The position or role (e.g., Data Analyst, Backend Developer)
        
    Returns:
        List of generated interview questions
    """
    logger.debug(f"Generating interview questions for {position} in {field}")
    
    prompt = f"""
    You are an expert interviewer in the field of {field}. 
    Generate 10 professional interview questions for a {position} position.
    Focus on both technical and behavioral questions that would effectively evaluate a candidate.
    The questions should be challenging but fair, and cover key skills and knowledge areas for this role.
    
    Return the response in JSON format with a key 'questions' containing an array of questions.
    Example: {{"questions": ["question1", "question2", ...]}}
    """
    
    messages = [
        {"role": "system", "content": "You are an AI assistant that generates professional interview questions in JSON format."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = call_groq_api(messages, temperature=0.8)
        questions = response.get("questions", [])
        
        # Filter out any non-question lines and ensure questions end with '?'
        questions = [q.strip() for q in questions if q.strip().endswith('?')]
        
        # Ensure we have at least 5 questions
        if len(questions) < 5:
            raise Exception("Failed to generate enough interview questions")
            
        return questions
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise

def evaluate_answer(field: str, position: str, question: str, answer: str) -> Dict[str, Any]:
    """
    Evaluate the answer given by the user.
    
    Args:
        field: The field or domain
        position: The position or role
        question: The question asked
        answer: The user's answer
        
    Returns:
        Dictionary containing evaluation results and feedback
    """
    logger.debug(f"Evaluating answer for question: {question}")
    
    prompt = f"""
    You are evaluating a candidate's interview answer for a {position} position in {field}.
    
    Question: {question}
    
    Candidate's Answer: {answer}
    
    Please evaluate the answer on the following criteria:
    1. Relevance to the question (scored 1-10)
    2. Technical accuracy (scored 1-10)
    3. Clarity and communication (scored 1-10)
    4. Overall impression (scored 1-10)
    
    Then provide:
    - Brief feedback (2-3 sentences) with constructive criticism
    - A short, encouraging comment to motivate the candidate
    
    Return the response in JSON format with the following keys:
    - relevance_score
    - technical_score
    - clarity_score
    - overall_score
    - feedback
    - encouragement
    """
    
    messages = [
        {"role": "system", "content": "You are an AI assistant that evaluates interview answers and returns results in JSON format."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        evaluation = call_groq_api(messages, temperature=0.7)
        
        # Ensure all required fields are present
        required_fields = [
            'relevance_score', 'technical_score', 'clarity_score', 
            'overall_score', 'feedback', 'encouragement'
        ]
        
        for field in required_fields:
            if field not in evaluation:
                evaluation[field] = "Not provided" if field in ['feedback', 'encouragement'] else 5
                
        return evaluation
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        # Return default evaluation to avoid breaking the interview flow
        return {
            'relevance_score': 5,
            'technical_score': 5,
            'clarity_score': 5,
            'overall_score': 5,
            'feedback': "We experienced an issue evaluating your answer.",
            'encouragement': "Let's continue with the next question."
        }

def generate_performance_summary(field: str, position: str, questions: List[str], 
                                answers: List[str], evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate an overall performance summary for the interview.
    
    Args:
        field: The field or domain
        position: The position or role
        questions: List of questions asked
        answers: List of answers provided
        evaluations: List of evaluation results
        
    Returns:
        Dictionary containing summary information
    """
    logger.debug("Generating performance summary")
    
    # Prepare interview data for the prompt
    interview_data = ""
    for i in range(len(questions)):
        if i < len(answers) and i < len(evaluations):
            interview_data += f"Question {i+1}: {questions[i]}\n"
            interview_data += f"Answer: {answers[i]}\n"
            interview_data += f"Evaluation Scores: "
            interview_data += f"Relevance: {evaluations[i].get('relevance_score', 'N/A')}, "
            interview_data += f"Technical: {evaluations[i].get('technical_score', 'N/A')}, "
            interview_data += f"Clarity: {evaluations[i].get('clarity_score', 'N/A')}, "
            interview_data += f"Overall: {evaluations[i].get('overall_score', 'N/A')}\n\n"
    
    prompt = f"""
    You are analyzing the results of an interview for a {position} position in {field}.
    
    Here is the interview data:
    
    {interview_data}
    
    Based on this interview data, please provide:
    
    1. An overall assessment of the candidate's performance (3-5 sentences)
    2. Key strengths demonstrated in the interview (list 2-4 strengths)
    3. Areas for improvement (list 2-3 areas)
    4. Recommendations for further preparation (2-3 specific recommendations)
    5. A rating out of 100 that reflects overall interview performance
    
    Return the response in JSON format with the following keys:
    - overall_assessment
    - strengths (array)
    - improvement_areas (array)
    - recommendations (array)
    - performance_rating (number out of 100)
    """
    
    messages = [
        {"role": "system", "content": "You are an AI assistant that analyzes interview performance and returns results in JSON format."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        summary = call_groq_api(messages, temperature=0.7)
        
        # Ensure all required fields are present
        required_fields = [
            'overall_assessment', 'strengths', 'improvement_areas', 
            'recommendations', 'performance_rating'
        ]
        
        for field in required_fields:
            if field not in summary:
                if field in ['strengths', 'improvement_areas', 'recommendations']:
                    summary[field] = ["Not provided"]
                elif field == 'performance_rating':
                    summary[field] = 70  # Default score
                else:
                    summary[field] = "Not provided"
                    
        return summary
    except Exception as e:
        logger.error(f"Error generating performance summary: {str(e)}")
        # Return default summary to avoid breaking the application flow
        return {
            'overall_assessment': "Unable to generate a complete assessment due to technical issues.",
            'strengths': ["Communication skills"],
            'improvement_areas': ["Further technical preparation"],
            'recommendations': ["Practice more mock interviews"],
            'performance_rating': 70
        }