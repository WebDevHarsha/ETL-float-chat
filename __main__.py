from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import os
import netCDF4 as nc
import pandas as pd

# ================================================================
# 1. ENV + CONNECTIONS
# ================================================================
load_dotenv(".env.local")
POSTGRES_LINK = os.getenv("POSTGRES_LINK")
NC_FILE = "ocean.nc"

# SQLAlchemy connection
engine = create_engine(POSTGRES_LINK)

# ChromaDB persistent client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
meta_collection = chroma_client.get_or_create_collection(
    name="netcdf_metadata",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

# Gemini client
client = genai.Client()

# Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # allow frontend

# ================================================================
# 2. ETL: Load NetCDF -> Postgres + Chroma metadata
# ================================================================
def run_etl(nc_file: str):
    print("🔄 Running ETL pipeline...")

    ds = nc.Dataset(nc_file)

    df = pd.DataFrame({
        "time": ds.variables["time"][:],
        "cast": ds.variables["cast"][:],
        "cruise": ds.variables["cruise"][:],
        "transect": ds.variables["transect"][:],
        "event": ds.variables["event"][:],
        "station": ds.variables["station"][:],
        "longitude": ds.variables["longitude"][:],
        "latitude": ds.variables["latitude"][:],
        "depth": ds.variables["depth"][:],
        "pressure": ds.variables["pressure"][:],
        "temperature": ds.variables["temperature"][:],
        "salinity": ds.variables["salinity"][:],
        "density": ds.variables["density"][:],
        "transmission": ds.variables["transmission"][:],
        "oxygen": ds.variables["oxygen"][:],
        "oxygenSaturation": ds.variables["oxygenSaturation"][:],
        "par": ds.variables["par"][:],
        "fluorescence": ds.variables["fluorescence"][:],
    })

    df.to_sql("ocean_data", engine, if_exists="replace", index=False)
    print("✅ Data inserted into PostgreSQL (table: ocean_data)")

    # Metadata into Chroma
    documents, metas, ids = [], [], []
    meta_collection.delete(where={"scope": "global"})

    for i, (k, v) in enumerate(ds.__dict__.items()):
        documents.append(f"Global metadata - {k}: {v}")
        metas.append({"scope": "global", "attribute": k})
        ids.append(f"global_meta_{i}")

    for i, (dim_name, dim) in enumerate(ds.dimensions.items()):
        dim_info = {"name": dim_name, "size": len(dim), "isunlimited": dim.isunlimited()}
        documents.append(f"Dimension metadata - {dim_name}: {dim_info}")
        metas.append({"scope": "dimension", "attribute": dim_name})
        ids.append(f"dim_meta_{i}")

    for i, (var_name, var) in enumerate(ds.variables.items()):
        var_info = {
            "name": var_name,
            "dtype": str(var.dtype),
            "shape": var.shape,
            "attributes": var.__dict__,
        }
        documents.append(f"Variable metadata - {var_name}: {var_info}")
        metas.append({"scope": "variable", "attribute": var_name})
        ids.append(f"var_meta_{i}")

    meta_collection.add(documents=documents, metadatas=metas, ids=ids)
    print(f"✅ Inserted {len(documents)} metadata records into ChromaDB")


# ================================================================
# 3. API: POST /query
# ================================================================
@app.route("/query", methods=["POST"])
def handle_query():
    data = request.get_json(silent=True)
    user_query = str(data.get("query", "")).strip() if data else ""
    print(f"Received query: {user_query!r}")

    if not user_query:
        return jsonify({"error": "Missing query parameter"}), 400

    # Step 1: Retrieve metadata from Chroma
    meta_result = meta_collection.query(query_texts=[user_query], n_results=5)
    retrieved_meta = meta_result.get("documents", [])

    # Step 2: Ask Gemini to generate SQL
    gemini_prompt = f"""
    The user asked: "{user_query}".
    You have access to a PostgreSQL table called "ocean_data".
    Relevant metadata from the dataset: {retrieved_meta}
    Generate a PostgreSQL SELECT query using this metadata. Respond ONLY with SQL. 
    Do NOT include any markdown code fences like ```sql``` or ``` in your response.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=gemini_prompt
    )
    sql_query = response.text.strip()

    # Remove any leftover code fences just in case
    sql_query = sql_query.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()

    if not sql_query.lower().startswith("select"):
        return jsonify({"error": "Only SELECT queries allowed", "sql_generated": sql_query}), 400

    # Step 3: Execute SQL on Postgres
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = [dict(row) for row in result.fetchall()]  # works on older SQLAlchemy

    except Exception as e:
        return jsonify({"error": f"SQL execution failed: {str(e)}", "sql_generated": sql_query}), 500

    return jsonify({
        "query": user_query,
        "metadata_used": retrieved_meta,
        "sql_used": sql_query,
        "results": rows
    })


# ================================================================
# 4. Main
# ================================================================
if __name__ == "__main__":
    # run_etl(NC_FILE)
    app.run(host="0.0.0.0", port=5001, debug=True)
