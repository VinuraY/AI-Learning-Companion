# This section of code handles the backend operations for an AI Learning Companion application.
import os
import re
from dotenv import load_dotenv
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.llms.groq import Groq
from google.oauth2 import id_token
from google.auth.transport import requests
import user_manager
import load_balancer


# Load environment variables from .env file.
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
INDEX_NAME = 'ai-learning-companion'

app = fastapi.FastAPI()

# Whitelist of allowed origins.
origins = [
    'http://localhost:3000',
    'http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],  # Allow all HTTP methods (GET, POST etc.)
    allow_headers=['*']  # Allow authorization headers.
)

# Filter classes for request validation.
class GoogleAuthRequest(BaseModel):
    token: str


class ChatResponse(BaseModel):
    response: str
    model_used: str
    credits_remaining: int

class ChatRequest(BaseModel):
    message: str


# Endpoint for Google OAuth2 authentication.
@app.post("/auth/google")
async def google_auth(request: GoogleAuthRequest, response: fastapi.Response):

    try:

        # Verify the token with Google's OAuth2.
        id_info = id_token.verify_oauth2_token(
            request.token, requests.Request(), GOOGLE_CLIENT_ID)

        # Extract user info.
        user_id = id_info['email'].split('@')[0]

        # Generate JWT token for the user.
        token = user_manager.generate_token(user_id)

        # Set the token as an Http-Only cookie.
        response.set_cookie(key='access_token', value=token,
                            httponly=True, secure=True, samesite='lax', max_age=86400)

        return {'status': 'success', 'user_id': user_id}

    except ValueError:
        raise fastapi.HTTPException(
            status_code=401, detail='Invalid Google token')


##########################
#    RAG Model Engine    #
##########################

# Startup event to initialize models and Pinecone client.
@app.on_event('startup')
async def startup_event():

    global index

    try:
    # Initialize Embedding Model.
        Settings.embed_model = HuggingFaceEmbedding(
            model_name='intfloat/multilingual-e5-small',
            device='cpu')

        # Initialize Pinecone Client.
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pinecone_client.Index(INDEX_NAME)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

        # Create index.
        storage_context = StorageContext.from_defaults(vector_store=vector_store)   
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
    
    except Exception as e:

        raise fastapi.HTTPException(
            status_code=500, detail=f'Backend Initialization Failed: {str(e)}')


# Create chat engine for each user.
def chat_engine(user_id: str, model_name: str, filters=None):
    
    global index

    # Memory initialization for user.
    memory = user_manager.get_user_memory(user_id)

    # Set up LLM with selected model.
    llm = Groq(model=model_name, api_key=GROQ_API_KEY)

    # Initialize query engine with chat mode and memory.
    return index.as_chat_engine(
        llm=llm,
        chat_mode='condense_plus_context', # type: ignore
        memory=memory,
        filters=filters,
        similarity_top_k=3
    )

@app.post('/chat', response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user_id: str = fastapi.Depends(user_manager.verify_token)): # user_id: str = fastapi.Depends(user_manager.verify_token)


    try:

        # Check user rate limits.
        user_manager.check_user_limit(user_id)

        # Initialize guard-rail check.
        if load_balancer.guard_rail_model(request.message) == 'safe':

            # Select best available LLM model.
            model_name = load_balancer.get_best_model(request.message)

            # Check for page-specific queries.
            page_match = re.search(r"page\s+(\d+)", request.message.lower())

            filters = None

            if page_match:

                page_num = page_match.group(1)

                # Create a hard metadata filter to restrict search to the specified page.
                filters = MetadataFilters(
                    filters=[ExactMatchFilter(key='page_label', value=str(page_num))]
                )

            # Create a chat engine with the selected LLM. Use similarity_top_k=3 to fetch top 3 relevant documents. Filters force page-specific search if applicable.
            engine = chat_engine(user_id, model_name, filters)
            response = engine.chat(request.message)

            # Execute the RAG query.
            response = engine.chat(request.message)

            return {
                'response': str(response),
                'model_used': model_name,
                'credits_remaining': 10 - len(user_manager.user_usage[user_id])
                }

        else:

            raise fastapi.HTTPException(
                status_code=403, detail='Request blocked by guard-rail policy.')
    
    except Exception as e:

        raise fastapi.HTTPException(
            status_code=500, detail=f'AI Processing Failed: {str(e)}')

if __name__ == '__main__':

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
