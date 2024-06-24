from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, database
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Group)
def create_group(
    group: schemas.GroupCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_group(db=db, group=group, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Group])
def read_groups(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    groups = crud.get_groups(db, skip=skip, limit=limit)
    return groups
