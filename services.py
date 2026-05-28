import pymysql
from pymysql.cursors import DictCursor
import jwt
from fastapi import HTTPException,status,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime,timezone, timedelta

SECRET_KEY = "paste-your-secret-key-change-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hasher = PasswordHasher()
authentication_method = HTTPBearer()

DB_CONFIG = {
    "host" : "localhost",
    "user" : "root",
    "password":"mypassword", #change accordingly
    "database":"todoorm",
    "cursorclass":DictCursor
}

def get_connection():
    connection = pymysql.connect(**DB_CONFIG)
    return connection


def hash_password(password:str):
    return password_hasher.hash(password)

def verify_password(plain_password:str,hashed_password:str):
    try:
        return password_hasher.verify(hashed_password,plain_password)
    except VerifyMismatchError:
        return False
    
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp":expire})
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(authentication_method)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, username, email FROM users WHERE id=%s",
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if not user:
        raise credentials_exception
    return user
