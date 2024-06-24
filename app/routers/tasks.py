from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, database
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    group_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_task(db=db, task=task, group_id=group_id)

@router.get("/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks
