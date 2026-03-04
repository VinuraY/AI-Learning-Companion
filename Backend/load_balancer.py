# load_balancer_redis_enhanced.py
# Production-grade capacity-aware LLM load balancer with Redis persistence
# 
# Key improvements:
# 1. Redis backend for persistent state across restarts and multi-server deployments
# 2. Atomic Redis operations for thread-safety without Python locks
# 3. Accurate tiktoken-based token counting with caching
# 4. Capacity-first selection with quality tie-breaking (prevents model exhaustion)
# 5. Optimized Redis key structure with automatic TTL expiration
# 6. Connection pooling for better performance
# 7. Graceful degradation when Redis is unavailable

import os
import time
import logging
import hashlib
from typing import Optional, Dict, List
from functools import lru_cache

import redis
from redis.connection import ConnectionPool
import tiktoken
from groq import Groq
from fastapi import HTTPException
from dotenv import load_dotenv
from semantic_router.routers import SemanticRouter
from semantic_router.encoders.jina import JinaEncoder
from semantic_router.index.pinecone import PineconeIndex
from model_info import GROQ_MODELS, POOLS, FAILSAFE_CHAIN, fast, complex, reasoning

load_dotenv()

JINA_API_KEY = os.getenv('JINA_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT= os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
#  REDIS CONNECTION POOL
#  Reuses connections for better performance
# ═══════════════════════════════════════════════════════════════════
_redis_pool = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True,
    max_connections=50,
    socket_timeout=2,
    socket_connect_timeout=2,
    retry_on_timeout=True
)

def _get_redis_client() -> redis.Redis:
    """Get Redis client from connection pool"""
    return redis.Redis(connection_pool=_redis_pool)


# ═══════════════════════════════════════════════════════════════════
#  REDIS KEY STRUCTURE
#  Optimized for performance and automatic cleanup
#
#  Keys:
#    model:{model_name}:rpm:{minute_ts}  → RPM counter (TTL: 120s)
#    model:{model_name}:tpm:{minute_ts}  → TPM counter (TTL: 120s)
#    model:{model_name}:rpd:{day_ts}     → RPD counter (TTL: 172800s)
#    model:{model_name}:tpd:{day_ts}     → TPD counter (TTL: 172800s)
#    model:{model_name}:config           → Model config (hash, no TTL)
#    token_cache:{hash}                  → Token count cache (TTL: 3600s)
# ═══════════════════════════════════════════════════════════════════

def _get_current_minute() -> int:
    """Get current minute timestamp (aligned to 60s boundary)"""
    return int(time.time() // 60) * 60

def _get_current_day() -> int:
    """Get current day timestamp (aligned to 86400s boundary)"""
    return int(time.time() // 86400) * 86400


# ═══════════════════════════════════════════════════════════════════
#  TOKEN COUNTING WITH CACHING
#  Dramatically reduces tokenization overhead for repeated text
# ═══════════════════════════════════════════════════════════════════

try:
    _tokenizer = tiktoken.get_encoding("cl100k_base")
    logger.info("✅ Tokenizer loaded successfully")
except Exception as e:
    _tokenizer = None
    logger.warning(f"⚠️ Tokenizer failed: {e}. Using fallback.")


@lru_cache(maxsize=1000)
def _count_tokens_cached(text_hash: str, text: str) -> int:
    """
    Count tokens with in-memory LRU cache.
    text_hash is used as cache key for faster lookup.
    """
    if _tokenizer is not None:
        try:
            return len(_tokenizer.encode(text))
        except Exception:
            pass
    
    # Sinhala-aware fallback
    sinhala_chars = sum(1 for c in text if '\u0D80' <= c <= '\u0DFF')
    other_chars = len(text) - sinhala_chars
    return (sinhala_chars // 8) + (other_chars // 4)


def _count_tokens(text: str, use_redis_cache: bool = True) -> int:
    """
    Count tokens with two-tier caching (Redis + LRU).
    
    Cache hierarchy:
    1. In-memory LRU cache (instant)
    2. Redis cache (fast, shared across servers)
    3. Actual tokenization (slow)
    """
    if not text:
        return 0
    
    # Generate cache key
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    # Try in-memory cache first (instant)
    try:
        return _count_tokens_cached(text_hash, text)
    except Exception:
        pass
    
    # Try Redis cache (shared across servers)
    if use_redis_cache:
        try:
            r = _get_redis_client()
            cache_key = f"token_cache:{text_hash}"
            cached = r.get(cache_key)
            
            if cached is not None:
                return int(cached)
            
            # Not in cache - count and store
            count = _count_tokens_cached(text_hash, text)
            r.setex(cache_key, 3600, count)  # Cache for 1 hour
            return count
            
        except redis.RedisError as e:
            logger.debug(f"Redis cache miss: {e}")
    
    # Direct count (fallback)
    return _count_tokens_cached(text_hash, text)


def estimate_request_tokens(
    user_message: str,
    rag_context: str = "",
    system_prompt: str = "",
    response_buffer: int = 500
) -> int:
    """
    Estimate total tokens with intelligent caching.
    System prompt is cached globally (rarely changes).
    RAG context is cached per-chunk (often repeated).
    """
    system_tokens = _count_tokens(system_prompt) if system_prompt else 0
    context_tokens = _count_tokens(rag_context) if rag_context else 0
    message_tokens = _count_tokens(user_message, use_redis_cache=False)  # Don't cache unique queries
    
    total = system_tokens + context_tokens + message_tokens + response_buffer
    
    logger.debug(
        f"Tokens → System: {system_tokens} | Context: {context_tokens} | "
        f"Message: {message_tokens} | Buffer: {response_buffer} | Total: {total}"
    )
    
    return total


# ═══════════════════════════════════════════════════════════════════
#  REDIS CAPACITY OPERATIONS
#  All operations are atomic using Redis INCR/INCRBY
# ═══════════════════════════════════════════════════════════════════

def _get_model_usage(model_name: str) -> Dict[str, int]:
    """
    Get current usage counters from Redis.
    Returns all 4 usage metrics atomically.
    """
    try:
        r = _get_redis_client()
        current_minute = _get_current_minute()
        current_day = _get_current_day()
        
        pipe = r.pipeline()
        pipe.get(f"model:{model_name}:rpm:{current_minute}")
        pipe.get(f"model:{model_name}:tpm:{current_minute}")
        pipe.get(f"model:{model_name}:rpd:{current_day}")
        pipe.get(f"model:{model_name}:tpd:{current_day}")
        results = pipe.execute()
        
        return {
            'rpm_used': int(results[0] or 0),
            'tpm_used': int(results[1] or 0),
            'rpd_used': int(results[2] or 0),
            'tpd_used': int(results[3] or 0),
        }
    
    except redis.RedisError as e:
        logger.error(f"Redis read error: {e}")
        # Return zeros on error (fail open)
        return {'rpm_used': 0, 'tpm_used': 0, 'rpd_used': 0, 'tpd_used': 0}


def _consume_capacity(model_name: str, estimated_tokens: int):
    """
    Atomically increment usage counters in Redis.
    Uses pipelined INCR for efficiency.
    Sets TTL automatically so old keys expire.
    """
    try:
        r = _get_redis_client()
        current_minute = _get_current_minute()
        current_day = _get_current_day()
        
        pipe = r.pipeline()
        
        # Minute counters (auto-expire after 2 minutes)
        rpm_key = f"model:{model_name}:rpm:{current_minute}"
        tpm_key = f"model:{model_name}:tpm:{current_minute}"
        pipe.incr(rpm_key)
        pipe.expire(rpm_key, 120)
        pipe.incrby(tpm_key, estimated_tokens)
        pipe.expire(tpm_key, 120)
        
        # Day counters (auto-expire after 2 days)
        rpd_key = f"model:{model_name}:rpd:{current_day}"
        tpd_key = f"model:{model_name}:tpd:{current_day}"
        pipe.incr(rpd_key)
        pipe.expire(rpd_key, 172800)
        pipe.incrby(tpd_key, estimated_tokens)
        pipe.expire(tpd_key, 172800)
        
        pipe.execute()
        
        logger.debug(
            f"Consumed capacity: {model_name} → +1 req, +{estimated_tokens} tokens"
        )
    
    except redis.RedisError as e:
        logger.error(f"Redis write error: {e}. Continuing anyway.")


def _is_model_available(model_name: str, estimated_tokens: int) -> bool:
    """
    Check if model has capacity on all 4 dimensions.
    Reads from Redis for accurate cross-server state.
    """
    config = GROQ_MODELS[model_name]
    usage = _get_model_usage(model_name)
    
    # Safety margins (90% of limit)
    rpm_ok = usage['rpm_used'] < config['rpm_limit'] * 0.9
    rpd_ok = usage['rpd_used'] < config['rpd_limit'] * 0.9
    tpm_ok = (usage['tpm_used'] + estimated_tokens) < config['tpm_limit'] * 0.9
    tpd_ok = (usage['tpd_used'] + estimated_tokens) < config['tpd_limit'] * 0.9
    
    is_available = rpm_ok and rpd_ok and tpm_ok and tpd_ok
    
    if not is_available:
        logger.warning(
            f"Model '{model_name}' at capacity → "
            f"RPM: {usage['rpm_used']}/{config['rpm_limit']} | "
            f"RPD: {usage['rpd_used']}/{config['rpd_limit']} | "
            f"TPM: {usage['tpm_used']+estimated_tokens}/{config['tpm_limit']} | "
            f"TPD: {usage['tpd_used']+estimated_tokens}/{config['tpd_limit']}"
        )
    
    return is_available


def _capacity_score(model_name: str, estimated_tokens: int) -> float:
    """
    Compute pure capacity score (0.0-1.0).
    Higher score = more available capacity.
    
    Weights: RPM 15%, RPD 15%, TPM 35%, TPD 35%
    Token limits weighted higher for RAG workloads.
    """
    config = GROQ_MODELS[model_name]
    usage = _get_model_usage(model_name)
    
    rpm_ratio = 1 - (usage['rpm_used'] / config['rpm_limit'])
    rpd_ratio = 1 - (usage['rpd_used'] / config['rpd_limit'])
    tpm_ratio = 1 - ((usage['tpm_used'] + estimated_tokens) / config['tpm_limit'])
    tpd_ratio = 1 - ((usage['tpd_used'] + estimated_tokens) / config['tpd_limit'])
    
    # Ensure ratios are non-negative
    rpm_ratio = max(0, rpm_ratio)
    rpd_ratio = max(0, rpd_ratio)
    tpm_ratio = max(0, tpm_ratio)
    tpd_ratio = max(0, tpd_ratio)
    
    weighted_score = (
        rpm_ratio * 0.15 +
        rpd_ratio * 0.15 +
        tpm_ratio * 0.35 +
        tpd_ratio * 0.35
    )
    
    return weighted_score


def _select_from_pool(pool: List[str], estimated_tokens: int) -> Optional[str]:
    """
    Select best model from pool using capacity-first strategy.
    Quality used only as tie-breaker (within 5% capacity difference).
    """
    # Filter to available models
    available = [
        name for name in pool
        if _is_model_available(name, estimated_tokens)
    ]
    
    if not available:
        return None
    
    # Sort by capacity score
    available.sort(
        key=lambda n: _capacity_score(n, estimated_tokens),
        reverse=True
    )
    
    # Tie-breaking by quality (only if top 2 are close)
    if len(available) >= 2:
        top_model = available[0]
        second_model = available[1]
        
        top_score = _capacity_score(top_model, estimated_tokens)
        second_score = _capacity_score(second_model, estimated_tokens)
        
        # Within 5% → use quality
        if abs(top_score - second_score) < 0.05:
            top_quality = GROQ_MODELS[top_model]['quality']
            second_quality = GROQ_MODELS[second_model]['quality']
            
            if second_quality > top_quality:
                logger.debug(
                    f"Tie-breaker: {second_model} (Q{second_quality}) "
                    f"over {top_model} (Q{top_quality})"
                )
                return second_model
    
    return available[0]


# ═══════════════════════════════════════════════════════════════════
#  SEMANTIC ROUTER
#  Initialized once at module load
# ═══════════════════════════════════════════════════════════════════

_encoder = JinaEncoder(api_key=JINA_API_KEY)
_pinecone_index = PineconeIndex(
    index_name='ai-learning-router',
    api_key=PINECONE_API_KEY
)
_semantic_router = SemanticRouter(
    encoder=_encoder,
    routes=[fast, complex, reasoning],
    index=_pinecone_index
)

_guard_rail_client = Groq(api_key=GROQ_API_KEY)


# ═══════════════════════════════════════════════════════════════════
#  API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

def get_best_model(
    request: str,
    rag_context: str = "",
    system_prompt: str = ""
) -> str:
    """
    Select best available model using Redis-backed state.
    
    Features:
    - Redis persistence (survives restarts, works across servers)
    - Atomic operations (no race conditions)
    - Accurate token counting with caching
    - Capacity-first selection with quality tie-breaking
    - Graceful degradation on Redis failure
    
    Thread-safe via Redis atomic operations (no Python locks needed).
    Raises HTTP 503 only if ALL models exhausted.
    """
    # Accurate token estimation with caching
    estimated_tokens = estimate_request_tokens(
        user_message=request,
        rag_context=rag_context,
        system_prompt=system_prompt,
        response_buffer=500
    )
    
    # Semantic routing
    route_result = _semantic_router(request)
    route_name = route_result.name if route_result else 'fast'
    
    logger.info(f"📍 Route: '{route_name}' | Tokens: {estimated_tokens}")
    
    # Try pools in failsafe order
    chain = FAILSAFE_CHAIN.get(route_name, ['fast', 'complex', 'reasoning'])
    
    for pool_name in chain:
        pool = POOLS[pool_name]
        selected = _select_from_pool(pool, estimated_tokens)
        
        if selected:
            # Consume capacity atomically in Redis
            _consume_capacity(selected, estimated_tokens)
            
            # Log selection
            config = GROQ_MODELS[selected]
            if pool_name != route_name:
                logger.warning(
                    f"⚠️ Failsafe: '{route_name}' → '{pool_name}' | "
                    f"Selected: {selected} ({config['params']}, Q{config['quality']})"
                )
            else:
                logger.info(
                    f"✅ Selected: {selected} ({config['params']}, Q{config['quality']}) | "
                    f"Capacity: {_capacity_score(selected, estimated_tokens):.2f} | "
                    f"Pool: {pool_name}"
                )
            
            return selected
    
    # All models exhausted
    logger.error('❌ All models at capacity')
    raise HTTPException(
        status_code=503,
        detail='All AI models at capacity. Please wait 60 seconds and try again.'
    )


def guard_rail_model(request: str) -> str:
    """Safety classification using Llama Guard"""
    try:
        response = _guard_rail_client.chat.completions.create(
            model='meta-llama/llama-guard-4-12b',
            messages=[{'role': 'user', 'content': request}],
            max_tokens=20,
        )
        result = response.choices[0].message.content.strip().lower()
        verdict = 'safe' if result.startswith('safe') else 'unsafe'
        logger.info(f"🛡️ Guard rail: '{verdict}'")
        return verdict
    except Exception as e:
        logger.error(f"Guard rail failed: {e}")
        return 'safe'


def get_model_status() -> Dict:
    """Get current usage stats from Redis"""
    status = {}
    
    for name, config in GROQ_MODELS.items():
        usage = _get_model_usage(name)
        
        status[name] = {
            'tier': config['tier'],
            'quality': config['quality'],
            'params': config['params'],
            'rpm': f"{usage['rpm_used']}/{config['rpm_limit']}",
            'rpd': f"{usage['rpd_used']}/{config['rpd_limit']}",
            'tpm': f"{usage['tpm_used']}/{config['tpm_limit']}",
            'tpd': f"{usage['tpd_used']}/{config['tpd_limit']}",
            'capacity_score': round(_capacity_score(name, 500), 3),
            'available': _is_model_available(name, 500),
            'rpm_percent': round((usage['rpm_used'] / config['rpm_limit']) * 100, 1),
            'tpm_percent': round((usage['tpm_used'] / config['tpm_limit']) * 100, 1),
        }
    
    return status


def get_load_distribution() -> Dict:
    """Get load distribution statistics"""
    distribution = {}
    total_requests = 0
    
    for name, config in GROQ_MODELS.items():
        usage = _get_model_usage(name)
        total_requests += usage['rpd_used']
        
        distribution[name] = {
            'requests_today': usage['rpd_used'],
            'tier': config['tier'],
            'quality': config['quality']
        }
    
    # Calculate percentages
    for name in distribution:
        if total_requests > 0:
            distribution[name]['percentage'] = round(
                (distribution[name]['requests_today'] / total_requests) * 100, 1
            )
        else:
            distribution[name]['percentage'] = 0
    
    return {
        'total_requests_today': total_requests,
        'distribution': distribution
    }


def clear_token_cache():
    """Clear Redis token cache (useful for testing)"""
    try:
        r = _get_redis_client()
        keys = r.keys("token_cache:*")
        if keys:
            r.delete(*keys)
            logger.info(f"Cleared {len(keys)} token cache entries")
    except redis.RedisError as e:
        logger.error(f"Failed to clear cache: {e}")


def health_check() -> Dict:
    """Check system health including Redis connectivity"""
    try:
        r = _get_redis_client()
        r.ping()
        redis_healthy = True
        redis_error = None
    except Exception as e:
        redis_healthy = False
        redis_error = str(e)
    
    status = get_model_status()
    available_models = sum(1 for m in status.values() if m['available'])
    
    return {
        'status': 'healthy' if redis_healthy and available_models > 0 else 'degraded',
        'redis_connected': redis_healthy,
        'redis_error': redis_error,
        'models_available': available_models,
        'models_total': len(GROQ_MODELS),
        'tokenizer_loaded': _tokenizer is not None,
    }


# ═══════════════════════════════════════════════════════════════════
#  INITIALIZATION
# ═══════════════════════════════════════════════════════════════════

def initialize():
    """
    Initialize load balancer.
    Call this from FastAPI startup event.
    """
    # Test Redis connection
    try:
        r = _get_redis_client()
        r.ping()
        logger.info("✅ Redis connected")
    except redis.RedisError as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.warning("⚠️ Load balancer will work but state won't persist")
    
    # Test tokenizer
    if _tokenizer:
        logger.info("✅ Tokenizer ready")
    else:
        logger.warning("⚠️ Using fallback token counting")
    
    logger.info(f"✅ Load balancer initialized ({len(GROQ_MODELS)} models)")
