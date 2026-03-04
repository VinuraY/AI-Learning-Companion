# This section of code handles the backend operations for an AI Learning Companion application.
import json
import os
import re
import requests
import logging
from dotenv import load_dotenv
import fastapi
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.jinaai import JinaEmbedding
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.llms.groq import Groq
import user_manager
import load_balancer
from prompts import context_prompt, condense_prompt

# Configure logging.
logger = logging.getLogger(__name__)

# Load environment variables from .env file.
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
JINA_API_KEY = os.getenv('JINA_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
INDEX_NAME = 'ai-learning-companion-1024'

app = fastapi.FastAPI()

# Whitelist of allowed origins.
origins = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:5173',
]

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


################################
#    Authentication Section    #
################################

# Endpoint for Google OAuth2 authentication.
@app.post('/auth/google')
async def google_auth(request: GoogleAuthRequest, response: fastapi.Response):

    try:

        # Verify the token with Google's OAuth2 and extract user info.
        user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'

        user_info_response = requests.get(user_info_url, headers={
            'Authorization': f'Bearer {request.token}'
        })

        # Check if the request was successful.
        if user_info_response.status_code != 200:

            raise fastapi.HTTPException(
                status_code=401, detail='Failed to retrieve user info from Google')

        user_info = user_info_response.json()

        # Extract user info.
        user_id = user_info.get('sub')

        # Generate JWT token for the user.
        token = user_manager.generate_token(user_id)

        # Set the token as an Http-Only cookie.
        response.set_cookie(key='access_token', value=token,
                            httponly=True, secure=False, samesite='lax', max_age=86400)
        
        return {'status': 'success', 'user_id': user_id}

    except Exception as e:
        raise fastapi.HTTPException(
            status_code=401, detail=f'Invalid Google token : {str(e)}')


##########################
#    RAG Model Engine    #
##########################

# Startup event to initialize models and Pinecone client.
@app.on_event('startup')
async def startup_event():

    global index

    logging.info('[*] Initiating Backend Startup...')

    try:
        # Initialize Radis database.
        load_balancer.initialize()

        # Initialize Embedding Model.
        Settings.embed_model = JinaEmbedding(api_key=JINA_API_KEY)
        logging.info('[+] Jina embedding model initialized.')

        # Configure Global LlamaIndex Settings.
        Settings.context_window = 128000  # Large context for Groq models
        Settings.num_output = 4096  # Max tokens for response
        Settings.chunk_size = 512  # Reasonable chunk size
        Settings.chunk_overlap = 50

        # Initialize Pinecone Client.
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pinecone_client.Index(INDEX_NAME)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        logging.info('[+] Pinecone client created.')

        # Create index.
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, storage_context=storage_context)
        logging.info('[+] LlamaIndex vector store index created.')
        logging.info('[+] Backend Startup Completed.')

    except Exception as e:

        logging.error('[!] Backend Startup Failed.')
        raise fastapi.HTTPException(
            status_code=500, detail=f'Backend Initialization Failed : {str(e)}')


# Create chat engine for each user.
def chat_engine(user_id: str, model_name: str, filters=None):

    global index

    try:
        # Memory initialization for user.
        memory = user_manager.get_user_memory(user_id)

        # Set up LLM with selected model.
        llm = Groq(
            model=model_name,
            api_key=GROQ_API_KEY,
            temperature=0.7,
            max_tokens=4096
        )
        logging.info('[+] Groq LLM initialized.')

        # Initialize query engine with chat mode and memory.
        engine = index.as_chat_engine(
            llm=llm,
            chat_mode='condense_plus_context',  # type: ignore
            context_prompt=context_prompt,
            condense_prompt=condense_prompt,
            memory=memory,
            filters=filters,
            similarity_top_k=2,
        )

        logging.info('[+] Chat engine created.')
        return engine
    
    except Exception as e:

        logging.error('[!] Chat engine creation failed.')
        raise fastapi.HTTPException(
            status_code=500, detail=f'Backend Initialization Failed : {str(e)}')


######################
#    API Endpoint    #
######################

# Chat API endpoint.
@app.post('/chat', response_model=ChatResponse)
# user_id: str = fastapi.Depends(user_manager.verify_token)
async def chat_endpoint(request: ChatRequest, user_id: str = fastapi.Depends(user_manager.verify_token)):

    try:

        # Check user rate limits.
        logging.info('[*] Check user rate limits...')
        user_manager.check_user_limit(user_id)

        # Initialize the guard-rail check.
        if load_balancer.guard_rail_model(request.message) != 'safe':

            logging.error('[!] Guard rail check failed.')
            raise fastapi.HTTPException(
                status_code=403, detail='Request blocked by guard-rail policy.')

        # Select best available LLM model.
        model_name = load_balancer.get_best_model(request.message)
        logging.info(f'[+] Model selected : {model_name}')
        # model_name = 'gemini-2.0-flash-lite'

        # Check for page-specific queries.
        page_match = re.search(r"page\s+(\d+)", request.message.lower())

        filters = None

        if page_match:

            page_num = page_match.group(1)

            # Create a hard metadata filter to restrict search to the specified page.
            filters = MetadataFilters(
                filters=[ExactMatchFilter(
                    key='page_label', value=str(page_num))]
            )

        # Create a chat engine with the selected LLM. Use similarity_top_k=3 to fetch top 3 relevant documents. Filters force page-specific search if applicable.
        logging.info('[*] Preparing chat engine...')
        engine = chat_engine(user_id, model_name, filters)

        # Execute the RAG query.
        stream_response = await engine.astream_chat(request.message)
        logging.info('[*] RAG query initiated, streaming started...')

        # Create yielding generator for streaming response.
        async def response_generator():

            async for chunk in stream_response.async_response_gen():
                data = {'response': chunk, 'is_final': False}
                yield json.dumps(data) + '\n'

            meta_data = {
                'response': '',
                'model_used': model_name,
                'credits_remaining': 10 - len(user_manager.user_usage[user_id]),
                'is_final': True
            }
            yield json.dumps(meta_data) + '\n'
        
        logging.info('[+] Response generator created, returning StreamingResponse.')

        # Return streaming response.
        return StreamingResponse(response_generator(), media_type='application/x-ndjson')

    except Exception as e:

        logging.error('[!] Processing Failed.')
        raise fastapi.HTTPException(
            status_code=500, detail=f'AI Processing Failed: {str(e)}')
