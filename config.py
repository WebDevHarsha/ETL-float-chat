import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai

# Load env
load_dotenv(".env.local")

POSTGRES_LINK = os.getenv("POSTGRES_LINK")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NC_FILE = "ocean.nc"

# DB
engine = create_engine(POSTGRES_LINK)

# Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_db")
meta_collection = chroma_client.get_or_create_collection(
    name="netcdf_metadata",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

# Gemini
genai.configure(api_key=GOOGLE_API_KEY)
gemini_client = genai
