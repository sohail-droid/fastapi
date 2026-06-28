from typing import Annotated

from dataclasses import Field
from fastapi import APIRouter, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends, Path, HTTPException, FastAPI
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from database import SessionLocal
import models

router = APIRouter()



def get_db():
    #this is a session object that will be used to interact with the database When you call db = SessionLocal()
    # you're opening a temporary connection handle to your database.
    db = SessionLocal()    
    try:
        yield db #this will yield the database session object to the caller.
    finally:
        db.close() #this will close the database session object after the caller is done with it.


db_dependency = Annotated[Session, Depends(get_db)]
# db_dependency = Session = Depends(get_db) is the same as db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool



@router.get("/")
async def read_all(db: db_dependency,status_code=status.HTTP_200_OK): #this is a dependency that will be used to get the database session object.
    return db.query(models.Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")





@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.dict())

    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,todo_id: int,todo_request: TodoRequest):
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f'todo with id ({todo_id} not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete


    db.add(todo_model)
    db.commit()



@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found')
    db.query(Todos).filter(Todos.id == todo_id).delete()


    db.commit()
