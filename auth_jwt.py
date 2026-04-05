# lets handle our authentication our authorized user with token based and with hashed
from fastapi import HTTPException

from jose import jwt,JWTError

from passlib.context import CryptContext



sec_key = "secret123"
algo = "HS256"

pass_hash = CryptContext(schemes=["pbkdf2_sha256"],deprecated="auto")

def hash_pswd(password: str):
    return pass_hash.hash(password)

def verify_pass(password: str, hashed: str):
    return pass_hash.verify(password,hashed)



def create_tok(data:dict):
    return jwt.encode(data, sec_key,algorithm=algo)


def tok_deco(token:str):
    try:
        dec_paload = jwt.decode(token,sec_key, algorithms=[algo])
        return dec_paload


    except JWTError:
        raise HTTPException(status_code=401,detail="token is invalid or expired")



def verify_userrole(user, allowed_roles):
    if user.role not in allowed_roles:
        raise HTTPException(status_code=403,detail="access denied")


