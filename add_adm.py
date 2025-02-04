import os
import geopandas as gpd
from sqlalchemy import create_engine

# Database connection settings
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '10000')
DB_NAME = os.getenv('DB_NAME', 'osm_data')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '1234')

# Create connection string
connection_string = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create SQLAlchemy engine
engine = create_engine(connection_string)

# Read the GeoJSON file
de = gpd.read_file('gadm41_DEU_1.json')

# Filter the GeoDataFrame only for Hamburg
hamburg = de[de["NAME_1"] == "Hamburg"]

# Write filtered data to PostgreSQL database
hamburg.to_postgis('hamburg_adm', engine, if_exists='replace', index=False)

print("Data successfully written to the database.")