from dotenv import load_dotenv
import os
import fastapi
import jwt
import datetime
import time
from llama_index.core.memory import ChatMemoryBuffer

# Load environment variables from .env file.
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

app = fastapi.FastAPI()

# Store memory for each user.
user_memory = {}

# Function to get or create user memory buffer.
def get_user_memory(user_id):

    if user_id not in user_memory:
        user_memory[user_id] = ChatMemoryBuffer.from_defaults(token_limit=3000)
    
    return user_memory[user_id]

# Generate JWT token for authenticated users.
def generate_token(user_id, role='student'):

    ACCESS_TOKEN_EXPIRE_HOURS = 24

    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    payload = {
        'subject': user_id,
        'role': role,
        'expire': expire
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256") # type: ignore
    return token

# In-memory store for user usage timestamps.
user_usage = {}


# Check user LLM usage limits. A user gets 10 requests per minute.
def check_user_limit(user_id):

    current_time = time.time()

    # Clean up old timestamps (older than 60s).
    user_usage[user_id] = [t for t in user_usage.get(
        user_id, []) if current_time - t < 60]

    if len(user_usage[user_id]) >= 10:
        raise fastapi.HTTPException(
            status_code=429, detail='Hitting rate limit! Max 10 requests per minute.')

    user_usage[user_id].append(current_time)


# Verify user JWT token.
def verify_token(access_token: str = fastapi.Cookie(None)):

    if not access_token:
        raise fastapi.HTTPException(
            status_code=401, detail='Not authenticated')

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256']) # type: ignore
        return payload['subject']

    except jwt.ExpiredSignatureError:
        raise fastapi.HTTPException(status_code=401, detail='Token expired')

    except jwt.InvalidTokenError:
        raise fastapi.HTTPException(status_code=401, detail='Invalid token')
