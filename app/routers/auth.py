import requests
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.config import settings
from app.database import get_db
from app.models.graph import User

router = APIRouter()

SESSION_KEY = "skillsera_session"


def _get_session(request: Request) -> dict:
    return request.session if hasattr(request, "session") else {}


class LoginRequest(BaseModel):
    email: str
    password: str
    redirect: str = "/"


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


def _authenticate(email: str, password: str) -> dict:
    try:
        r = requests.post(
            f"{settings.auth_server_url}/authorize",
            data={"email": email, "password": password},
            timeout=10,
        )
        resp = r.json()
        if "http_error_code" not in resp:
            return resp
        raise HTTPException(status_code=401, detail=resp.get("msg", "Authentication failed"))
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Auth server unavailable: {e}")


def _ensure_user(db: Session, email: str, username: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/auth/login")
async def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    resp = _authenticate(payload.email, payload.password)
    session_data = resp.get("session", {})
    email = session_data.get("email", payload.email)
    username = session_data.get("username", "")

    user = _ensure_user(db, email, username)
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["logged"] = True

    return {"logged": True, "username": user.username, "id": user.id}


@router.post("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return {"logged": False}


@router.post("/auth/register")
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        r = requests.post(
            f"{settings.auth_server_url}/register",
            data={
                "email": payload.email,
                "name": payload.username,
                "password": payload.password,
                "password_conf": payload.password,
                "service": "skillsera",
            },
            timeout=10,
        )
        resp = r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Auth server unavailable: {e}")

    if "http_error_code" in resp or "id" not in resp:
        raise HTTPException(status_code=400, detail=resp.get("msg", "Registration failed"))

    _ensure_user(db, payload.email, payload.username)
    return {"msg": "Registration successful. Check your email to activate your account."}


@router.get("/auth/activate")
async def activate(email: str, secret: str):
    try:
        r = requests.get(
            f"{settings.auth_server_url}/activate",
            params={"email": email, "secret": secret},
            timeout=10,
        )
        resp = r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Auth server unavailable: {e}")

    if resp is True:
        return {"msg": "Activation successful"}
    raise HTTPException(status_code=400, detail=resp.get("msg", "Activation failed"))


@router.post("/auth/session")
async def session(request: Request):
    if request.session.get("logged"):
        return {
            "logged": True,
            "username": request.session.get("username"),
            "id": request.session.get("user_id"),
        }
    return {"logged": False}
