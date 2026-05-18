"""
Gemini AI wrapper for the Chandramonians educational hub.

Usage:
    from webapp.ai_service import get_tutoring_response
    answer = get_tutoring_response("What is photosynthesis?", subject="Biology")

To swap AI providers in the future, only modify this file.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an academic tutor for students of Dulalpur Chandramoni High School (DCMHS) in Bangladesh.

Your role:
- Answer academic questions clearly and step-by-step
- Focus on SSC and HSC (Bangladesh secondary and higher secondary) curriculum
- Use simple, encouraging language appropriate for high school students
- For mathematics and science, always show the complete working/steps
- For Bengali literature or language questions, you may respond with relevant Bengali terms but keep explanations in English
- If a question is off-topic (not educational), politely redirect the student
- Keep responses concise but complete — aim for 150-300 words

Always end with an encouraging note for the student."""


def get_tutoring_response(question: str, subject: str = "", chat_history: list = None) -> str:
    """
    Send a question to Google Gemini and return the answer.

    Args:
        question: The student's question
        subject: Optional subject context (e.g. "Mathematics", "Physics")
        chat_history: Optional list of prior messages for context

    Returns:
        AI response string, or an error message if the API fails.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return "AI tutoring is not configured yet. Please contact the administrator."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT,
        )

        subject_prefix = f"[Subject: {subject}]\n" if subject else ""
        prompt = f"{subject_prefix}{question}"

        response = model.generate_content(prompt)
        return response.text

    except ImportError:
        logger.error("google-generativeai package not installed")
        return "AI service is not available. Please install required packages."
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "Sorry, the AI tutor is temporarily unavailable. Please try again later."


def get_problem_solution(problem: str, subject: str = "") -> str:
    """
    Solve a specific academic problem with detailed steps.
    Optimized for math, physics, and chemistry problems.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return "AI service is not configured. Please contact the administrator."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(model_name='gemini-1.5-flash')

        prompt = f"""Solve this {subject} problem step by step for a DCMHS (Bangladesh) high school student:

Problem: {problem}

Format your response as:
1. Understanding the problem
2. Method/Formula to use
3. Step-by-step solution
4. Final answer (clearly highlighted)
5. Quick tip to remember this type of problem"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        logger.error(f"Gemini problem solver error: {e}")
        return "Sorry, the problem solver is temporarily unavailable. Please try again."
