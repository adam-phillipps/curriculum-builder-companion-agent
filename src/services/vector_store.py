"""
Vector store service for content similarity and search.
Uses ChromaDB for efficient similarity detection with metadata filtering.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json
import requests
import traceback
from datetime import datetime
from src.config import get_settings
from src.vector_store.metadata_mapper import metadata_mapper

settings = get_settings()

class VectorStoreService:
    """Service for managing learning content vectors and similarity search."""
    
    def __init__(self):
        """Initialize service with lazy connection."""
        self._client = None
        self._approved_collection = None
        self._draft_collection = None
        self._outcomes_collection = None
    
    @property
    def client(self):
        """Lazy initialization of ChromaDB client."""
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=Settings(chroma_client_timeout_seconds=10)
            )
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
    
    @property
    def outcomes_collection(self):
        """Lazy initialization of learning outcomes collection."""
        if self._outcomes_collection is None:
            self._outcomes_collection = self._get_or_create_collection("learning_outcomes")
        return self._outcomes_collection
    
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
        is_approved: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> str:
        """Add content to vector store with comprehensive metadata."""
        
        # Generate content hash and vector ID
        content_hash = self._hash_content(content_text)
        vector_id = self._generate_content_id(content_id, content_hash)
        
        # Prepare document for embedding
        document = f"Title: {title}\nDescription: {description}\nContent: {content_text}"
        
        # Prepare comprehensive metadata using mapper
        full_metadata = {
            "content_id": content_id,
            "title": title,
            "description": description,
            "content_hash": content_hash,
            "is_approved": is_approved,
            "created_at": created_at or datetime.now(),
            "updated_at": updated_at or datetime.now(),
            **metadata  # Include all provided metadata
        }
        
        # Convert to ChromaDB-compatible format
        vector_metadata = metadata_mapper.to_chroma_metadata(full_metadata)
        
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
        
        # Build ChromaDB where clause using metadata mapper
        where_clause = {}
        if metadata_filters:
            where_clause = metadata_mapper.build_filter_query(metadata_filters)
        
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
                                # Convert ChromaDB metadata back to our format
                                content_metadata = metadata_mapper.from_chroma_metadata(metadata)
                                content_metadata["similarity_score"] = round(similarity_score, 3)
                                all_similar_items.append(content_metadata)
                except Exception as e:
                    print(f"Error querying collection: {e}")
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
    
    def add_learning_outcome(
        self,
        outcome_id: int,
        name: str,
        description: str,
        domain: str,
        difficulty_level: str,
        tags: List[str] = None
    ) -> str:
        """Add learning outcome to vector store."""
        
        # Generate vector ID
        vector_id = f"outcome_{outcome_id}"
        
        # Prepare document for embedding
        tags_text = " ".join(tags) if tags else ""
        document = f"Name: {name}\nDescription: {description}\nDomain: {domain}\nTags: {tags_text}"
        
        # Prepare metadata (ChromaDB only accepts str, int, float, bool)
        metadata = {
            "outcome_id": outcome_id,
            "name": name,
            "description": description or "",
            "domain": domain,
            "difficulty_level": difficulty_level,
            "tags_str": ",".join(tags) if tags else ""  # Convert list to comma-separated string
        }
        
        # Add to ChromaDB
        try:
            self.outcomes_collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[vector_id]
            )
        except Exception as e:
            if "already exists" in str(e).lower():
                # Update existing entry
                self.outcomes_collection.update(
                    documents=[document],
                    metadatas=[metadata],
                    ids=[vector_id]
                )
            else:
                raise
        
        return vector_id
    
    def find_similar_outcomes(
        self,
        query_text: str,
        max_results: int = 10,
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find similar learning outcomes using vector similarity."""
        
        # Build where clause for domain filtering
        where_clause = None
        if domain_filter:
            where_clause = {"domain": domain_filter}
        
        try:
            # Query ChromaDB
            results = self.outcomes_collection.query(
                query_texts=[query_text],
                n_results=max_results,
                where=where_clause
            )
            
            # Process results
            similar_outcomes = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    # Convert distance to similarity score
                    similarity_score = max(0, 1 / (1 + distance))
                    
                    outcome_data = {
                        "outcome_id": metadata["outcome_id"],
                        "name": metadata["name"],
                        "description": metadata["description"],
                        "domain": metadata["domain"],
                        "difficulty_level": metadata["difficulty_level"],
                        "tags": metadata["tags_str"].split(",") if metadata["tags_str"] else [],
                        "similarity_score": round(similarity_score, 3)
                    }
                    similar_outcomes.append(outcome_data)
            
            # Sort by similarity score
            similar_outcomes.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similar_outcomes
            
        except Exception as e:
            print(f"Error searching similar outcomes: {e}")
            return []
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about stored content."""
        try:
            approved_count = self.approved_collection.count()
            draft_count = self.draft_collection.count()
            outcomes_count = self.outcomes_collection.count()
            
            return {
                "approved_content_count": approved_count,
                "draft_content_count": draft_count,
                "learning_outcomes_count": outcomes_count,
                "total_content_count": approved_count + draft_count
            }
        except Exception as e:
            print(f"Error getting content stats: {e}")
            return {"error": str(e)}

# Global instance
vector_store = VectorStoreService()