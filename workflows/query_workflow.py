from typing import Dict, Any, List
import time
from langgraph.graph import StateGraph, END
from models.schemas import WorkflowState, MetadataResult, SQLQueryResult, QueryExecutionResult, QueryResponse
from services.chroma_service import query_metadata
from services.langchain_service import langchain_service
from services.db_service import execute_sql
from langgraph.graph import StateGraph, START, END

class QueryWorkflow:
    """LangGraph-based workflow for processing natural language queries"""
    
    def __init__(self):
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph state machine for query processing"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("retrieve_metadata", self.retrieve_metadata)
        workflow.add_node("generate_sql", self.generate_sql)
        workflow.add_node("validate_sql", self.validate_sql)
        workflow.add_node("execute_query", self.execute_query)
        workflow.add_node("format_response", self.format_response)
        workflow.add_node("handle_error", self.handle_error)
        
        # Define the workflow edges
        workflow.set_entry_point("retrieve_metadata")
        
        # Metadata retrieval -> SQL generation
        workflow.add_edge("retrieve_metadata", "generate_sql")
        
        # SQL generation -> validation
        workflow.add_edge("generate_sql", "validate_sql")
        
        # Conditional edges from validation
        workflow.add_conditional_edges(
            "validate_sql",
            self._should_execute_query,
            {
                "execute": "execute_query",
                "error": "handle_error"
            }
        )
        
        # Query execution -> format response
        workflow.add_edge("execute_query", "format_response")
        
        # Error handling and response formatting -> END
        workflow.add_edge("handle_error", END)
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def retrieve_metadata(self, state: WorkflowState) -> WorkflowState:
        """Step 1: Retrieve relevant metadata from ChromaDB"""
        try:
            print(f"🔍 Retrieving metadata for query: {state.user_query}")
            
            # Query ChromaDB for relevant metadata
            metadata_docs = query_metadata(state.user_query, n_results=5)
            
            # Enhance metadata with LangChain service
            metadata_result = langchain_service.enhance_metadata_search(
                state.user_query, 
                metadata_docs[0] if metadata_docs else []
            )
            
            state.metadata_result = metadata_result
            state.current_step = "metadata_retrieved"
            
            print(f"✅ Retrieved {len(metadata_result.documents)} metadata documents")
            
        except Exception as e:
            state.error = f"Metadata retrieval failed: {str(e)}"
            state.current_step = "error"
        
        return state
    
    def generate_sql(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Generate SQL query using LangChain"""
        try:
            print("🤖 Generating SQL query using LangChain...")
            
            metadata_docs = state.metadata_result.documents if state.metadata_result else []
            
            # Use LangChain service to generate SQL
            sql_result = langchain_service.generate_sql_with_langchain(
                state.user_query,
                metadata_docs
            )
            
            state.sql_result = sql_result
            state.current_step = "sql_generated"
            
            print(f"📝 Generated SQL: {sql_result.sql_query}")
            
        except Exception as e:
            state.error = f"SQL generation failed: {str(e)}"
            state.current_step = "error"
        
        return state
    
    def validate_sql(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Validate the generated SQL query"""
        try:
            print("✅ Validating SQL query...")
            
            if not state.sql_result or not state.sql_result.is_valid:
                state.error = state.sql_result.error_message if state.sql_result else "No SQL result"
                state.current_step = "error"
            else:
                state.current_step = "sql_validated"
                print("✅ SQL validation passed")
                
        except Exception as e:
            state.error = f"SQL validation failed: {str(e)}"
            state.current_step = "error"
        
        return state
    
    def execute_query(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Execute the validated SQL query"""
        try:
            print("🗄️ Executing SQL query...")
            
            start_time = time.time()
            
            # Execute the SQL query
            results = execute_sql(state.sql_result.sql_query)
            
            execution_time = time.time() - start_time
            
            state.execution_result = QueryExecutionResult(
                results=results,
                row_count=len(results),
                execution_time=execution_time
            )
            
            state.current_step = "query_executed"
            
            print(f"✅ Query executed successfully, returned {len(results)} rows in {execution_time:.2f}s")
            
        except Exception as e:
            state.error = f"Query execution failed: {str(e)}"
            state.current_step = "error"
        
        return state
    
    def format_response(self, state: WorkflowState) -> WorkflowState:
        """Step 5: Format the final response"""
        try:
            print("📋 Formatting response...")
            
            state.current_step = "completed"
            
            print("✅ Response formatted successfully")
            
        except Exception as e:
            state.error = f"Response formatting failed: {str(e)}"
            state.current_step = "error"
        
        return state
    
    def handle_error(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow"""
        print(f"❌ Error in workflow: {state.error}")
        state.current_step = "error_handled"
        return state
    
    def _should_execute_query(self, state: WorkflowState) -> str:
        """Determine whether to execute the query or handle an error"""
        if state.current_step == "error" or (state.sql_result and not state.sql_result.is_valid):
            return "error"
        return "execute"
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Main entry point for processing a query through the workflow"""
        print(f"\n🚀 Starting workflow for query: '{user_query}'\n")
        
        # Initialize state
        initial_state = WorkflowState(
            user_query=user_query,
            current_step="start"
        )
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        # Build response
        if final_state.current_step == "completed":
            response = QueryResponse(
                query=user_query,
                metadata_used=final_state.metadata_result.documents if final_state.metadata_result else [],
                sql_query=final_state.sql_result.sql_query if final_state.sql_result else "",
                results=final_state.execution_result.results if final_state.execution_result else [],
                row_count=final_state.execution_result.row_count if final_state.execution_result else 0,
                execution_time=final_state.execution_result.execution_time if final_state.execution_result else None,
                workflow_state=final_state.current_step
            )
            
            return response.dict()
        
        else:
            # Error response
            return {
                "query": user_query,
                "error": final_state.error,
                "workflow_state": final_state.current_step,
                "sql_generated": final_state.sql_result.sql_query if final_state.sql_result else None
            }

# Global workflow instance
query_workflow = QueryWorkflow()