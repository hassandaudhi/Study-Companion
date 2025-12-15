from pinecone import Pinecone, ServerlessSpec
from app.config.rag_config import RAGConfig
from app.config.settings import settings
from app.utils.logger import logger
from typing import List, Dict, Any, Optional
import uuid


class PineconeService:
    """Service for managing vector embeddings in Pinecone with Google Gemini"""

    def __init__(self):
        """Initialize Pinecone client and Gemini embeddings"""
        self._pc = None
        self._index = None
        self._embeddings = None
        self._initialized = False
        self.index_name = settings.PINECONE_INDEX_NAME

    @property
    def pc(self):
        """Lazy initialization of Pinecone client"""
        if self._pc is None:
            self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        return self._pc

    @property
    def embeddings(self):
        """Lazy initialization of embeddings"""
        if self._embeddings is None:
            self._embeddings = RAGConfig.get_embeddings()
        return self._embeddings

    @property
    def index(self):
        """Lazy initialization of Pinecone index"""
        if self._index is None:
            self._init_index()
        return self._index

    def _init_index(self) -> None:
        """Initialize Pinecone index if it doesn't exist"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]

            if self.index_name not in index_names:
                # Create new index with Google Gemini embedding dimension
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )

            # Connect to index
            self._index = self.pc.Index(self.index_name)
            self._initialized = True
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {str(e)}")
            raise

    async def create_embeddings(
        self,
        texts: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create embeddings for a list of texts and store in Pinecone
        
        Args:
            texts: List of text strings to embed
            metadata_list: Optional list of metadata dicts for each text
        
        Returns:
            List of dicts with vector_id, text, and metadata
        """
        try:
            # Generate embeddings
            embeddings = await self.embeddings.aembed_documents(texts)

            # Prepare vectors for upsert
            vectors = []
            results = []

            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                vector_id = str(uuid.uuid4())
                metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
                metadata["text"] = text  # Store original text in metadata

                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })

                results.append({
                    "vector_id": vector_id,
                    "text": text,
                    "metadata": metadata
                })

            # Upsert vectors to Pinecone
            self.index.upsert(vectors=vectors)

            return results
        except Exception as e:
            raise Exception(f"Failed to create embeddings: {str(e)}")

    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone
        
        Args:
            query: Query text to search for
            top_k: Number of results to return
            filter: Optional metadata filter
        
        Returns:
            List of similar results with text and metadata
        """
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)

            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )

            # Format results
            similar_items = []
            for match in results.matches:
                similar_items.append({
                    "vector_id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })

            return similar_items
        except Exception as e:
            raise Exception(f"Failed to search embeddings: {str(e)}")

    async def delete_embeddings(self, vector_ids: List[str]) -> bool:
        """
        Delete embeddings from Pinecone
        
        Args:
            vector_ids: List of vector IDs to delete
        
        Returns:
            True if successful
        """
        try:
            self.index.delete(ids=vector_ids)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete embeddings: {str(e)}")

    async def delete_by_metadata(self, filter: Dict[str, Any]) -> bool:
        """
        Delete embeddings by metadata filter
        
        Args:
            filter: Metadata filter to match vectors for deletion
        
        Returns:
            True if successful
        """
        try:
            self.index.delete(filter=filter)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete embeddings by metadata: {str(e)}")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            raise Exception(f"Failed to get index stats: {str(e)}")


# Singleton instance
pinecone_service = PineconeService()
