from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.graph import Question, Tag, User
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


@router.get("/questions/search")
async def search_questions(
    request: Request,
    q: str = "",
    limit: int = 10,
    db: Session = Depends(get_db),
):
    results = []
    if q:
        results = (
            db.query(Question)
            .filter(Question.question.ilike(f"%{q}%"), Question.dark == False)
            .limit(limit)
            .all()
        )

    if _is_htmx(request):
        return templates.TemplateResponse(
            request, "partials/search_results.html",
            {"results": results, "query": q},
        )
    return [{"id": r.id, "question": r.question} for r in results]


@router.get("/questions")
async def list_questions(
    request: Request,
    limit: int = 20,
    page: int = 0,
    db: Session = Depends(get_db),
):
    questions = (
        db.query(Question)
        .filter(Question.dark == False)
        .offset(page * limit)
        .limit(limit)
        .all()
    )
    return [{"id": q.id, "question": q.question} for q in questions]


@router.get("/questions/{question_id}")
async def get_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if _is_htmx(request):
        return templates.TemplateResponse(
            request, "partials/question_card.html",
            {"question": question},
        )
    return question.dict(verbose=True)


class QuestionCreate(BaseModel):
    question: str
    user_id: int
    tags: list[str] = []


@router.post("/questions")
async def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(Question).filter(Question.question == payload.question).first()
    if existing:
        raise HTTPException(status_code=409, detail="Question already exists")

    q = Question(question=payload.question, user_id=payload.user_id)
    for tag_name in payload.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        q.tags.append(tag)

    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "question": q.question}
