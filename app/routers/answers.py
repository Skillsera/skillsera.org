import re
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.graph import Answer, Question, question_answers
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

YOUTUBE_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_\-]{11})"
)


def youtube_video_id(url: str) -> str | None:
    m = YOUTUBE_RE.search(url)
    return m.group(1) if m else None


class AnswerCreate(BaseModel):
    question_id: int
    user_id: int
    url: str
    start: Optional[int] = None
    stop: Optional[int] = None


@router.post("/answers")
async def create_answer(
    request: Request,
    question_id: int = Form(...),
    user_id: int = Form(...),
    url: str = Form(...),
    start: Optional[int] = Form(None),
    stop: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    if not youtube_video_id(url):
        raise HTTPException(status_code=422, detail="URL must be a valid YouTube link")

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    answer = Answer(user_id=user_id, url=url, start=start, stop=stop)
    db.add(answer)
    db.flush()
    question.answers.append(answer)
    db.commit()
    db.refresh(answer)

    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            request, "partials/answer_item.html",
            {"answer": answer},
        )
    return answer.dict()


@router.get("/answers/{answer_id}")
async def get_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return answer.dict()
