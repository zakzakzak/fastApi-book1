from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from database import engine, Sessionlocal
from models import Todos
import models

app = FastAPI()

# Hanya akan jalan ketika belum ada table nya
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = Sessionlocal()
    try : 
        yield db
    finally :
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db: db_dependency):
    # Depends() -> Dependency Injection : Menjalankan function get_db saat mulai, dan selesai (finally)
    return db.query(Todos).all()
