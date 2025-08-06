import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import time

from ..models.rag_system import RAGSystem
from ..config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="RAG System for Document Processing and Question Answering",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Initialize RAG system
rag_system = RAGSystem()

# Pydantic models
class QuestionRequest(BaseModel):
    documents: str
    questions: List[str]

class QuestionResponse(BaseModel):
    answers: List[str]

class HealthResponse(BaseModel):
    status: str
    components: dict

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Bearer token"""
    # For demo purposes, accept any Bearer token
    # In production, you should implement proper API key validation
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "run": "/hackrx/run"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        system_status = rag_system.get_system_status()
        
        # Determine overall health
        overall_healthy = (
            system_status.get("vector_store_available", False) and
            system_status.get("llm_client_available", False) and
            system_status.get("document_processor_available", False)
        )
        
        return HealthResponse(
            status="healthy" if overall_healthy else "degraded",
            components=system_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            components={"error": str(e)}
        )

@app.post("/hackrx/run", response_model=QuestionResponse)
async def run_rag_system(
    request: QuestionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Main endpoint for processing documents and answering questions.
    
    This endpoint:
    1. Processes the provided document URL
    2. Indexes the document in the vector store
    3. Answers the provided questions using RAG
    """
    try:
        start_time = time.time()
        
        logger.info(f"Processing request with {len(request.questions)} questions")
        
        # Step 1: Process and index the document
        logger.info(f"Processing document: {request.documents}")
        index_result = rag_system.process_and_index_document(request.documents)
        
        if not index_result["success"]:
            logger.error(f"Document indexing failed: {index_result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {index_result.get('error')}"
            )
        
        logger.info(f"Document indexed successfully. Processed {index_result.get('chunks_processed', 0)} chunks")
        
        # Step 2: Answer questions
        logger.info(f"Answering {len(request.questions)} questions")
        answer_result = rag_system.answer_multiple_questions(request.questions)
        
        if not answer_result["success"]:
            logger.error(f"Question answering failed: {answer_result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Question answering failed: {answer_result.get('error')}"
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.info(f"Request completed in {processing_time:.2f} seconds")
        
        return QuestionResponse(answers=answer_result["answers"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /hackrx/run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/v1/process-document")
async def process_document(
    document_url: str,
    api_key: str = Depends(verify_api_key)
):
    """Process and index a single document"""
    try:
        result = rag_system.process_and_index_document(document_url)
        return result
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/v1/answer")
async def answer_single_question(
    question: str,
    document_url: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Answer a single question"""
    try:
        result = rag_system.answer_question(question, document_url)
        return result
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 