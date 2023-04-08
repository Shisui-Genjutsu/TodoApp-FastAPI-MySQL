import sys
sys.path.append("..")
from fastapi import Depends,HTTPException,APIRouter
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal,engine
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
import models

router= APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        401:{"user":"not found"}
    }
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

models.Base.metadata.create_all(bind=engine)  

SECRET_KEY = "ThisWorldShallKnowPain"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

#####password hashing
def pass_hashing(password):
    return bcrypt_context.hash(password)

#####user password validation
def pass_verify(plainpassword,hashpassword):
    return bcrypt_context.verify(plainpassword,hashpassword)

#####schemas
class users_schema(BaseModel):
    id:int
    username:Optional[str] = None
    email:str
    first_name:str
    last_name:str
    password:str
#####db func
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
 
 #####user validation
def  authenticate_user(username:str,password:str,db:Session=Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    
    if not user:
        return False
    if not pass_verify(password,user.hashed_password):
        return False
    else:
        return user
    
#####token generation
def token_gen(username:str, user_id:int, expire_delta:Optional[timedelta]=None):
    encode = {'usr':username,'usrId':user_id}
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({'exp':expire})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

@router.post('/token') 
def login_user_auth(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    token_expires = timedelta(minutes=20)
    token = token_gen(user.username,user.id,expire_delta=token_expires)
    return {
        'token' : token,
        'transacion':'User is authenticated Successfully'
    }
    
#####JWT Decoding
@router.post('/jwtdecode/')
def user_decode_jwt(token: str=Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("usr")
        user_id:int=payload.get("usrId")
    
        if username is None or user_id is None:
            raise HTTPException(
                status_code=404,
                detail='username or password not found'
            )
        
        return {'username':username,'id':user_id}
    except JWTError:
        raise HTTPException(
            status_code=404,
            detail='username or password  not found'
        )
        
#####CURD OPERATIONS 
@router.post('/Users')

def create_users(us:users_schema,db:Session=Depends(get_db)):
    hashed_password = pass_hashing(us.password)
    um = models.Users(email=us.email,username=us.username,first_name=us.first_name,last_name=us.last_name,hashed_password=hashed_password,is_active=True)
    
    db.add(um)
    db.commit()
    return {
        'created':db.query(models.Users).all(),
        'transction':'Created Succesfully'
    }

#####Exception Functions
def user_exception():
    return HTTPException(
        status_code=404,
        detail='User not found'
    )