from sqlalchemy import Boolean, Column, Integer, String,ForeignKey,VARCHAR
from database import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"
    
    id  = Column(Integer,primary_key=True,index=True)
    email = Column(VARCHAR(100),unique=True,index=True)
    username = Column(VARCHAR(100),unique=True,index=True)
    first_name=Column(VARCHAR(100))
    last_name=Column(VARCHAR(100))
    hashed_password = Column(VARCHAR(100))
    is_active=Column(Boolean,default=True)
    
    todos = relationship('Todos', back_populates = 'owner')
    
class Todos(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key = True, index=True)
    title = Column(VARCHAR(100))
    description = Column(VARCHAR(100))
    priority = Column(Integer)
    complete = Column(Boolean, default = False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    owner = relationship('Users', back_populates = 'todos')

