"""Loads data/places.geojson into PostGIS using GeoPandas."""
import os
import geopandas as gpd
from sqlalchemy import create_engine, text

DB_URL = os.getenv("SQLALCHEMY_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/geochat")

gdf = gpd.read_file("data/places.geojson")          # read GeoJSON into a GeoDataFrame
gdf = gdf.rename_geometry("geom")                    # column name used in our SQL
gdf = gdf.set_crs(epsg=4326, allow_override=True)    # lon/lat

engine = create_engine(DB_URL)
gdf.to_postgis("places", engine, if_exists="replace", index=False)

with engine.begin() as conn:
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_places_geom ON places USING GIST (geom)"))

print(f"Loaded {len(gdf)} places into PostGIS")
