from sqlalchemy.orm import Session
from . import models, schemas

## users
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = ""  # Utilisez une méthode pour hacher le mot de passe si nécessaire
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

## groups
def get_groups(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Group).offset(skip).limit(limit).all()

def create_group(db: Session, group: schemas.GroupCreate, user_id: int):
    db_group = models.Group(**group.dict(), owner_id=user_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

## message
def create_message(db: Session, message: schemas.MessageCreate, user_id: int, group_id: int):
    db_message = models.Message(**message.dict(), sender_id=user_id, group_id=group_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Message).offset(skip).limit(limit).all()

## tasks
def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate, group_id: int):
    db_task = models.Task(**task.dict(), group_id=group_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

## files

def get_files(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.File).offset(skip).limit(limit).all()

def create_file(db:Session, file: schemas.FileCreate, group_id:int):
    db_file = models.File(**file.dict(), group_id=group_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_files_by_group(db: Session, group_id: int):
    return db.query(models.File).filter(models.File.group_id == group_id).all()





