from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import Sessionlocal
from models import Todos
from .auth import get_current_user 


router = APIRouter()

# # Hanya akan jalan ketika belum ada table nya
# models.Base.metadata.create_all(bind=engine)
# app.include_router(auth.router)

def get_db():
    db = Sessionlocal()
    try : 
        yield db
    finally :
        db.close()

# Depends() -> Dependency Injection : Menjalankan function get_db saat mulai, dan selesai (finally)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title       : str = Field(min_length = 3)
    description : str = Field(min_length = 3, max_length = 100)
    priority    : int = Field(gt=0, lt=6)
    complete    : bool 



@router.get("/", status_code = status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None : 
        raise   HTTPException(status_code=401, detail='Unauthorized')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todos/{todo_id}", status_code = status.HTTP_200_OK)
async def read_todo(user : user_dependency, db: db_dependency, todo_id:int= Path(gt=0)):
    if user is None : 
        raise   HTTPException(status_code=401, detail='Unauthorized')
    todo_model = db.query(Todos)\
                   .filter(Todos.id == todo_id)\
                   .filter(Todos.owner_id == user.get('id'))\
                   .first()
    if todo_model is not None : 
        return todo_model
    raise HTTPException(status_code = 404, detail='Todo not found.')

@router.post("/todo", status_code = status.HTTP_200_OK)
async def create_todo(user : user_dependency, db: db_dependency, 
                      todo_request : TodoRequest):
    if user is None : 
        raise   HTTPException(status_code=401, detail='Unauthorized')
    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()

@router.post("/todo/{todo_id}", status_code = status.HTTP_200_OK)
async def update_todo(user : user_dependency,
                      db : db_dependency, 
                      todo_request : TodoRequest,
                      todo_id : int = Path(gt=0) ):
    if user is None : 
        raise   HTTPException(status_code=401, detail='Unauthorized')
    todo_model = db.query(Todos)\
                   .filter(Todos.id == todo_id)\
                   .filter(Todos.owner_id == user.get('id'))\
                   .first()
    if todo_model is None : 
        raise HTTPException(status_code = 404, detail = 'Todo not found.')
    
    todo_model.title = todo_request.title 
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete 
    
    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code = status.HTTP_200_OK)
async def delete_todo(db : db_dependency, todo_id : int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None : 
        raise HTTPException(status_code = 404, detail = 'Todo not found.')
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    
