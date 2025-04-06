from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.hash import bcrypt

from psycopg2 import sql, OperationalError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_HOST = "host.docker.internal"
DB_NAME = "shoppingapp"
DB_USER = "aakash"
DB_PASSWORD = "Aakash1997"
DB_PORT = "5433" 

# Schema for signin data
class SigninData(BaseModel):
    username: str
    password: str

@app.post("/signin")
def signin(user: SigninData):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD,  port=DB_PORT
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if the user exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        db_user = cursor.fetchone()
        if not db_user or not bcrypt.verify(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        cursor.close()
        conn.close()

        return {"message": "Sign-in successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
