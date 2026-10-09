import json

from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.interview_answer import InterviewAnswer
from app.models.interview_question import InterviewQuestion as InterviewQuestionModel
from app.models.interview_session import InterviewSession
from app.schemas.interview import InterviewAnswerEvaluation, InterviewQuestion


def create_interview_session(
    db: Session,
    user_id: int,
    resume_id: int,
    status: str = "created",
) -> InterviewSession:
    session = InterviewSession(
        user_id=user_id,
        resume_id=resume_id,
        status=status,
    )
    db.add(session)
    db.flush()
    return session


def get_interview_session(
    db: Session,
    session_id: int,
    user_id: int,
) -> InterviewSession | None:
    return (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
        .first()
    )


def delete_questions_for_session(
    db: Session,
    session_id: int,
) -> None:
    db.query(InterviewQuestionModel).filter(
        InterviewQuestionModel.session_id == session_id
    ).delete(synchronize_session=False)

    db.flush()


def create_questions(
    db: Session,
    session_id: int,
    questions: list[InterviewQuestion],
) -> list[InterviewQuestionModel]:
    question_models = []

    for index, question in enumerate(questions, start=1):
        question_model = InterviewQuestionModel(
            session_id=session_id,
            question=question.question,
            category=question.category,
            difficulty=question.difficulty,
            expected_topics=json.dumps(question.expected_topics),
            question_order=index,
        )

        db.add(question_model)
        question_models.append(question_model)

    db.flush()
    return question_models


def get_question_for_user(
    db: Session,
    question_id: int,
    user_id: int,
) -> InterviewQuestionModel | None:
    return (
        db.query(InterviewQuestionModel)
        .join(
            InterviewSession,
            InterviewQuestionModel.session_id == InterviewSession.id,
        )
        .filter(
            InterviewQuestionModel.id == question_id,
            InterviewSession.user_id == user_id,
        )
        .first()
    )


def create_answer(
    db: Session,
    question_id: int,
    answer: str,
) -> InterviewAnswer:
    answer_model = InterviewAnswer(
        question_id=question_id,
        answer=answer,
    )

    db.add(answer_model)
    db.flush()

    return answer_model


def create_evaluation(
    db: Session,
    answer_id: int,
    evaluation: InterviewAnswerEvaluation,
) -> Evaluation:
    evaluation_model = Evaluation(
        answer_id=answer_id,
        score=evaluation.score,
        feedback=evaluation.feedback,
        strengths=json.dumps(evaluation.strengths),
        improvements=json.dumps(evaluation.improvements),
    )

    db.add(evaluation_model)
    db.flush()

    return evaluation_model