import pandas as pd
import netCDF4 as nc
from config import engine, meta_collection

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
