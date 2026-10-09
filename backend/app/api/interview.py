import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.interview_repository import (
    create_answer,
    create_evaluation,
    create_questions,
    delete_questions_for_session,
    get_interview_session,
    get_question_for_user,
)
from app.repositories.resume_repository import get_candidate_profile
from app.schemas.interview import (
    InterviewAnswerEvaluation,
    InterviewAnswerRequest,
    InterviewQuestion,
    InterviewQuestionRequest,
    InterviewQuestionResponse,
)
from app.services.interview_service import (
    evaluate_coding_answer,
    evaluate_interview_answer,
    generate_interview_questions,
)

router = APIRouter(
    prefix="/api/interview",
    tags=["Interview"],
)


@router.get("/health")
def interview_health():
    return {
        "status": "ok",
        "module": "interview",
    }


@router.post(
    "/questions",
    response_model=InterviewQuestionResponse,
)
def generate_questions(
    request: InterviewQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = get_interview_session(
        db,
        request.session_id,
        current_user.id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    candidate_profile = get_candidate_profile(
        db=db,
        resume_id=session.resume_id,
        user_id=current_user.id,
    )

    if candidate_profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    try:
        result = generate_interview_questions(
            candidate_profile.model_dump(mode="json"),
            interview_type=request.interview_type,
            question_count=request.question_count,
        )

        delete_questions_for_session(
            db,
            session.id,
        )

        question_models = create_questions(
            db,
            session.id,
            result.questions,
        )

        session.interview_type = request.interview_type
        session.question_count = request.question_count
        session.status = "questions_generated"

        db.commit()

        saved_questions = [
            InterviewQuestion(
                id=model.id,
                question=model.question,
                category=model.category,
                difficulty=model.difficulty,
                expected_topics=json.loads(model.expected_topics),
            )
            for model in question_models
        ]

        return InterviewQuestionResponse(
            questions=saved_questions,
        )

    except RuntimeError as exc:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to generate interview questions.",
        ) from exc


@router.post(
    "/evaluate",
    response_model=InterviewAnswerEvaluation,
)
def evaluate_answer(
    request: InterviewAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = get_question_for_user(
        db,
        request.question_id,
        current_user.id,
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Interview question not found.",
        )

    answer = request.answer.strip()

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty.",
        )

    if question.answer is not None:
        raise HTTPException(
            status_code=409,
            detail="This question has already been answered.",
        )

    try:
        if question.category.lower() == "coding":
            evaluation = evaluate_coding_answer(
                question.question,
                answer,
            )
        else:
            evaluation = evaluate_interview_answer(
                question.question,
                answer,
                question.category,
            )

        answer_model = create_answer(
            db,
            question.id,
            answer,
        )

        create_evaluation(
            db,
            answer_model.id,
            evaluation,
        )

        question.session.status = "in_progress"

        db.commit()

        return evaluation

    except RuntimeError as exc:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to evaluate interview answer.",
        ) from exc