from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import Sessionlocal
from models import Todos, Users
from .auth import get_current_user 
from passlib.context import CryptContext


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
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password : str
    new_password : str = Field(min_length=6)

@router.get("/", status_code = status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None :
        raise   HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/password", status_code = status.HTTP_204_NO_CONTENT)
async def change_password(user : user_dependency, db : db_dependency, userVerif : UserVerification):
    if user is None :
        raise   HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    
    if not bcrypt_context.verify(userVerif.password, user_model.hashed_password) : 
        raise   HTTPException(status_code=401, detail='Wrong password')
    user_model.hashed_password = bcrypt_context.hash(userVerif.new_password)
    db.add(user_model)
    db.commit()
    # if user.get('hashed_password') != bcrypt_context.hash(userVerif.get('password')) : 
    #     raise   HTTPException(status_code=401, detail='Wrong password!')
    
