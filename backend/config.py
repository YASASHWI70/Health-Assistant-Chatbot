"""
config.py - Centralized configuration management for Healthcare Copilot
Loads settings from environment variables with sensible defaults.
"""

import os   #used to read environment variable
from pathlib import Path #used to handle file paths
from dotenv import load_dotenv #loads value from .env file

# Load .env file if present
load_dotenv()

# ─── Project Paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent #gets root folder of your project
DATA_DIR = BASE_DIR / "data" #folder where all your data (PDF's etc) is stored
KNOWLEDGE_DIR = DATA_DIR / "medical_knowledge" #folder where all your medical knowledge is stored
FAISS_INDEX_PATH = str(DATA_DIR / "faiss_index") #path to your faiss index, where vector base will be saved 
LOG_DIR = BASE_DIR / "logs" #folder where all your logs are stored
LOG_DIR.mkdir(exist_ok=True) #creates a folder if it doesn't exist

# ─── Ollama / LLM ─────────────────────────────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") # where ollama server runs
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b") # which model to use
OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text") # embedding model that is used, Converting text → embeddings (RAG), finds relevant data
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60")) # Max time (seconds) to wait for response

# ─── RAG Configuration ────────────────────────────────────────────────────────
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512")) # Split documents into chunks of 512 tokens
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "64")) # overlap between chunks, reason: Avoid losing context between chunks
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5")) # number of chunks to retrieve

# ─── Conversation Memory ──────────────────────────────────────────────────────
MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "10")) # Max number of past conversations to remember, rreason: Keeps conversation context, Prevents too long history (performance issue)

# ─── Backend Configuration ────────────────────────────────────────────────────
BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0") # IP address of the Server accessible from anywhere (local network)
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000")) # Port number of the server, FastAPI will run on: http://localhost:8000

# ─── Logging Configuration ────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO") # INFO, DEBUG, WARNING, ERROR, CRITICAL
LOG_FILE: str = os.getenv("LOG_FILE", str(LOG_DIR / "copilot.log")) # Path to the log file

# ─── Disclaimer ──────────────────────────────────────────────────────────────
MEDICAL_DISCLAIMER = (
    "⚠️ DISCLAIMER: This tool is for informational and educational purposes only."
    "It does NOT constitute medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare professional for medical concerns. "
    "In an emergency, call your local emergency services (911/112/999) immediately."
)