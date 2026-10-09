from typing import Literal

from app.schemas.interview import (
    InterviewAnswerEvaluation,
    InterviewQuestionResponse,
)
from app.services.gemini_service import generate_structured


MAX_INTERVIEW_QUESTION_LENGTH = 5000
MAX_INTERVIEW_ANSWER_LENGTH = 10000
MIN_INTERVIEW_ANSWER_LENGTH = 20

InterviewType = Literal[
    "mixed",
    "technical",
    "hr",
    "resume",
    "coding",
    "ml_ai",
    "genai_rag",
]


def _type_instructions(interview_type: InterviewType, question_count: int) -> str:
    instructions = {
        "technical": "Focus on technical fundamentals and technologies explicitly present in the candidate profile.",
        "hr": "Focus on behavioral, communication, motivation, teamwork, strengths, weaknesses, and career questions appropriate for a fresher.",
        "resume": "Focus strongly on the candidate's education, projects, experience, certifications, and stated skills.",
        "coding": "Generate coding interview problems. Prefer Python because it is a stated target skill for this candidate. Every question must require writing or explaining code and must include enough information to solve it.",
        "ml_ai": "Focus on machine learning, data science, AI concepts, and technologies explicitly supported by the candidate profile.",
        "genai_rag": "Focus on GenAI, LLM, embeddings, RAG, vector databases, prompt engineering, and related concepts only when supported by the candidate profile.",
        "mixed": (
            "Create a balanced interview rather than unrelated random questions. "
            "For 10 or 15 questions include a meaningful mixture of resume/project, technical, "
            "AI/ML or GenAI where supported, behavioral, and at least one coding/problem-solving question. "
            "For 5 questions, include a smaller but still useful mix."
        ),
    }

    return (
        f"Interview type: {interview_type}.\n"
        f"Generate exactly {question_count} questions.\n"
        f"{instructions[interview_type]}"
    )


def generate_interview_questions(
    candidate_profile: dict,
    interview_type: InterviewType = "mixed",
    question_count: int = 10,
) -> InterviewQuestionResponse:
    if question_count not in (5, 10, 15):
        raise ValueError("Question count must be 5, 10, or 15.")

    prompt = f"""
You are an interview question generator for a fresher-level interview preparation system.

Candidate profile:
{candidate_profile}

{_type_instructions(interview_type, question_count)}

Strict grounding rules:
1. Use only information explicitly present in the candidate profile when making resume-specific claims.
2. Do not assume technologies, libraries, databases, tools, methods, architectures, responsibilities,
   challenges, or implementation details that are not explicitly listed.
3. Do not infer that a project used a technology merely because that technology appears elsewhere in the profile.
4. Do not invent project responsibilities or technical challenges.
5. If a project has no implementation details, ask about it at a high level.
6. Questions may test a stated skill using normal interview knowledge, but must not falsely claim the candidate used an unstated technology.
7. For coding questions, provide a self-contained problem statement in the question text, including examples or constraints when useful.
8. Coding questions must have category "Coding".
9. HR questions must have category "HR".
10. ML/AI questions must have category "ML/AI" when applicable.
11. GenAI/RAG questions must have category "GenAI/RAG" when applicable.
12. Resume/project questions must have category "Resume/Project".
13. Technical questions should use category "Technical".
14. Difficulty must be one of: Easy, Medium, Hard.
15. expected_topics must contain only useful topics directly relevant to the question.
16. Return exactly the requested number of questions.
17. Avoid duplicate questions and avoid repeating the same concept with minor wording changes.

Return only the structured response requested by the API.
"""

    response_text = generate_structured(
        prompt=prompt,
        response_schema=InterviewQuestionResponse,
    )

    try:
        result = InterviewQuestionResponse.model_validate_json(response_text)
    except Exception as exc:
        raise ValueError(
            "Gemini returned an invalid interview question response."
        ) from exc

    if len(result.questions) != question_count:
        raise ValueError(
            f"Gemini did not return exactly {question_count} interview questions."
        )

    return result


def evaluate_interview_answer(
    question: str,
    answer: str,
    category: str = "Technical",
) -> InterviewAnswerEvaluation:
    question = question.strip()
    answer = answer.strip()

    if not question:
        raise ValueError("Interview question cannot be empty.")

    if not answer:
        raise ValueError("Interview answer cannot be empty.")

    if len(question) > MAX_INTERVIEW_QUESTION_LENGTH:
        raise ValueError("Interview question is too long.")

    if len(answer) > MAX_INTERVIEW_ANSWER_LENGTH:
        raise ValueError("Interview answer is too long.")

    if len(answer) < MIN_INTERVIEW_ANSWER_LENGTH:
        raise ValueError(
            "Answer is too short. Please provide a more detailed answer."
        )

    prompt = f"""
Evaluate the candidate's answer to this interview question.

Category: {category}

Question:
{question}

Candidate answer:
{answer}

Score from 0 to 10 using correctness, relevance, clarity, depth, and technical understanding.
Give specific feedback, strengths, and improvements.
Do not invent information about the candidate.
"""

    response_text = generate_structured(
        prompt=prompt,
        response_schema=InterviewAnswerEvaluation,
    )

    try:
        return InterviewAnswerEvaluation.model_validate_json(response_text)
    except Exception as exc:
        raise ValueError("Gemini returned an invalid answer evaluation.") from exc


def evaluate_coding_answer(
    question: str,
    code: str,
) -> InterviewAnswerEvaluation:
    question = question.strip()
    code = code.strip()

    if not question:
        raise ValueError("Coding question cannot be empty.")

    if not code:
        raise ValueError("Code cannot be empty.")

    if len(code) > MAX_INTERVIEW_ANSWER_LENGTH:
        raise ValueError("Code submission is too long.")

    if len(code) < MIN_INTERVIEW_ANSWER_LENGTH:
        raise ValueError(
            "Code submission is too short. Please provide a complete solution."
        )

    prompt = f"""
You are evaluating a fresher coding interview submission.

Coding problem:
{question}

Candidate code:
{code}

Evaluate the submission.

Requirements:
- Score from 0 to 10.
- Judge correctness against the stated problem.
- Check logical errors.
- Check whether the code handles important edge cases.
- Consider code quality and readability.
- Explain the main reason for the score.
- Give strengths.
- Give specific improvements.
- Give the expected time complexity of the submitted approach.
- Give the expected space complexity of the submitted approach.
- Do not invent execution results that cannot be determined from the code.
- If the code appears incorrect, explain why.
- If the code is incomplete, mention what is missing.

Return the structured evaluation requested by the API.
"""

    response_text = generate_structured(
        prompt=prompt,
        response_schema=InterviewAnswerEvaluation,
    )

    try:
        result = InterviewAnswerEvaluation.model_validate_json(response_text)
    except Exception as exc:
        raise ValueError("Gemini returned an invalid coding evaluation.") from exc

    return result