from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, database
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Message)
def create_message(
    group_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_message(db=db, message=message, user_id=current_user.id, group_id=group_id)

@router.get("/", response_model=List[schemas.Message])
def read_messages(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
    return messages

