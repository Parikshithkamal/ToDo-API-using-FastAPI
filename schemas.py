from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ToDoCreate(BaseModel):
    title:str
    description:str

class ToDoUpdate(BaseModel):
    title: str
    description: str

class ToDoResponse(BaseModel):
    id:int
    title:str
    description:str
    user_id:int
    
    class Config:
        from_attributes = True
