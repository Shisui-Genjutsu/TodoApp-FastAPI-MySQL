import sys
sys.path.append("..")
from fastapi import APIRouter,Depends
from pydantic import BaseModel,Field
from database import SessionLocal,engine
from sqlalchemy.orm import Session
from typing import Optional
from .auth import user_decode_jwt,user_exception

import models

router= APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={
        404:{"description":"not found"}
    }
)

models.Base.metadata.create_all(bind=engine)

#####schema start
#Todos
class todo_schema(BaseModel):
    id:int
    title:str
    description:Optional[str] = None
    priority:int = Field(gt=-1,lt=10,description='must be in range 1 to 10') 
    complete:bool = Field(default=True)
    owner_id:int
    
#Users
# class user_schema(BaseModel):
#     email:str
#     username:str
#     first_name:str
#     last_name:str
#     hashed_password:str
#     is_active:str
    
#####schema end


def get_db():
    try:
        db =SessionLocal()
        yield db
    finally:
        db.close()
    
#---------------------------------------------Users CURD starts-------------------------------------------------#
@router.get('/')
def all_todos(db:Session=Depends(get_db)):
    todo_model = db.query(models.Todos).all()
    return todo_model

@router.get('/id/{todo_id}')
def all_todos_id(todo_id:int,user:dict=Depends(user_decode_jwt),db:Session=Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
    .filter(models.Todos.owner_id==user.get("id"))\
    .first()
    return todo_model

@router.post('/adding')
def add_todos(s:todo_schema,user:dict=Depends(user_decode_jwt),db:Session=Depends(get_db)):
    tm = models.Todos(title=s.title,description=s.description,priority=s.priority,complete=s.complete,owner_id=user.get("id"))
    db.add(tm)
    db.commit()
    db.refresh(tm)
    
    return {
        'created':tm,
        'transaction':'created successfully'
    }
    
@router.put('/updated/{todo_id}')
def updated_todo(todo_id:int,s:todo_schema,user:dict=Depends(user_decode_jwt),db:Session=Depends(get_db)):
    tm = db.query(models.Todos).filter(models.Todos.id==todo_id)\
    .filter(models.Todos.owner_id==user.get("id"))\
    .update({'title':s.title,'description':s.description,'priority':s.priority,'complete':s.complete,'owner_id':s.owner_id},synchronize_session=False)
    db.commit()
    return {
        'updated':db.query(models.Todos).filter(models.Todos).all(),
        'transaction':'updated successfully'
    }
    
@router.delete('/delete/{todo_id}')
def delete_todo(todo_id:int,db:Session=Depends(get_db)):
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete(synchronize_session=False)
    db.commit()
    return {
        'transaction':'deleted successfully'
    }
    
@router.get('/user')
def read_all_by_user(user:dict=Depends(user_decode_jwt),db:Session=Depends(get_db)):
    return db.query(models.Todos).filter(models.Todos.owner_id==user.get("id")).all()

#---------------------------------------------Todos CURD ends---------------------------------------------------#

#---------------------------------------------Users CURD starts-------------------------------------------------# 
@router.get('/Users')
def all_users(db:Session=Depends(get_db)):
    um  = db.query(models.Users).all()
    return um
#---------------------------------------------Users CURD ends---------------------------------------------------# 

   
# return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id").all())