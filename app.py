from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import json

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Database connection parameters (update with your own)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '10000')
DB_NAME = os.getenv('DB_NAME', 'osm_data')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '1234')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/api/voronoi')
def get_voronoi():
    # Retrieve amenity parameter; it is required!
    amenity_param = request.args.get('amenity')
    if not amenity_param:
        return jsonify({"error": "Missing required parameter: amenity"}), 400

    # Clean and split the string into a list
    amenities = [x.strip() for x in amenity_param.split(',') if x.strip()]
    if not amenities:
        return jsonify({"error": "Parameter amenity must contain valid values"}), 400

    # Create an SQL clause to filter for these amenities
    if len(amenities) == 1:
        amenity_filter = f"amenity = '{amenities[0]}'"
    else:
        joined = "', '".join(amenities)
        amenity_filter = f"amenity IN ('{joined}')"

    conn = get_db_connection()
    cur = conn.cursor()

    # Build the SQL query using the amenity filter and Voronoi tessellation
    query = f"""
        WITH points AS (
            SELECT way AS geom
            FROM planet_osm_point
            WHERE {amenity_filter}
        ),
        voronoi AS (
            SELECT
                (ST_Dump(ST_VoronoiPolygons(ST_Collect(geom)))).geom AS geom
            FROM points
        )
        SELECT ST_AsGeoJSON(ST_Intersection(v.geom, h.geometry)) AS geometry
        FROM voronoi v, hamburg_adm h;
    """

    try:
        cur.execute(query)
        rows = cur.fetchall()

        features = []
        for row in rows:
            geometry = row[0]

            # Skip if geometry is None
            if geometry is None:
                continue

            # Attempt to parse geometry if it's a string.
            try:
                if isinstance(geometry, str):
                    geometry_obj = json.loads(geometry)
                else:
                    geometry_obj = geometry

                # Validate that the geometry_obj has the expected keys.
                if not isinstance(geometry_obj, dict) or 'type' not in geometry_obj or 'coordinates' not in geometry_obj:
                    print(f"Invalid geometry structure: {geometry_obj}")
                    continue

            except Exception as e:
                print(f"Error parsing geometry: {e}")
                continue

            feature = {
                "type": "Feature",
                "geometry": geometry_obj,
                "properties": {}
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        # For debugging purposes, print the resulting GeoJSON to the console.
        print("Returning GeoJSON:", json.dumps(geojson, indent=2))
        return jsonify(geojson)
    except Exception as e:
        print(f"Error generating Voronoi polygons: {e}")
        return jsonify({"error": "Error generating Voronoi polygons"}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/heatmap')
def get_heatmap():
    """ Returns heatmap data as a GeoJSON FeatureCollection """
    amenity_param = request.args.get('amenity')
    if not amenity_param:
        return jsonify({"error": "Missing required parameter: amenity"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    query = f"""
        SELECT ST_AsGeoJSON(way) AS geometry
        FROM planet_osm_point
        WHERE amenity = %s;
    """

    try:
        cur.execute(query, (amenity_param,))
        rows = cur.fetchall()

        features = []
        for row in rows:
            geometry = row[0]
            if geometry:
                feature = {
                    "type": "Feature",
                    "geometry": json.loads(geometry),
                    "properties": {}
                }
                features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        return jsonify(geojson)
    except Exception as e:
        print(f"Error fetching heatmap data: {e}")
        return jsonify({"error": "Error fetching heatmap data"}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5003)