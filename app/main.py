from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import pages, questions, answers, tags, auth

app = FastAPI(title="Skillsera", docs_url="/api/docs" if settings.debug else None)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(',') if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(tags.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup():
    create_tables()
