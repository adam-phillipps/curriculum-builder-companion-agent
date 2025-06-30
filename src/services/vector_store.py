"""
Vector store service for content similarity and search.
Uses ChromaDB for efficient similarity detection with metadata filtering.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json
from src.config import get_settings

settings = get_settings()

class VectorStoreService:
    """Service for managing learning content vectors and similarity search."""
    
    def __init__(self):
        """Initialize service with lazy connection."""
        self._client = None
        self._approved_collection = None
        self._draft_collection = None
    
    @property
    def client(self):
        """Lazy initialization of ChromaDB client."""
        if self._client is None:
            try:
                # Try PersistentClient first, fallback to HttpClient
                try:
                    # For development, use PersistentClient with shared volume
                    self._client = chromadb.PersistentClient(
                        path="/tmp/chroma_data"
                    )
                except Exception as e:
                    print(f"PersistentClient failed: {e}, trying HttpClient...")
                    # Fallback to HttpClient
                    self._client = chromadb.HttpClient(
                        host=settings.CHROMA_HOST,
                        port=settings.CHROMA_PORT
                    )
                # Test connection
                self._client.heartbeat()
            except Exception as e:
                print(f"ChromaDB connection failed: {e}")
                # For development, we can continue without vector store
                self._client = None
                raise
        return self._client
    
    @property
    def approved_collection(self):
        """Lazy initialization of approved collection."""
        if self._approved_collection is None:
            self._approved_collection = self._get_or_create_collection("approved_content")
        return self._approved_collection
    
    @property
    def draft_collection(self):
        """Lazy initialization of draft collection."""
        if self._draft_collection is None:
            self._draft_collection = self._get_or_create_collection("draft_content")
        return self._draft_collection
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        try:
            return self.client.get_collection(name=name)
        except Exception as e:
            print(f"Collection {name} not found, creating: {e}")
            return self.client.create_collection(
                name=name,
                metadata={"description": f"Learning content collection: {name}"}
            )
    
    def _generate_content_id(self, content_id: int, content_hash: str) -> str:
        """Generate unique vector ID for content."""
        return f"content_{content_id}_{content_hash[:8]}"
    
    def _hash_content(self, content: str) -> str:
        """Generate hash of content for deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_content(
        self, 
        content_id: int,
        title: str,
        description: str,
        content_text: str,
        metadata: Dict[str, Any],
        is_approved: bool = False
    ) -> str:
        """Add content to vector store."""
        
        # Generate content hash and vector ID
        content_hash = self._hash_content(content_text)
        vector_id = self._generate_content_id(content_id, content_hash)
        
        # Prepare document for embedding
        document = f"Title: {title}\nDescription: {description}\nContent: {content_text}"
        
        # Enhanced metadata with searchable fields
        vector_metadata = {
            "content_id": content_id,
            "title": title,
            "description": description,
            "tier": metadata.get("tier", ""),
            "content_type": metadata.get("content_type", ""),
            "personas": json.dumps(metadata.get("personas", [])),
            "aws_services": json.dumps(metadata.get("aws_services", [])),
            "estimated_duration": metadata.get("estimated_duration", 0),
            "estimated_cost": metadata.get("estimated_cost", 0.0),
            "sandbox_type": metadata.get("sandbox_type", ""),
            "content_hash": content_hash,
            "is_approved": is_approved
        }
        
        # Choose collection based on approval status
        collection = self.approved_collection if is_approved else self.draft_collection
        
        # Add to ChromaDB
        try:
            collection.add(
                documents=[document],
                metadatas=[vector_metadata],
                ids=[vector_id]
            )
        except Exception as e:
            print(f"Error adding to ChromaDB collection: {e}")
            # Try to handle duplicate IDs
            if "already exists" in str(e).lower():
                # Update existing entry
                collection.update(
                    documents=[document],
                    metadatas=[vector_metadata],
                    ids=[vector_id]
                )
            else:
                raise
        
        return vector_id
    
    def find_similar_content(
        self,
        query_text: str,
        metadata_filters: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.3,
        max_results: int = 10,
        search_approved_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Find similar content using vector similarity and metadata filtering."""
        
        # Search both collections if not restricted to approved only
        collections_to_search = []
        if search_approved_only:
            collections_to_search = [self.approved_collection]
        else:
            collections_to_search = [self.approved_collection, self.draft_collection]
        
        # Build ChromaDB where clause from filters (simplified for compatibility)
        where_clause = {}
        if metadata_filters:
            for key, value in metadata_filters.items():
                if key in ["tier", "content_type", "sandbox_type"] and value:
                    where_clause[key] = value
                # Skip complex range queries that cause ChromaDB issues
        
        try:
            # Search across all specified collections
            all_similar_items = []
            
            for collection in collections_to_search:
                try:
                    # Query ChromaDB
                    results = collection.query(
                        query_texts=[query_text],
                        n_results=max_results,
                        where=where_clause if where_clause else None
                    )
                    
                    # Process results
                    if results["documents"] and results["documents"][0]:
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results["documents"][0],
                            results["metadatas"][0], 
                            results["distances"][0]
                        )):
                            # Convert distance to similarity score
                            # ChromaDB uses squared euclidean distance, convert to similarity (0-1)
                            # Lower distance = higher similarity
                            similarity_score = max(0, 1 / (1 + distance))  # Normalize distance to 0-1 range
                            
                            # Filter by similarity threshold
                            if similarity_score >= similarity_threshold:
                                all_similar_items.append({
                                    "content_id": metadata["content_id"],
                                    "title": metadata["title"],
                                    "description": metadata["description"],
                                    "tier": metadata["tier"],
                                    "content_type": metadata["content_type"],
                                    "similarity_score": round(similarity_score, 3),
                                    "personas": json.loads(metadata.get("personas", "[]")),
                                    "aws_services": json.loads(metadata.get("aws_services", "[]")),
                                    "estimated_duration": metadata["estimated_duration"],
                                    "estimated_cost": metadata["estimated_cost"]
                                })
                except Exception as e:
                    print(f"Error querying collection: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Sort by similarity score and limit results
            all_similar_items.sort(key=lambda x: x["similarity_score"], reverse=True)
            return all_similar_items[:max_results]
            
        except Exception as e:
            print(f"Error searching similar content: {e}")
            return []
    
    def update_content_status(self, content_id: int, approve: bool = True):
        """Move content between draft and approved collections."""
        # This would involve querying one collection, getting the content, 
        # adding to the other collection, and removing from the original
        # Implementation depends on specific workflow requirements
        pass
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about stored content."""
        try:
            approved_count = self.approved_collection.count()
            draft_count = self.draft_collection.count()
            
            return {
                "approved_content_count": approved_count,
                "draft_content_count": draft_count,
                "total_content_count": approved_count + draft_count
            }
        except Exception as e:
            print(f"Error getting content stats: {e}")
            return {"error": str(e)}

# Global instance
vector_store = VectorStoreService()