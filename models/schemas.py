from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import re

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query about oceanographic data")

class SQLQueryResult(BaseModel):
    sql_query: str = Field(..., description="Generated SQL query")
    is_valid: bool = Field(True, description="Whether the SQL query is valid")
    error_message: Optional[str] = Field(None, description="Error message if SQL is invalid")
    
    @validator('sql_query')
    def validate_sql_query(cls, v):
        v = v.strip()
        if not v.lower().startswith('select'):
            raise ValueError("Only SELECT queries are allowed")
        
        # Basic SQL injection prevention
        dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 'truncate']
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', v.lower()):
                raise ValueError(f"Dangerous SQL keyword '{keyword}' not allowed")
        
        return v

class MetadataResult(BaseModel):
    documents: List[str] = Field(default_factory=list, description="Retrieved metadata documents")
    relevance_scores: Optional[List[float]] = Field(None, description="Relevance scores for metadata")

class QueryExecutionResult(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Query execution results")
    row_count: int = Field(0, description="Number of rows returned")
    execution_time: Optional[float] = Field(None, description="Query execution time in seconds")

class QueryResponse(BaseModel):
    query: str = Field(..., description="Original user query")
    metadata_used: List[str] = Field(default_factory=list, description="Metadata used for SQL generation")
    sql_query: str = Field(..., description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Query results")
    row_count: int = Field(0, description="Number of rows returned")
    execution_time: Optional[float] = Field(None, description="Total execution time")
    workflow_state: Optional[str] = Field(None, description="Current workflow state")

class WorkflowState(BaseModel):
    user_query: str
    metadata_result: Optional[MetadataResult] = None
    sql_result: Optional[SQLQueryResult] = None
    execution_result: Optional[QueryExecutionResult] = None
    current_step: str = "start"
    error: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True