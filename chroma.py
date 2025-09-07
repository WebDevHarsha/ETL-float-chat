import netCDF4 as nc
from pprint import pprint
import chromadb
from chromadb.utils import embedding_functions

# 1. Load NetCDF file
fn = "ocean.nc"
ds = nc.Dataset(fn)

# 2. Setup Chroma client & collection
client = chromadb.PersistentClient(path="./chroma_db")  # or InMemoryClient()
collection = client.get_or_create_collection(
    name="netcdf_metadata",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)
collection.delete(where={"scope": "global"}) 


documents, metas, ids = [], [], []

# 3a. Global metadata
for i, (k, v) in enumerate(ds.__dict__.items()):
    doc_text = f"Global metadata - {k}: {v}"
    documents.append(doc_text)
    metas.append({"scope": "global", "attribute": k})
    ids.append(f"global_meta_{i}")

# 3b. Dimensions metadata
for i, (dim_name, dim) in enumerate(ds.dimensions.items()):
    dim_info = {
        "name": dim_name,
        "size": len(dim),
        "isunlimited": dim.isunlimited()
    }
    doc_text = f"Dimension metadata - {dim_name}: {dim_info}"
    documents.append(doc_text)
    metas.append({"scope": "dimension", "attribute": dim_name})
    ids.append(f"dim_meta_{i}")

# 3c. Variables metadata
for i, (var_name, var) in enumerate(ds.variables.items()):
    var_info = {
        "name": var_name,
        "dtype": str(var.dtype),
        "shape": var.shape,
        "attributes": var.__dict__
    }
    doc_text = f"Variable metadata - {var_name}: {var_info}"
    documents.append(doc_text)
    metas.append({"scope": "variable", "attribute": var_name})
    ids.append(f"var_meta_{i}")

# 4. Insert all metadata into Chroma
collection.add(
    documents=documents,
    metadatas=metas,
    ids=ids
)

print(f"✅ Inserted {len(documents)} metadata records into ChromaDB")

# 5. Example query
results = collection.query(
    query_texts=["temperature data"],
    n_results=5
)
pprint(results)
