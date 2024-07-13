from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import Sessionlocal
from models import Todos
from .auth import get_current_user 


router = APIRouter(
    prefix = '/admin',
    tags = ['admin']
)

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

@router.get("/", status_code = status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin' : 
        raise   HTTPException(status_code=401, detail='Unauthorized')
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_todo(user : user_dependency,
                      db : db_dependency, todo_id : int = Path(gt=0)):
    if user is None or user.get('role') != 'admin' : 
        raise   HTTPException(status_code=401, detail='Unauthorized')
    
    todo_model = db.query(Todos)\
                   .filter(Todos.id == todo_id)\
                   .first()
    if todo_model is None : 
        raise HTTPException(status_code = 404, detail = 'Todo not found.')
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()