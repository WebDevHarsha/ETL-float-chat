# ETL Float Chat

An experimental ETL and query system for NetCDF oceanographic data. The project reads structured `.nc` files, loads the tabular data into PostgreSQL, indexes metadata in ChromaDB, and exposes a Flask API for natural-language querying using Gemini-powered SQL generation.

## Overview

This project is designed to help users ask questions like:

- "What is the average temperature at different depths?"
- "Show me salinity values for a specific cruise or station"
- "Find high-oxygen regions in the dataset"

The system transforms raw ocean data into queryable records and uses metadata + LLM assistance to convert natural-language requests into SQL.

## Features

- NetCDF ingestion and ETL pipeline
- PostgreSQL storage for cleaned tabular data
- ChromaDB metadata indexing for dataset understanding
- Gemini-based SQL generation from natural language
- Flask API with CORS enabled
- Basic validation and routing structure for query handling

## Tech Stack

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- NetCDF4
- ChromaDB
- Google Generative AI (Gemini)
- Pandas
- Python-dotenv

## Project Structure

```text
ETL-float-chat/
├── app.py                 # Flask app entry point
├── config.py              # Environment config, DB, Chroma, Gemini setup
├── etl.py                 # NetCDF ETL pipeline
├── ocean.nc               # Sample NetCDF dataset
├── requirement.txt        # Python package requirements
├── Readme.md              # Project documentation
├── todo                   # Project TODO list
├── models/                # Data/schema models
├── routes/                # API routes
├── services/              # Service layer logic
├── workflows/             # Workflow orchestration modules
├── chroma_db/             # Local Chroma persistence (generated)
└── .env.local             # Local environment variables (not committed)
```

## Installation

1. Clone the repository
2. Create a virtual environment (optional but recommended)
3. Install dependencies:

```bash
pip install -r requirement.txt
```

## Configuration

Create a `.env.local` file in the project root with the following values:

```env
POSTGRES_LINK=postgresql://username:password@host:port/database
GOOGLE_API_KEY=your_gemini_api_key_here
```

The application loads this file via `python-dotenv` in `config.py`.

## Running the Application

```bash
python app.py
```

The Flask app will run on:

```text
http://localhost:5001
```

## API Endpoints

### POST /query

Submit a natural language query about the dataset.

Example request:

```json
{
  "query": "Show me temperature and salinity data for depths greater than 100m"
}
```

Example response:

```json
{
  "query": "Show me temperature and salinity data for depths greater than 100m",
  "metadata_used": ["Variable metadata - depth: {...}", "..."],
  "sql_query": "SELECT depth, temperature, salinity FROM ocean_data WHERE depth > 100 LIMIT 100;",
  "results": [
    {"depth": 150.5, "temperature": 15.2, "salinity": 35.1}
  ],
  "row_count": 45,
  "execution_time": 0.032,
  "total_processing_time": 1.245,
  "workflow_state": "completed"
}
```

### GET /health

Returns the health status of the service.

### GET /schema

Returns schema information and sample queries for the dataset.

## ETL Pipeline

The ETL process does the following:

1. Opens the NetCDF file using `netCDF4`
2. Extracts important variables into a Pandas DataFrame
3. Writes the dataframe into PostgreSQL as the table `ocean_data`
4. Stores metadata (global, dimension, and variable metadata) into ChromaDB

This makes the data both structured for database querying and searchable for metadata-driven NLP reasoning.

## Dataset Notes

The sample dataset includes fields such as:

- time
- cast
- cruise
- transect
- event
- station
- longitude
- latitude
- depth
- pressure
- temperature
- salinity
- density
- transmission
- oxygen
- oxygenSaturation
- par
- fluorescence

## Current Roadmap / TODO

The project is currently evolving. Planned improvements include:

1. Build a dynamic ETL pipeline that can ingest multiple NetCDF formats and structures
2. Add schema validation using Zod-like validation patterns (or equivalent Python validation)
3. Improve error handling and edge-case management
4. Store more structured metadata in ChromaDB
5. Move to an async FastAPI backend for better scalability
6. Add JWT-based security for API access

## Development Notes

This repo is a strong starting point for a semantic data querying system built around scientific NetCDF files. It combines:

- raw dataset ingestion
- structured DB storage
- vector metadata search
- natural-language-to-SQL assistance

## License

This project currently does not include a license file. If this is intended for public or production use, add an appropriate license such as MIT or Apache 2.0.

## Contributing

Contributions are welcome. If you plan to improve the ETL logic, add validation, or enhance the AI query flow, please keep the project modular and document changes clearly.

