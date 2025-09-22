from typing import List, Dict, Any
import time
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import PydanticOutputParser
from config import llm, SQL_GENERATION_PROMPT
from models.schemas import SQLQueryResult, MetadataResult
import re

class LangChainQueryService:
    """Enhanced query processing service using LangChain"""
    
    def __init__(self):
        self.sql_chain = LLMChain(
            llm=llm,
            prompt=SQL_GENERATION_PROMPT,
            verbose=True
        )
        
    def generate_sql_with_langchain(self, user_query: str, metadata_docs: List[str]) -> SQLQueryResult:
        """Generate SQL query using LangChain with enhanced error handling"""
        try:
            start_time = time.time()
            
            # Prepare metadata context
            metadata_context = "\n".join(metadata_docs[:5]) if metadata_docs else "No specific metadata found"
            
            # Table schema information
            table_schema = """
            ocean_data table columns:
            - time (float): Time measurements
            - cast, cruise, transect, event, station (int): Measurement identifiers
            - longitude, latitude (float): Geographic coordinates
            - depth, pressure (float): Depth and pressure measurements
            - temperature, salinity, density (float): Physical water properties
            - transmission, par, fluorescence (float): Optical measurements
            - oxygen, oxygenSaturation (float): Chemical measurements
            """
            
            # Generate SQL using LangChain
            result = self.sql_chain.run(
                user_query=user_query,
                metadata=metadata_context,
                table_schema=table_schema
            )
            
            # Clean up the result
            sql_query = self._clean_sql_response(result)
            
            # Validate the SQL
            validation_result = self._validate_sql(sql_query)
            
            return SQLQueryResult(
                sql_query=sql_query,
                is_valid=validation_result["is_valid"],
                error_message=validation_result.get("error")
            )
            
        except Exception as e:
            return SQLQueryResult(
                sql_query="",
                is_valid=False,
                error_message=f"SQL generation failed: {str(e)}"
            )
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean and format the SQL response from LLM"""
        sql_query = response.strip()
        
        # Remove common markdown formatting
        sql_query = re.sub(r'```sql\s*', '', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'```\s*$', '', sql_query)
        sql_query = re.sub(r'^sql\s*', '', sql_query, flags=re.IGNORECASE)
        
        # Remove extra whitespace and newlines
        sql_query = ' '.join(sql_query.split())
        
        return sql_query
    
    def _validate_sql(self, sql_query: str) -> Dict[str, Any]:
        """Enhanced SQL validation"""
        if not sql_query:
            return {"is_valid": False, "error": "Empty SQL query"}
            
        sql_lower = sql_query.lower().strip()
        
        # Check if it's a SELECT query
        if not sql_lower.startswith('select'):
            return {"is_valid": False, "error": "Only SELECT queries are allowed"}
        
        # Check for dangerous keywords
        dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 'truncate', 'exec']
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', sql_lower):
                return {"is_valid": False, "error": f"Dangerous SQL keyword '{keyword}' not allowed"}
        
        # Basic syntax checks
        if sql_query.count('(') != sql_query.count(')'):
            return {"is_valid": False, "error": "Mismatched parentheses in SQL query"}
        
        # Ensure it references the correct table
        if 'ocean_data' not in sql_lower:
            return {"is_valid": False, "error": "Query must reference the 'ocean_data' table"}
        
        return {"is_valid": True}
    
    def enhance_metadata_search(self, query: str, metadata_docs: List[str]) -> MetadataResult:
        """Enhance metadata search results with relevance scoring"""
        # For now, return the documents as-is, but this could be enhanced
        # with additional LangChain components for better relevance scoring
        return MetadataResult(
            documents=metadata_docs,
            relevance_scores=None  # Could add scoring logic here
        )

# Global service instance
langchain_service = LangChainQueryService()