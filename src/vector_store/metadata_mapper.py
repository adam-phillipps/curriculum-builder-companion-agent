"""
Metadata mapping service for ChromaDB integration.
Provides type-safe mapping between our content metadata and ChromaDB metadata.
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

class MetadataType(Enum):
    """Supported metadata types for ChromaDB."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON_ARRAY = "json_array"
    DATETIME = "datetime"

@dataclass
class MetadataField:
    """Definition of a metadata field for ChromaDB."""
    name: str
    type: MetadataType
    required: bool = False
    default: Any = None
    description: str = ""

class ChromaMetadataMapper:
    """Maps learning content metadata to ChromaDB-compatible format."""
    
    # Define all supported metadata fields
    METADATA_SCHEMA = {
        # Core content fields
        "content_id": MetadataField("content_id", MetadataType.INTEGER, True, description="Database content ID"),
        "title": MetadataField("title", MetadataType.STRING, True, description="Content title"),
        "description": MetadataField("description", MetadataType.STRING, False, "", description="Content description"),
        
        # Content classification
        "tier": MetadataField("tier", MetadataType.STRING, False, "T2", description="Difficulty tier (T1-T4)"),
        "content_type": MetadataField("content_type", MetadataType.STRING, False, "lesson", description="Type of content"),
        "personas": MetadataField("personas", MetadataType.JSON_ARRAY, False, [], description="Target learner roles"),
        "tags": MetadataField("tags", MetadataType.JSON_ARRAY, False, [], description="Topic tags"),
        
        # Duration and cost
        "estimated_duration": MetadataField("estimated_duration", MetadataType.INTEGER, False, 60, description="Duration in minutes"),
        "estimated_cost": MetadataField("estimated_cost", MetadataType.FLOAT, False, 0.0, description="Estimated cost in USD"),
        
        # Technical requirements
        "sandbox_type": MetadataField("sandbox_type", MetadataType.STRING, False, "individual", description="Required sandbox environment"),
        "aws_services": MetadataField("aws_services", MetadataType.JSON_ARRAY, False, [], description="AWS services used"),
        "learning_objectives": MetadataField("learning_objectives", MetadataType.JSON_ARRAY, False, [], description="Learning objectives"),
        
        # Author and source information
        "author": MetadataField("author", MetadataType.STRING, False, "", description="Primary author"),
        "co_authors": MetadataField("co_authors", MetadataType.JSON_ARRAY, False, [], description="Co-authors list"),
        "sources": MetadataField("sources", MetadataType.STRING, False, "", description="Reference sources"),
        "artifacts": MetadataField("artifacts", MetadataType.STRING, False, "", description="Supplementary materials"),
        "ai_assisted": MetadataField("ai_assisted", MetadataType.STRING, False, "", description="AI tools used"),
        
        # Timestamps
        "created_at": MetadataField("created_at", MetadataType.DATETIME, False, description="Creation timestamp"),
        "updated_at": MetadataField("updated_at", MetadataType.DATETIME, False, description="Last update timestamp"),
        
        # Status and approval
        "status": MetadataField("status", MetadataType.STRING, False, "draft", description="Content status"),
        "is_approved": MetadataField("is_approved", MetadataType.BOOLEAN, False, False, description="Approval status"),
        
        # Vector store specific
        "content_hash": MetadataField("content_hash", MetadataType.STRING, False, "", description="Content hash for deduplication"),
    }
    
    @classmethod
    def to_chroma_metadata(cls, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert content metadata to ChromaDB-compatible format."""
        chroma_metadata = {}
        
        for field_name, field_def in cls.METADATA_SCHEMA.items():
            value = content_metadata.get(field_name, field_def.default)
            
            # Handle different data types
            if field_def.type == MetadataType.STRING:
                chroma_metadata[field_name] = str(value) if value is not None else ""
                
            elif field_def.type == MetadataType.INTEGER:
                chroma_metadata[field_name] = int(value) if value is not None else 0
                
            elif field_def.type == MetadataType.FLOAT:
                chroma_metadata[field_name] = float(value) if value is not None else 0.0
                
            elif field_def.type == MetadataType.BOOLEAN:
                chroma_metadata[field_name] = bool(value) if value is not None else False
                
            elif field_def.type == MetadataType.JSON_ARRAY:
                # ChromaDB doesn't support arrays directly, so we serialize to JSON
                if isinstance(value, (list, tuple)):
                    chroma_metadata[field_name] = json.dumps(value)
                elif isinstance(value, str):
                    # Already serialized
                    chroma_metadata[field_name] = value
                else:
                    chroma_metadata[field_name] = json.dumps([])
                    
            elif field_def.type == MetadataType.DATETIME:
                if isinstance(value, datetime):
                    chroma_metadata[field_name] = value.isoformat()
                elif isinstance(value, str):
                    chroma_metadata[field_name] = value
                else:
                    chroma_metadata[field_name] = ""
        
        return chroma_metadata
    
    @classmethod
    def from_chroma_metadata(cls, chroma_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ChromaDB metadata back to our content format."""
        content_metadata = {}
        
        for field_name, field_def in cls.METADATA_SCHEMA.items():
            value = chroma_metadata.get(field_name)
            
            if value is None:
                content_metadata[field_name] = field_def.default
                continue
            
            # Handle different data types
            if field_def.type == MetadataType.JSON_ARRAY:
                try:
                    content_metadata[field_name] = json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    content_metadata[field_name] = []
                    
            elif field_def.type == MetadataType.DATETIME:
                if isinstance(value, str) and value:
                    try:
                        content_metadata[field_name] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        content_metadata[field_name] = None
                else:
                    content_metadata[field_name] = None
                    
            else:
                content_metadata[field_name] = value
        
        return content_metadata
    
    @classmethod
    def build_filter_query(cls, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB-compatible filter query from user filters."""
        chroma_filters = {}
        filter_conditions = []
        
        for filter_name, filter_value in filters.items():
            if filter_name not in cls.METADATA_SCHEMA:
                continue
                
            field_def = cls.METADATA_SCHEMA[filter_name]
            
            # Handle different filter types
            if isinstance(filter_value, dict):
                # Range queries (e.g., {"min": 30, "max": 120} for duration)
                if "min" in filter_value or "max" in filter_value:
                    # ChromaDB has limited range query support, skip complex ranges
                    continue
            elif isinstance(filter_value, list):
                # Multiple values (OR condition) - ChromaDB uses $in operator
                if filter_value:
                    filter_conditions.append({filter_name: {"$in": filter_value}})
            elif filter_value is not None and filter_value != "":
                # Simple equality
                if field_def.type == MetadataType.JSON_ARRAY:
                    # For array fields, we need to check if the value is contained
                    # This is complex in ChromaDB, so we'll handle it in post-processing
                    continue
                else:
                    filter_conditions.append({filter_name: filter_value})
        
        # Build proper ChromaDB query with $and operator for multiple conditions
        if len(filter_conditions) == 0:
            return {}
        elif len(filter_conditions) == 1:
            return filter_conditions[0]
        else:
            return {"$and": filter_conditions}
        
        return chroma_filters
    
    @classmethod
    def get_searchable_fields(cls) -> List[str]:
        """Get list of fields that can be used for filtering."""
        return [
            "tier", "content_type", "sandbox_type", "author", "status",
            "is_approved", "estimated_duration", "estimated_cost"
        ]
    
    @classmethod
    def get_array_fields(cls) -> List[str]:
        """Get list of fields that contain arrays."""
        return [
            "personas", "tags", "aws_services", "learning_objectives", "co_authors"
        ]
    
    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate metadata against schema and return errors."""
        errors = {"missing": [], "invalid": []}
        
        for field_name, field_def in cls.METADATA_SCHEMA.items():
            value = metadata.get(field_name)
            
            # Check required fields
            if field_def.required and (value is None or value == ""):
                errors["missing"].append(field_name)
                continue
            
            # Type validation
            if value is not None:
                try:
                    if field_def.type == MetadataType.INTEGER:
                        int(value)
                    elif field_def.type == MetadataType.FLOAT:
                        float(value)
                    elif field_def.type == MetadataType.BOOLEAN:
                        bool(value)
                    elif field_def.type == MetadataType.JSON_ARRAY:
                        if isinstance(value, str):
                            json.loads(value)
                except (ValueError, TypeError, json.JSONDecodeError):
                    errors["invalid"].append(f"{field_name}: invalid {field_def.type.value}")
        
        return errors

# Global mapper instance
metadata_mapper = ChromaMetadataMapper()