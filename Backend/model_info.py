from semantic_router import Route

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
        'what is scalar quantity',


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


# The Model Pool for LLMs.
GROQ_MODELS = {
    
    'llama-3.1-8b-instant': {
        'rpm_limit': 30,
        'rpd_limit': 14_400,
        'tpm_limit': 6_000,
        'tpd_limit': 500_000,
        'quality': 4,
        'tier': 'fast',
        'params': '8B',
    },
    'meta-llama/llama-4-scout-17b-16e-instruct': {
        'rpm_limit': 30,
        'rpd_limit': 1_000,
        'tpm_limit': 30_000,
        'tpd_limit': 500_000,
        'quality': 6,
        'tier': 'fast',
        'params': '17B',
    },
    'llama-3.3-70b-versatile': {
        'rpm_limit': 30,
        'rpd_limit': 1_000,
        'tpm_limit': 12_000,
        'tpd_limit': 100_000,
        'quality': 8,
        'tier': 'complex',
        'params': '70B',
    },
    'moonshotai/kimi-k2-instruct-0905': {
        'rpm_limit': 60,
        'rpd_limit': 1_000,
        'tpm_limit': 12_000,
        'tpd_limit': 100_000,
        'quality': 8,
        'tier': 'complex',
        'params': 'Unknown',
    },
    'openai/gpt-oss-120b': {
        'rpm_limit': 30,
        'rpd_limit': 1_000,
        'tpm_limit': 12_000,
        'tpd_limit': 100_000,
        'quality': 9,
        'tier': 'reasoning',
        'params': '120B',
    },
    'openai/gpt-oss-20b': {
        'rpm_limit': 30,
        'rpd_limit': 1_000,
        'tpm_limit': 12_000,
        'tpd_limit': 100_000,
        'quality': 6,
        'tier': 'complex',
        'params': '20B',
    },
}

# Pool definitions
POOLS = {
    'fast': ['llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct'],
    'complex': ['llama-3.3-70b-versatile', 'moonshotai/kimi-k2-instruct-0905', 'openai/gpt-oss-20b'],
    'reasoning': ['openai/gpt-oss-120b', 'moonshotai/kimi-k2-instruct-0905', 'llama-3.3-70b-versatile'],
}

# Failsafe cascade
FAILSAFE_CHAIN = {
    'fast': ['fast', 'complex', 'reasoning'],
    'complex': ['complex', 'reasoning', 'fast'],
    'reasoning': ['reasoning', 'complex', 'fast'],
}
