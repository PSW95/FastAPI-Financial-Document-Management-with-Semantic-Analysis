# lest here import our pydantic base model
from pydantic import BaseModel
from datetime import datetime

from typing import Optional


class create_user(BaseModel):
    username: str 
    password: str 
    role: str


class login(BaseModel):
    username:  str
    password: str




class docs_base(BaseModel):
    title: str
    document_type: str 

class docs_res(docs_base):
    id: int 
    path: str 
    uploaded_by: int 
    created_at: datetime

    class Config:
        orm_mode = True


class query_req(BaseModel):
    query: str 

class query_res(BaseModel):
    doc_id: Optional[int]
    text: str    

                