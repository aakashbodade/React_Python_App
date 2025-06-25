import json
import boto3
from botocore.exceptions import ClientError
import psycopg2
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import bcrypt
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class SecretsManager:
    """
    Centralized secrets management class
    """
    def __init__(self, region_name="ap-south-1"):
        self.region_name = region_name
        self.client = boto3.client('secretsmanager', region_name=region_name)
        self._cache = {}

    def get_secret(self, secret_name, force_refresh=False):
        """
        Get secret with caching support
        """
        if secret_name in self._cache and not force_refresh:
            return self._cache[secret_name]

        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            
            # Try to parse as JSON, fall back to plain text
            try:
                secret = json.loads(secret_value)
            except json.JSONDecodeError:
                secret = secret_value
            
            # Cache the result
            self._cache[secret_name] = secret
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret
            
        except ClientError as e:
            logger.error(f"Error retrieving secret {secret_name}: {e}")
            raise e

    def get_database_credentials(self, secret_name="aws/keys"):
        """
        Get database credentials from AWS Secrets Manager
        """
        try:
            secret = self.get_secret(secret_name)
            
            # Handle both RDS auto-generated secrets and custom secrets
            credentials = {
            'host': secret.get('host'),
            'database': secret.get('database'),
            'user': secret.get('username'),
            'password': secret.get('password'),
            'port': secret.get('port', '5432')
            }
            
            # Validate required fields
            required_fields = ['host', 'user', 'password']
            missing_fields = [field for field in required_fields if not credentials[field]]
            
            if missing_fields:
                raise ValueError(f"Missing required database fields in secret: {missing_fields}")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get database credentials from secret: {e}")
            raise e

# Initialize secrets manager
secrets_manager = SecretsManager()

def get_database_config():
    """
    Get database configuration from AWS Secrets Manager only
    """
    try:
        # Get configuration from AWS Secrets Manager
        db_config = secrets_manager.get_database_credentials()
        logger.info("Using database configuration from AWS Secrets Manager")
        return db_config
        
    except Exception as e:
        logger.error(f"Failed to load credentials from AWS Secrets Manager: {e}")
        raise ValueError("Database credentials must be configured in AWS Secrets Manager")

# Get database configuration
try:
    DB_CONFIG = get_database_config()
except Exception as e:
    logger.error(f"Failed to initialize database configuration: {e}")
    raise e

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """
    Create and return a database connection using the configured credentials
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

# Pydantic models
class SigninData(BaseModel):
    username: str
    password: str

class SigninResponse(BaseModel):
    message: str
    user_id: int
    username: str

class SecretTestResponse(BaseModel):
    message: str
    secret_name: str
    has_credentials: bool

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "FastAPI Authentication Service",
        "database_configured": bool(DB_CONFIG)
    }

@app.get("/test-secret", response_model=SecretTestResponse)
def test_secret():
    """
    Test endpoint to verify secret retrieval (without exposing sensitive data)
    """
    try:
        # Test getting the secret (this will use cache if already retrieved)
        secret = secrets_manager.get_secret("aws/keys")
        
        return SecretTestResponse(
            message="Secret retrieved successfully",
            secret_name="aws/keys",
            has_credentials=bool(secret.get('username') and secret.get('password'))
        )
        
    except Exception as e:
        logger.error(f"Error testing secret retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve secret"
        )

@app.post("/signin", response_model=SigninResponse)
def signin(user: SigninData):
    """
    Authenticate user with username and password
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

        # Connect to PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if the user exists
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s", 
            (user.username,)
        )
        db_user = cursor.fetchone()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Verify password
        if not bcrypt.verify(user.password, db_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        logger.info(f"User {user.username} signed in successfully")
        
        return SigninResponse(
            message="Sign-in successful!",
            user_id=db_user["id"],
            username=db_user["username"]
        )

    except HTTPException:
        raise
    except psycopg2.Error as e:
        logger.error(f"Database error during signin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error during signin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.post("/refresh-secrets")
def refresh_secrets():
    """
    Endpoint to refresh cached secrets (useful for secret rotation)
    """
    try:
        # Clear cache and reload database config
        secrets_manager._cache.clear()
        global DB_CONFIG
        DB_CONFIG = get_database_config()
        
        return {"message": "Secrets refreshed successfully"}
        
    except Exception as e:
        logger.error(f"Error refreshing secrets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh secrets"
        )

# Remove Lambda handler - this is now a standalone FastAPI app