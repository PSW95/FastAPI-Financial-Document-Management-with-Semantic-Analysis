
from fastapi import FastAPI, UploadFile, File,HTTPException,Depends
from PyPDF2 import PdfReader
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session
from models import base,User,Docs
from db import sess_loc,en

from auth_jwt import hash_pswd, verify_pass, create_tok, verify_userrole, tok_deco
from rag_conn import add_doc,find, del_doc

from pyd_schema import create_user, login


import os



base.metadata.create_all(bind=en)

app = FastAPI()

upload_folder = "uploaded_files"
os.makedirs(upload_folder, exist_ok=True)

def check_db():
    db = sess_loc()
    try:
        yield db

    finally:
        db.close()


sec = HTTPBearer()

def curr_user(token=Depends(sec),db: Session = Depends(check_db)):
    data = tok_deco(token.credentials)
    user = db.query(User).filter(User.id == data["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="USER NOT FOUND")
    return user

#creatng the method to create or register the new users    

@app.post("/auth/register")
def register(data:create_user, db: Session= Depends(check_db)):
    # here first lest check the present or not
    present = db.query(User).filter(User.name == data.username).first()
    if present:
        raise HTTPException(status_code=400,detail="user is already exist")

    # if not then create the new
    user = User(
        name = data.username,
        passw = hash_pswd(data.password),
        role = data.role.capitalize()
    )    

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User Created Successfully"
    }

# lets make it for the login 
@app.post("/auth/login")
def login_user(data: login, db: Session = Depends(check_db)):
    user = db.query(User).filter(User.name == data.username).first()
    if not user or not verify_pass(data.password, user.passw):
        raise HTTPException(status_code=400,detail="invalid credentials")

    token = create_tok(
        {"user_id": user.id,
        "role": user.role}
    )
    return {
        "access_token": token
    }        

role_permission = {
    "Admin": ["all"],
    "Analyst": ["upload", "edit"],
    "Auditor": ["review"],
    "Client": ["view"]
}

# create for role generation
@app.post("/roles/create")
def role_create(role: str):
    role_permission[role] = []
    return {
        "message": f"{role} is created"
    }

# method for assigning the roles
@app.post("/user/assign-role")
def check_role(user_id: int, role: str, db: Session=Depends(check_db)):
    user = db.query(User).filter(User.id == user_id).first()
    user.role = role
    db.commit()
    return {
        "message": "Role Assigned"
    }


#fetch the roles by the id
@app.get("/users/{id}/roles")
def get_role(id: int, db: Session = Depends(check_db)):
    user = db.query(User).filter(User.id == id).first()
    return {
        "role": user.role
    }

# get the permission associated with the roles
@app.get("/users/{id}/permissions")
def get_perm(id: int, db: Session = Depends(check_db)):
    user = db.query(User).filter(User.id == id).first()
    return {
        "permission": role_permission.get(user.role,[])
    }  

# method for uploading the docs
@app.post("/documents/upload")
async def upload_docs(title: str, company_name: str, document_type: str, file: UploadFile= File(...), user=Depends(curr_user), db: Session = Depends(check_db)):
    verify_userrole(user, ["Admin","Analyst"])

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="only pdf files are allowed")

    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())


    doc = Docs(
        title= title,
        company_name = company_name,
        document_type  = document_type,
        path = file_path,
        uploaded_by = user.id
    )                      

    db.add(doc)
    db.commit()
    db.refresh(doc)


    return {
        "message": "Uploaded",
        "doc-id": doc.id
    }

# get alll the docs associated with user
@app.get("/documents")
def all_doc(db: Session=Depends(check_db)):
    return db.query(Docs).all()

# get by id
@app.get("/documents/{id}")
def find_doc(id: int, db: Session=Depends(check_db)):
    return db.query(Docs).filter(Docs.id == id).first()

# deleting the documents by id
@app.delete("/documents/{id}")
def del_doc(id: int, db: Session = Depends(check_db)):
    doc = db.query(Docs).filter(Docs.id == id).first()
    db.delete(doc)
    db.commit()
    return {
        "message": "Deleted"
    } 

# rang index docs
@app.post("/rag/index-documents")
def idx_doc(doc_id: int, db: Session = Depends(check_db)):
    doc = db.query(Docs).filter(Docs.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="document not found")

    read = PdfReader(doc.path)
    text = ""

    for p in read.pages:
        text += p.extract_text() or ""

    add_doc(text, doc.id)


    return {
        "message": "Indexed"
    }                    

# deleting the docs
@app.delete("/rag/remove-document/{doc_id}")
def rem_doc(doc_id: int):
    return {
        "message": "removed"
    }    

# searching the keyword or query from the docs
@app.post("/rag/search")
def raf_find(query: str):
    return {
        "results": find(query)
    }    