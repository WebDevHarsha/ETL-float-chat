from config import meta_collection

def query_metadata(user_query: str, n_results: int = 5):
    result = meta_collection.query(query_texts=[user_query], n_results=n_results)
    return result.get("documents", [])
