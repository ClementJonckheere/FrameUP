import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request, HTTPException
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
import logging
from logging.handlers import RotatingFileHandler
from .routers import groups, messages, users, files, tasks
from .database import engine
from . import models
from .auth import oauth

load_dotenv()  # Charger les variables d'environnement depuis le fichier .env

models.Base.metadata.create_all(bind=engine)

class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("CSRF_SECRET_KEY")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add a file handler
file_handler = RotatingFileHandler("app.log", maxBytes=100000, backupCount=3)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FrameUP API"}

app.include_router(groups.router, prefix="/groups", tags=["groups"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

@app.get('/auth/github')
async def github_login(request: Request):
    redirect_uri = 'http://127.0.0.1:8000/auth/github/callback'
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get('/auth/github/callback')
async def github_auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    if token is None:
        return {"error": "Authorization failed"}
    user = await oauth.github.get('https://api.github.com/user', token=token)
    profile = user.json()
    return profile

@app.get('/auth/google')
async def google_login(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    redirect_response = await oauth.google.authorize_redirect(request, 'http://127.0.0.1:8000/auth/google/callback')
    response = RedirectResponse(url=str(redirect_response.headers['Location']))
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=True)
    return response

@app.get('/auth/google/callback')
async def google_auth(request: Request, csrf_protect: CsrfProtect = Depends()):
    state = request.query_params.get("state")
    csrf_token = request.cookies.get("csrf_token")
    logger.info("Request state: %s", state)
    logger.info("CSRF token: %s", csrf_token)
    try:
        await csrf_protect.validate_csrf(csrf_token)
        token = await oauth.google.authorize_access_token(request)
        logger.info("Token response: %s", token)
        if token is None:
            return {"error": "Authorization failed"}

        if 'id_token' not in token:
            raise HTTPException(status_code=400, detail="ID token not found in token response")

        # Utiliser le token pour parser l'ID token
        user = oauth.google.parse_id_token(token['id_token'])
        return user
    except Exception as e:
        logger.error("Error during Google auth: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
