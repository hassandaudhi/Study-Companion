from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import MemoryResponse
from app.services.database_services import MemoryDBService
from app.services.rag_service import rag_service
from app.services.pinecone_service import pinecone_service
from typing import List, Dict, Any

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/", response_model=List[MemoryResponse], status_code=status.HTTP_201_CREATED)
async def create_embeddings(
    user_id: int,
    texts: List[str],
    file_id: int = None,
    content_type: str = "general",
    metadata: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """
    Create embeddings and store in Pinecone and PostgreSQL using RAG pipeline
    
    Args:
        user_id: User ID
        texts: List of text strings to embed
        file_id: Optional file ID to associate with embeddings
        content_type: Type of content (summary, question, explanation, resource)
        metadata: Additional metadata
    """
    try:
        # Validate input
        if not texts or len(texts) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="texts list cannot be empty"
            )
        # Combine texts into a single document for processing
        combined_text = "\n\n".join(texts)

        # Use RAG service to process and store
        result = await rag_service.process_and_store_document(
            text=combined_text,
            user_id=user_id,
            file_id=file_id,
            content_type=content_type,
            metadata=metadata,
            db=db
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )

        # Retrieve the created memory records
        memories = MemoryDBService.get_user_memories(db, user_id, skip=0, limit=result["embeddings_stored"])

        return memories[-result["embeddings_stored"]:]  # Return only newly created

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embeddings: {str(e)}"
        )


@router.get("/search")
async def search_embeddings(
    query: str,
    user_id: int,
    top_k: int = 5,
    content_type: str = None,
    db: Session = Depends(get_db)
):
    """
    Search for similar embeddings based on query using RAG service
    
    Args:
        query: Query text to search for
        user_id: User ID to filter by
        top_k: Number of results to return (default: 5, max: 50)
        content_type: Optional content type filter
    """
    try:
        # Validate input
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="query cannot be empty"
            )

        # Validate top_k range
        if top_k < 1 or top_k > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="top_k must be between 1 and 50"
            )
        # Use RAG service for context retrieval
        result = await rag_service.retrieve_context(
            query=query,
            user_id=user_id,
            top_k=top_k,
            content_type=content_type
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )

        return {
            "query": query,
            "context": result["context"],
            "chunks_retrieved": result["chunks_retrieved"],
            "chunks": result["chunks"],
            "scores": result["scores"],
            "metadata": result["metadata"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search embeddings: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[MemoryResponse])
def get_user_memories(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all memory records for a user"""
    return MemoryDBService.get_user_memories(db, user_id, skip, limit)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    """Delete memory embedding from both Pinecone and PostgreSQL"""
    try:
        # Get memory record
        memory = MemoryDBService.get_memory(db, memory_id)
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found"
            )

        # Delete from Pinecone
        await pinecone_service.delete_embeddings([memory.vector_id])

        # Delete from PostgreSQL
        MemoryDBService.delete_memory(db, memory_id)

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )


@router.get("/stats")
def get_memory_stats():
    """Get statistics about the memory/embeddings index"""
    try:
        stats = pinecone_service.get_index_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory stats: {str(e)}"
        )
