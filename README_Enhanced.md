# ETL FloatChat - Enhanced with LangChain & LangGraph

An intelligent ETL pipeline for oceanographic data processing with AI-powered natural language querying using LangChain and LangGraph workflow orchestration.

## 🚀 New Features

### LangChain Integration
- **Enhanced Prompt Management**: Structured prompts for better SQL generation
- **Output Validation**: Pydantic models for robust data validation
- **Improved Error Handling**: Better error messages and validation

### LangGraph Workflow Orchestration
- **State Machine**: Organized query processing pipeline
- **Step-by-Step Processing**: Clear workflow stages with logging
- **Error Recovery**: Graceful error handling at each step
- **Workflow Visibility**: Track processing progress

## 📋 Installation

```bash
pip install -r requirement.txt
```

## 🔧 Configuration

Create a `.env.local` file with:
```
POSTGRES_LINK=postgresql://username:password@host:port/database
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🏃‍♂️ Running the Application

```bash
python app.py
```

The API will be available at `http://localhost:5001`

## 📡 API Endpoints

### POST /query
Process natural language queries about oceanographic data.

**Request:**
```json
{
    "query": "Show me temperature and salinity data for depths greater than 100m"
}
```

**Response:**
```json
{
    "query": "Show me temperature and salinity data for depths greater than 100m",
    "metadata_used": ["Variable metadata - depth: {...}", "..."],
    "sql_query": "SELECT depth, temperature, salinity FROM ocean_data WHERE depth > 100 LIMIT 100;",
    "results": [
        {"depth": 150.5, "temperature": 15.2, "salinity": 35.1},
        "..."
    ],
    "row_count": 45,
    "execution_time": 0.032,
    "total_processing_time": 1.245,
    "workflow_state": "completed"
}
```

### GET /health
Check API health and enabled features.

### GET /schema
Get database schema and sample queries.

## 🔄 Workflow Process

The enhanced system uses a LangGraph state machine with these steps:

1. **Metadata Retrieval** - Query ChromaDB for relevant metadata
2. **SQL Generation** - Use LangChain to generate SQL from natural language
3. **Validation** - Validate SQL syntax and security
4. **Execution** - Execute query against PostgreSQL
5. **Response Formatting** - Format and return results

## 🛠️ Architecture

### Enhanced Components

- **LangChain Service** (`services/langchain_service.py`)
  - Structured prompt templates
  - Enhanced SQL generation with validation
  - Better error handling and response cleaning

- **LangGraph Workflow** (`workflows/query_workflow.py`)
  - State machine for query processing
  - Step-by-step workflow orchestration
  - Comprehensive logging and error handling

- **Pydantic Models** (`models/schemas.py`)
  - Input validation with `QueryRequest`
  - Structured responses with `QueryResponse`
  - SQL validation with `SQLQueryResult`
  - Workflow state management

### Data Models

#### Available Data Columns
- **Identifiers**: time, cast, cruise, transect, event, station
- **Location**: longitude, latitude, depth, pressure
- **Physical**: temperature, salinity, density
- **Optical**: transmission, par, fluorescence
- **Chemical**: oxygen, oxygenSaturation

## 🎯 Sample Queries

Try these natural language queries:

- "What is the average temperature at different depths?"
- "Show me locations with high oxygen levels"
- "Find salinity measurements for cruise number 5"
- "What's the temperature range for each station?"
- "Show me fluorescence data where depth is less than 50m"

## 🔒 Security Features

- **SQL Injection Protection**: Validates queries for dangerous keywords
- **Query Restriction**: Only SELECT queries allowed
- **Input Validation**: Pydantic models ensure data integrity
- **Error Sanitization**: Safe error messages without exposing internals

## 📊 Workflow Monitoring

The system provides detailed workflow state tracking:
- Current processing step
- Execution times for each stage
- Error locations and descriptions
- Metadata usage statistics

## 🚀 Future Enhancements

- [ ] Async FastAPI migration for better performance
- [ ] JWT authentication
- [ ] Dynamic ETL for various NetCDF formats
- [ ] Enhanced metadata structuring
- [ ] Real-time query streaming
- [ ] Workflow visualization dashboard

## 🛠️ Development

### Project Structure
```
ETL-float-chat/
├── app.py                 # Flask application
├── config.py             # LangChain & database configuration
├── etl.py                # ETL pipeline
├── models/
│   └── schemas.py        # Pydantic data models
├── services/
│   ├── langchain_service.py   # LangChain query processing
│   ├── chroma_service.py     # Vector database service
│   └── db_service.py         # PostgreSQL service
├── workflows/
│   └── query_workflow.py     # LangGraph workflow
└── routes/
    └── query_routes.py       # Enhanced API routes
```

### Dependencies
- **LangChain**: LLM orchestration and prompt management
- **LangGraph**: Workflow state machine
- **Pydantic**: Data validation and serialization
- **ChromaDB**: Vector database for metadata
- **PostgreSQL**: Primary data storage
- **Flask**: Web API framework