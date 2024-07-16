from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import Sessionlocal
from models import Todos, Users
from .auth import get_current_user 


router = APIRouter(
    prefix = '/user',
    tags = ['user']
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
async def get_user_new(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin' :
        raise   HTTPException(status_code=401, detail='Unauthorizxxxed')
    return db.query(Users).all()

