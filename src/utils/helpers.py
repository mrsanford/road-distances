from pathlib import Path


# constants
BASE_DIR = Path(__file__).resolve().parents[2]
LOGS_INFO = BASE_DIR / "logs"

STATE = "Puerto Rico"
state_url = f"https://download.geofabrik.de/north-america/us/{STATE}.html"
input_pbf = Path(f"./data/{STATE}-latest.osm.pbf")
filtered_pbf = Path(f"./data/{STATE}-roads.osm.pbf")
geojson_file = Path(f"./data/{STATE}-roads.geojson")

# tags to keep
KEEP_TAGS = {
    "highway",
    "name",
    "ref",
    "oneway",
    "surface",
    "lanes",
    "maxspeed",
    "bridge",
    "tunnel",
    "access",
}
