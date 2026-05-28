from fastapi import FastAPI,Depends,HTTPException
from schemas import ( 
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    ToDoUpdate,
    ToDoCreate,
    ToDoResponse)

from services import(
      get_connection,
    hash_password,
    verify_password,
    create_access_token,
    authentication_method,
    password_hasher,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    DB_CONFIG,
    get_current_user
)


app = FastAPI()

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE email=%s",
        (user.email,)
    )
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    cursor.execute(
        """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """,
        (user.username, user.email, hashed_pw)
    )
    connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return {
        "id": user_id,
        "username": user.username,
        "email": user.email
    }

@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (user.email,)
    )
    db_user = cursor.fetchone()
    cursor.close()
    connection.close()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        {
            "sub": str(db_user["id"])
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/todos", response_model=ToDoResponse)
def create_todo(
    todo: ToDoCreate,
    current_user=Depends(get_current_user)
):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO todos (title, description, user_id)
        VALUES (%s, %s, %s)
        """,
        (todo.title, todo.description, current_user["id"])
    )
    connection.commit()
    todo_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "user_id": current_user["id"]
    }

@app.get("/todos", response_model=list[ToDoResponse])
def get_todos(current_user=Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM todos WHERE user_id=%s",
        (current_user["id"],)
    )
    todos = cursor.fetchall()
    cursor.close()
    connection.close()
    return todos

@app.get("/todos/{todo_id}", response_model=ToDoResponse)
def get_todo(todo_id: int, current_user=Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM todos
        WHERE id=%s AND user_id=%s
        """,
        (todo_id, current_user["id"])
    )
    todo = cursor.fetchone()
    cursor.close()
    connection.close()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}")
def update_todo(
    todo_id: int,
    todo: ToDoUpdate,
    current_user=Depends(get_current_user)
):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE todos
        SET title=%s, description=%s
        WHERE id=%s AND user_id=%s
        """,
        (todo.title, todo.description, todo_id, current_user["id"])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Todo updated successfully"}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, current_user=Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM todos WHERE id=%s AND user_id=%s",
        (todo_id, current_user["id"])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Todo deleted successfully"}