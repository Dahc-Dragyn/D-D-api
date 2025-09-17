import os
import pickle
import faiss
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import logging

# --- LangChain Imports (Needed for unpickling) ---
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
# Add any other LangChain classes potentially pickled if necessary

# --- Configuration ---
FAISS_DIR = "faiss_index"
INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
PKL_PATH = os.path.join(FAISS_DIR, "index.pkl")
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
DEVICE = 'cpu'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global Variables (Load models/data at startup) ---
try:
    logger.info(f"Loading Sentence Transformer model: {MODEL_NAME}")
    embedding_model = SentenceTransformer(MODEL_NAME, device=DEVICE)
    logger.info("Model loaded successfully.")

    logger.info(f"Loading Faiss index from: {INDEX_PATH}")
    faiss_index = faiss.read_index(INDEX_PATH)
    logger.info("Faiss index loaded successfully.")

    logger.info(f"Loading Docstore and ID map from: {PKL_PATH}")
    with open(PKL_PATH, 'rb') as f:
        # Load the tuple: (docstore, index_to_docstore_id)
        docstore, index_to_docstore_id = pickle.load(f)
    logger.info("Docstore and ID map loaded successfully.")

    # Validate loaded types (optional but good practice)
    if not isinstance(docstore, InMemoryDocstore):
         logger.warning(f"Loaded object is not an InMemoryDocstore: {type(docstore)}")
    if not isinstance(index_to_docstore_id, dict):
         logger.warning(f"Loaded object is not a dict: {type(index_to_docstore_id)}")

    # Log info about the loaded docstore
    docstore_size = len(getattr(docstore, '_dict', {}))
    logger.info(f"Docstore contains {docstore_size} documents.")
    if faiss_index.ntotal != docstore_size:
         logger.warning(f"Faiss index size ({index.ntotal}) does not match Docstore size ({docstore_size})!")


except FileNotFoundError as e:
    logger.error(f"Error loading resources: {e}. Make sure '{FAISS_DIR}' exists and contains '{os.path.basename(INDEX_PATH)}' and '{os.path.basename(PKL_PATH)}'.")
    raise SystemExit(f"Could not load required files: {e}")
except ModuleNotFoundError as e:
     logger.error(f"Missing necessary library for unpickling: {e}. Did you install langchain-core and langchain-community?")
     raise SystemExit(f"Initialization failed due to missing module: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred during initialization: {e}", exc_info=True)
    raise SystemExit(f"Initialization failed: {e}")

# --- FastAPI App ---
app = FastAPI(
    title="D&D Knowledge Base API",
    description="API to query a Faiss index containing D&D information.",
    version="0.1.0"
)

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    query: str = Field(..., examples=["Show me the stats for an Owlbear"])
    top_k: int = Field(5, gt=0, le=20, description="Number of results to return")

class QueryResponseItem(BaseModel):
    page_content: str = Field(description="The formatted text chunk that was embedded.")
    metadata: dict = Field(description="Source document metadata, may include original JSON data.")
    score: float = Field(description="Similarity score (distance from query). Lower is more similar.")

class QueryResponse(BaseModel):
    results: list[QueryResponseItem]

# --- API Endpoint ---
@app.post("/query", response_model=QueryResponse)
async def search_index(request: QueryRequest):
    """
    Accepts a natural language query and returns the top_k relevant text chunks
    and their metadata from the D&D knowledge base.
    """
    logger.info(f"Received query: '{request.query}', top_k={request.top_k}")

    if not docstore or not faiss_index:
         raise HTTPException(status_code=503, detail="Knowledge base not loaded.")

    try:
        # 1. Embed the query
        query_embedding = embedding_model.encode([request.query], convert_to_tensor=False, device=DEVICE, normalize_embeddings=True)
        query_embedding = query_embedding.astype('float32') # Ensure float32

        # 2. Search Faiss index
        distances, indices = faiss_index.search(query_embedding, request.top_k)

        # 3. Retrieve content using indices from the mapping
        results = []
        if len(indices[0]) > 0:
            for i, idx in enumerate(indices[0]):
                if idx != -1: # Faiss might return -1
                    doc_id = str(idx) # The docstore uses string IDs '0', '1', ...
                    try:
                        # Retrieve the LangChain Document object
                        document = docstore.search(doc_id)

                        if document:
                            results.append(QueryResponseItem(
                                page_content=document.page_content,
                                metadata=document.metadata,
                                score=float(distances[0][i])
                            ))
                        else:
                            logger.warning(f"Document with ID '{doc_id}' (Faiss index {idx}) not found in Docstore.")

                    except Exception as e:
                        # Catch potential errors during docstore search or data extraction
                        logger.error(f"Error retrieving/processing document for index {idx} (ID '{doc_id}'): {e}", exc_info=True)

        logger.info(f"Returning {len(results)} results.")
        return QueryResponse(results=results)

    except Exception as e:
        logger.error(f"Error processing query '{request.query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while processing the query.")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    # Could add checks here to ensure models/index are loaded
    if docstore and faiss_index and embedding_model:
         return {"status": "ok", "index_size": faiss_index.ntotal}
    else:
         return {"status": "error", "detail": "Resources not loaded"}