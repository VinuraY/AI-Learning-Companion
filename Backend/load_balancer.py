# This script ensures LLM availability using a load balancer.
from fastapi import HTTPException
import time
from groq import Groq
import os
from dotenv import load_dotenv
from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders.jina import JinaEncoder
from semantic_router.index.pinecone import PineconeIndex


# The Model Pool for LLMs.
GROQ_MODELS = [
    {'name': 'llama-3.3-70b-versatile', 'limit': 30, 'hits': 0},
    {'name': 'llama-3.1-8b-instant', 'limit': 30, 'hits': 0},
    {'name': 'moonshotai/kimi-k2-instruct-0905', 'limit': 60, 'hits': 0},
    {'name': 'openai/gpt-oss-120b', 'limit': 30, 'hits': 0},
    {'name': 'openai/gpt-oss-20b', 'limit': 30, 'hits': 0},
    {'name': 'qwen/qwen3-32b', 'limit': 60, 'hits': 0},
    {'name': 'meta-llama/llama-4-scout-17b-16e-instruct', 'limit': 30, 'hits': 0}
]

# Track last reset time for hit counts.
last_reset_time = time.time()


# Automatic LLM selection.
def auto_select_model(request):

    # Models that perform speed based selection.
    fast = Route(
        name='fast',
        utterances=[
            # Greetings
            'hi', 'hello', 'hey', 'good morning', 'yo', 'hows it going',

            # Basic Networking Terminology
            'what is an ip address',
            'define dns',
            'what is photosynthesis',
            'how many layers in the osi model',
            'what is subnetting',
            '3rd planet from the sun',
            'what is vector quantity',
            'what is scalar quantity'


            # Small Talk / Identity
            'tell me a joke', 'who are you', 'how are you', 'are you ai',
            'what is the weather', 'do you like rust', 'are you single',

            # Simple Logic (Fast Response)
            'what time is it', 'define a cat', '1+1', 'thank you',

            # General Help/Closing
            'help me with my homework',
            'thank you very much',
            'bye bye',
            'stop',
            'clear chat',

            # A/L Science Flashcards
            'value of g', 'atomic number of carbon', 'what is newton\'s first law',
            'speed of light value', 'formula for water', 'what is a prime number',
            'boiling point of water', 'refractive index of glass',

            # A/L Tech Flashcards
            'what is a multimeter', 'define a logic gate', 'standard paper sizes',
            'what is alternating current', 'parts of a lathe machine',
            'what does sft stand for in tech stream', 'binary to decimal conversion',

            # Navigation
            'clear chat', 'summarize this page', 'what book is this?'
        ]
    )

    complex = Route(
        name='complex',
        utterances=[
            # Subnetting & Design
            'calculate the subnets for 10.0.0.0/8',
            'design a secure network topology',
            'how to configure vlans on a cisco switch',

            # Troubleshooting
            'troubleshoot a connection timed out error',
            'why is my c2 framework not receiving heartbeats',
            'debug this code for me',

            # Deep Theory
            'explain memory safety in rust',
            'how does djkstra\'s algorithm work in ospf',
            'compare rag vs fine-tuning for student ai',
            'explain the math of embeddings',

            # Advanced Programming
            'write a python script for network automation',
            'refactor this code using oop principles',
            'explain the borrow checker in rust',

            # Combined Maths
            'solve the quadratic equation x^2 - 5x + 6', 'find the derivative of sin(x)',
            'how to calculate the z-score', 'explain the center of gravity',
            'calculate the area of a circle using integration', 'matrix multiplication',

            # Physics / Engineering Tech
            'bernoulli\'s principle explanation', 'calculate total resistance in parallel',
            'how does a four stroke engine work', 'explain pascal\'s law',
            'logic circuit for an xor gate', 'calculate the efficiency of a transformer',
            'how to measure torque', 'explain modulation in communication',

            # Chemistry / Bio Systems
            'how to balance a chemical equation', 'difference between mitosis and meiosis',
            'explain the periodic table groups', 'how does photosynthesis work',
            'organic chemistry naming rules', 'titration calculation steps'
        ]
    )

    reasoning = Route(
        name='reasoning',
        utterances=[
            # Common Reasoning Prompts
            'why', 'how', 'what if', 'reason', 'logic', 'cause',

            # Advanced Derivations (The 'A' Grade questions)
            'derive the formula for the time of flight of a projectile',
            'prove the cosine rule using vectors', 'mathematical proof of work-energy theorem',
            'derive the equation for a standing wave', 'prove the binomial theorem',

            # Deep Engineering / Tech Analysis
            'design a zero-trust network architecture for a school',
            'analyze this pcap file for a man-in-the-middle attack',
            'troubleshoot why this rust memory safety check is failing',
            'evaluate the trade-offs between OSPF and BGP for an ISP',
            'find the security vulnerability in this python listener',

            # Complex Academic Strategy
            'provide a deep analysis of last 5 years physics past papers',
            'evaluate my study plan for combined maths to get an A',
            'explain gödel\'s incompleteness theorem in simple terms']
    )

    # Load environment variables.
    load_dotenv()

    JINA_API_KEY = os.getenv('JINA_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

    # Initialize the encoder (Embedding model).
    # encoder = HuggingFaceEncoder(name='intfloat/multilingual-e5-small', device='cpu')
    encoder = JinaEncoder(api_key=JINA_API_KEY)

    # Initialize pinecone index.
    pinecone_index = PineconeIndex(
        index_name='ai-learning-router', api_key=PINECONE_API_KEY)

    routes = [fast, complex, reasoning]

    # Add all routes to the router (encoder).
    sementic_router = SemanticRouter(
        encoder=encoder, routes=routes, index=pinecone_index)

    # Get the best route based on the request.
    selector = sementic_router(request).name # type: ignore

    return selector


# Pick best model based on load balancing logic.
def get_best_model(request):

    global last_reset_time

    # Get model type based on request.
    model_type = auto_select_model(request)

    # Model classification based on semantic similarity.
    fast_models = [GROQ_MODELS[1], GROQ_MODELS[4]]
    complex_models = [GROQ_MODELS[0], GROQ_MODELS[2],
                      GROQ_MODELS[3], GROQ_MODELS[5], GROQ_MODELS[6]]
    reasoning_models = [GROQ_MODELS[2],GROQ_MODELS[3],GROQ_MODELS[4],GROQ_MODELS[5]]

    if model_type == 'fast':
        model = fast_models

    elif model_type == 'complex':
        model = complex_models

    elif model_type == 'reasoning':
        model = reasoning_models

    else:
        model = fast_models

    # Reset hit counts every 60 seconds.
    if time.time() - last_reset_time > 60:

        for i in model:
            i['hits'] = 0
            last_reset_time = time.time()
        print('reset time')

    # Sort models by available capacity.
    available_models = sorted(
        [m for m in model if m['hits'] < m['limit']],
        key=lambda x: (x['limit'] - x['hits']),
        reverse=True
    )

    if available_models:
        selected = available_models[0]
        selected['hits'] += 1
        return selected['name']

    else:
        raise HTTPException(
            status_code=503, detail='All AI models are currently at capacity. Please wait 10s.')

# Guard-rail LLM selection.
def guard_rail_model(request):

    load_dotenv()
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    guard_rail = Groq(api_key=GROQ_API_KEY)

    response = guard_rail.chat.completions.create(model='meta-llama/llama-guard-4-12b', messages=[
        {'role': 'user', 'content': request}, {'role': 'system', 'content': 'If user ask about metadata show unsafe'}])

    return response.choices[0].message.content
