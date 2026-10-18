from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.graph import Question

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/learn")
async def learn(request: Request, id: int | None = None, db: Session = Depends(get_db)):
    question = None
    if id:
        question = db.query(Question).filter(Question.id == id).first()
    return templates.TemplateResponse(request, "learn.html", {
        "question": question,
        "question_id": id,
    })


@router.get("/about")
async def about(request: Request):
    return templates.TemplateResponse(request, "about.html")
