from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://localhost:5432"
SQLALCHEMY_DATABASE_URL = "postgresql://localhost/TodoApplicationDatabase?user=postgres&password=S3r@S3r@"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()