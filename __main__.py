import netCDF4 as nc
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv(".env.local")  # take environment variables from .env

link = os.getenv("POSTGRES_LINK")


fn = "ocean.nc"
ds = nc.Dataset(fn)

# 2. Extract all required variables
time = ds.variables["time"][:]
cast = ds.variables["cast"][:]
cruise = ds.variables["cruise"][:]
transect = ds.variables["transect"][:]
event = ds.variables["event"][:]
station = ds.variables["station"][:]
longitude = ds.variables["longitude"][:]
latitude = ds.variables["latitude"][:]
depth = ds.variables["depth"][:]
pressure = ds.variables["pressure"][:]
temperature = ds.variables["temperature"][:]
salinity = ds.variables["salinity"][:]
density = ds.variables["density"][:]
transmission = ds.variables["transmission"][:]
oxygen = ds.variables["oxygen"][:]
oxygenSaturation = ds.variables["oxygenSaturation"][:]
par = ds.variables["par"][:]
fluorescence = ds.variables["fluorescence"][:]

# 3. Convert to DataFrame
df = pd.DataFrame({
    "time": time,
    "cast": cast,
    "cruise": cruise,
    "transect": transect,
    "event": event,
    "station": station,
    "longitude": longitude,
    "latitude": latitude,
    "depth": depth,
    "pressure": pressure,
    "temperature": temperature,
    "salinity": salinity,
    "density": density,
    "transmission": transmission,
    "oxygen": oxygen,
    "oxygenSaturation": oxygenSaturation,
    "par": par,
    "fluorescence": fluorescence
})

engine = create_engine(link)

# 5. Insert into PostgreSQL
df.to_sql("ocean_data", engine, if_exists="replace", index=False)

print("✅ Data inserted into PostgreSQL table 'ocean_data'")
