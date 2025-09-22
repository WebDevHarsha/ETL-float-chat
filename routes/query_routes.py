from flask import Blueprint, request, jsonify
from services.chroma_service import query_metadata
from services.gemini_service import generate_sql
from services.db_service import execute_sql

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
def handle_query():
    data = request.get_json(silent=True)
    user_query = str(data.get("query", "")).strip() if data else ""

    if not user_query:
        return jsonify({"error": "Missing query parameter"}), 400

    # Step 1: Metadata retrieval
    retrieved_meta = query_metadata(user_query)

    # Step 2: SQL from Gemini
    sql_query = generate_sql(user_query, retrieved_meta)

    if not sql_query.lower().startswith("select"):
        return jsonify({"error": "Only SELECT queries allowed", "sql_generated": sql_query}), 400

    # Step 3: Execute SQL
    try:
        rows = execute_sql(sql_query)
    except Exception as e:
        return jsonify({"error": f"SQL execution failed: {str(e)}", "sql_generated": sql_query}), 500

    return jsonify({
        "query": user_query,
        "metadata_used": retrieved_meta,
        "sql_used": sql_query,
        "results": rows
    })
