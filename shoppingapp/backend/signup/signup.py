import json
import boto3
from botocore.exceptions import ClientError
import psycopg2
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import bcrypt
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_database_credentials():
    """
    Retrieve database credentials from AWS Secrets Manager
    """
    secret_name = "aws/keys"  # Change this to your secret name
    region_name = "ap-south-1"

    # Create a Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response['SecretString'])
        
        # Extract and return database credentials
        return {
            'host': secret.get('host'),
            'database': secret.get('database'),
            'user': secret.get('username'),
            'password': secret.get('password'),
            'port': secret.get('port', '5432')
        }
        
    except ClientError as e:
        logger.error(f"Error retrieving secret: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve database credentials"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing secret JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid secret format"
        )

# Get database configuration
try:
    DB_CONFIG = get_database_credentials()
    logger.info("Database credentials loaded from AWS Secrets Manager")
except Exception as e:
    logger.error(f"Failed to load database credentials: {e}")
    raise e

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )

# Schema for signup data
class SignupData(BaseModel):
    username: str
    password: str

class SignupResponse(BaseModel):
    message: str
    username: str

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI Signup Service"}

@app.post("/signup", response_model=SignupResponse)
def signup(user: SignupData):
    """
    Register a new user
    """
    conn = None
    cursor = None
    
    try:
        # Validate input
        if not user.username or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )

        if len(user.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )

        if len(user.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )

        # Connect to PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Hash the password
        hashed_password = bcrypt.hash(user.password)

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (user.username, hashed_password),
        )
        conn.commit()

        logger.info(f"New user '{user.username}' registered successfully")
        
        return SignupResponse(
            message="User registered successfully!",
            username=user.username
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        if conn:
            conn.rollback()
        raise
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
    finally:
        # Ensure database resources are cleaned up
        if cursor:
            cursor.close()
        if conn:
            conn.close()