from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.hash import bcrypt
from psycopg2 import sql, OperationalError
from fastapi.middleware.cors import CORSMiddleware
import os
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

# Schema for signup data
class SignupData(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(user: SignupData):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST, 
            database=DB_NAME, 
            user=DB_USER, 
            password=DB_PASSWORD,  
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash the password
        hashed_password = bcrypt.hash(user.password)

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (user.username, hashed_password),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create handler for AWS Lambda
handler = mangum.Mangum(app)