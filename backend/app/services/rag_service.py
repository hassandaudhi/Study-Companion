"""
RAG (Retrieval-Augmented Generation) Service

This service implements the complete RAG pipeline for context-aware AI responses,
including document processing, embedding storage, and semantic retrieval.
"""

from typing import List, Dict, Any, Optional
from app.config.rag_config import RAGConfig
from app.services.pinecone_service import pinecone_service
from app.services.database_services import MemoryDBService
from sqlalchemy.orm import Session


class RAGService:
    """
    Complete RAG Pipeline Service
    Handles document processing, embedding storage, and context-aware retrieval
    """

    def __init__(self):
        self.text_splitter = RAGConfig.get_text_splitter()
        self.embeddings = RAGConfig.get_embeddings()
        self.top_k = RAGConfig.TOP_K_RESULTS

    async def process_and_store_document(
        self,
        text: str,
        user_id: int,
        file_id: Optional[int] = None,
        content_type: str = "document",
        metadata: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: Split text → Create embeddings → Store in Pinecone + PostgreSQL
        
        Args:
            text: Text content to process
            user_id: User ID
            file_id: Optional file ID
            content_type: Type of content (document, summary, question, etc.)
            metadata: Additional metadata
            db: Database session
        
        Returns:
            Dict with processing results
        """
        try:
            # Step 1: Split text into chunks
            chunks = self.text_splitter.split_text(text)

            if not chunks:
                return {
                    "status": "error",
                    "message": "No text chunks generated",
                    "chunks_created": 0
                }

            # Step 2: Prepare metadata for each chunk
            chunk_metadata_list = []
            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    "user_id": user_id,
                    "content_type": content_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                if file_id:
                    chunk_meta["file_id"] = file_id
                if metadata:
                    chunk_meta.update(metadata)
                chunk_metadata_list.append(chunk_meta)

            # Step 3: Create embeddings and store in Pinecone
            embeddings_result = await pinecone_service.create_embeddings(
                texts=chunks,
                metadata_list=chunk_metadata_list
            )

            # Step 4: Store metadata in PostgreSQL (if db session provided)
            if db:
                from app.schemas.schemas import MemoryCreate
                for embedding in embeddings_result:
                    memory_create = MemoryCreate(
                        user_id=user_id,
                        file_id=file_id,
                        vector_id=embedding["vector_id"],
                        content=embedding["text"],
                        content_type=content_type,
                        metadata=embedding["metadata"]
                    )
                    MemoryDBService.create_memory(db, memory_create)

            return {
                "status": "success",
                "chunks_created": len(chunks),
                "embeddings_stored": len(embeddings_result),
                "vector_ids": [e["vector_id"] for e in embeddings_result],
                "chunk_sizes": [len(chunk) for chunk in chunks]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "chunks_created": 0
            }

    async def retrieve_context(
        self,
        query: str,
        user_id: int,
        top_k: Optional[int] = None,
        content_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query (RAG retrieval step)
        
        Args:
            query: User query
            user_id: User ID to filter results
            top_k: Number of results to return
            content_type: Optional content type filter
            min_score: Minimum similarity score threshold
        
        Returns:
            Dict with retrieved context and metadata
        """
        try:
            # Prepare filter
            filter_dict = {"user_id": user_id}
            if content_type:
                filter_dict["content_type"] = content_type

            # Search in Pinecone
            results = await pinecone_service.search_similar(
                query=query,
                top_k=top_k or self.top_k,
                filter=filter_dict
            )

            # Filter by score if min_score is provided
            if min_score:
                results = [r for r in results if r["score"] >= min_score]

            # Combine retrieved texts into context
            context_chunks = [r["text"] for r in results]
            combined_context = "\n\n".join(context_chunks)

            return {
                "status": "success",
                "query": query,
                "context": combined_context,
                "chunks_retrieved": len(results),
                "chunks": context_chunks,
                "scores": [r["score"] for r in results],
                "metadata": [r["metadata"] for r in results]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "context": "",
                "chunks_retrieved": 0
            }

    async def rag_query(
        self,
        question: str,
        user_id: int,
        agent_type: str = "explainer",
        top_k: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG query: Retrieve context → Generate answer
        
        Args:
            question: User question
            user_id: User ID
            agent_type: Type of agent to use (explainer, summarizer, etc.)
            top_k: Number of context chunks to retrieve
            parameters: Additional parameters for the agent
        
        Returns:
            Dict with answer and RAG metadata
        """
        try:
            # Step 1: Retrieve relevant context
            retrieval_result = await self.retrieve_context(
                query=question,
                user_id=user_id,
                top_k=top_k
            )

            if retrieval_result["status"] == "error":
                return {
                    "status": "error",
                    "message": f"Context retrieval failed: {retrieval_result['message']}",
                    "answer": None
                }

            # Step 2: Use agent to generate answer with context
            from app.agents.langchain_agents import get_agent

            agent = get_agent(agent_type)
            context = retrieval_result["context"]

            # Generate answer based on agent type
            if agent_type == "explainer":
                result = await agent.explain(question, context=context, parameters=parameters)
                answer = result["explanation"]
            else:
                # Fallback for other agent types
                result = {"output": "Agent type not optimized for RAG queries"}
                answer = result.get("output", "No answer generated")

            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "context_used": context,
                "chunks_retrieved": retrieval_result["chunks_retrieved"],
                "retrieval_scores": retrieval_result["scores"],
                "model": RAGConfig.MODEL_NAME,
                "agent_metadata": result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "answer": None
            }

    async def process_multiple_documents(
        self,
        documents: List[Dict[str, Any]],
        user_id: int,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Process multiple documents in batch
        
        Args:
            documents: List of documents with 'text', 'file_id', 'content_type', 'metadata'
            user_id: User ID
            db: Database session
        
        Returns:
            Dict with batch processing results
        """
        results = []
        total_chunks = 0
        total_embeddings = 0

        for doc in documents:
            result = await self.process_and_store_document(
                text=doc.get("text", ""),
                user_id=user_id,
                file_id=doc.get("file_id"),
                content_type=doc.get("content_type", "document"),
                metadata=doc.get("metadata"),
                db=db
            )
            results.append(result)
            total_chunks += result.get("chunks_created", 0)
            total_embeddings += result.get("embeddings_stored", 0)

        return {
            "status": "success",
            "documents_processed": len(documents),
            "total_chunks_created": total_chunks,
            "total_embeddings_stored": total_embeddings,
            "individual_results": results
        }

    def get_rag_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get RAG statistics for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with RAG statistics
        """
        try:
            # Get Pinecone index stats
            index_stats = pinecone_service.get_index_stats()

            return {
                "status": "success",
                "user_id": user_id,
                "pinecone_stats": index_stats,
                "chunk_size": RAGConfig.CHUNK_SIZE,
                "chunk_overlap": RAGConfig.CHUNK_OVERLAP,
                "embedding_model": RAGConfig.EMBEDDING_MODEL,
                "top_k_default": RAGConfig.TOP_K_RESULTS
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Singleton instance
rag_service = RAGService()
