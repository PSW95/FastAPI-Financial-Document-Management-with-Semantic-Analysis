# here we will handle all the dependencies 
from fastapi import HTTPException, Depends

from models import User

from sqlalchemy.orm import Session
from db import sess_loc
from auth_jwt import tok_deco

from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials


sec = HTTPBearer()

# check the db

def check_db():
    db = sess_loc()
    try:
        yield db
    finally:
        db.close()

# user auth        

def curr_user(token: HTTPAuthorizationCredentials= Depends(sec), db: Session=Depends(check_db)):
    try:
        db_payload = tok_deco(token.credentials)
    except Exception:
        raise HTTPException(status_code=401,detail="invalid token or token is expired")

    user = db.query(User).filter(User.id == db_payload.get("user_id")).first()

    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    return user                        