# import the db module and their properties 
# lets import neccessary lib
from db import base
from datetime import datetime

from sqlalchemy.orm import relationship

from sqlalchemy import Integer, String,Column, ForeignKey, TIMESTAMP

# create the user base
class User(base):
    __tablename__ = "users_data"

    id = Column(Integer,primary_key= True, index=True)
    name = Column(String(100),unique=True, nullable=False)
    passw = Column(String(255),nullable=False)
    role = Column(String(50), nullable = False)
    docs = relationship("Docs",back_populates="user")

# creating same for the documents
class Docs(base):
    __tablename__ = "users_docs"

    id = Column(Integer,primary_key= True, index=True)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255),nullable=False)
    document_type = Column(String(50), nullable=False) 
    path = Column(String(255), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users_data.id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="docs") 

