from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import crud, models, schemas, database
from ..auth import authenticate_user, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/signup", response_model=schemas.User, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token, tags=["users"])
def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
    )
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/refresh", response_model=schemas.Token, tags=["users"])
def refresh_access_token(refresh_token: str, db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, user_id=user_id)
    if user is None or user.refresh_token != refresh_token:
        raise credentials_exception
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/{provider}/callback", response_model=schemas.User, tags=["users"])
async def auth_callback(provider: str, request: Request, db: Session = Depends(database.get_db)):
    if provider == "github":
        token = await oauth.github.authorize_access_token(request)
        user_info = await oauth.github.get('https://api.github.com/user', token=token)
    elif provider == "google":
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    user_data = user_info.json()
    username = user_data.get("login") or user_data.get("email")
    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided")

    user = crud.get_user_by_email(db, email=email)
    if not user:
        user = crud.create_user(db, schemas.UserCreate(username=username, email=email, password=""))

    return user


