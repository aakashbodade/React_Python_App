from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.hash import bcrypt
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import mangum

load_dotenv()

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration using environment variables for security
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT", "5432")

# Schema for signin data
class SigninData(BaseModel):
    username: str
    password: str

@app.post("/signin")
def signin(user: SigninData):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST, 
            database=DB_NAME, 
            user=DB_USER, 
            password=DB_PASSWORD,  
            port=DB_PORT
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

# Create handler for AWS Lambda
handler = mangum.Mangum(app)