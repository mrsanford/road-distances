from pathlib import Path
import re
from utils.admin_bounds import target_area, PROVINCES


# ----------------------------------------------------------------------
# PATH CONSTANTS
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
LOGS_INFO = BASE_DIR / "logs"


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def normalize_area(area: str) -> str:
    """
    Normalizes for GeoFabrik format (lowercase, spaces to hyphens, strip accents/special chars).
    """
    area = area.strip().lower().replace(" ", "-")
    area = re.sub(r"[^a-z0-9\-]", "", area)
    return area


def build_url(
    region: str, country: str = None, province: str = None, html: bool = False
) -> str:
    """
    Builds download URL for GeoFabrik based on hierarchical structure (region/country/province).
        - region (str) : e.g. "europe" and IS ALWAYS REQUIRED
        - country (str) : e.g. "france" or "germany" and OPTIONAL
        - province (str) : e.g. "provence-alpes-cote-d-azur" or "baden-wuerttemberg" and OPTIONAL
    Default returns .osm.pbf download link; set html=True to return .html index link.
    """
    region = normalize_area(region)
    if country:
        country = normalize_area(country)
        if province:
            province = normalize_area(province)
            suffix = ".html" if html else "-latest.osm.pbf"
            return (
                f"https://download.geofabrik.de/{region}/{country}/{province}{suffix}"
            )
        suffix = ".html" if html else "-latest.osm.pbf"
        return f"https://download.geofabrik.de/{region}/{country}{suffix}"
    suffix = ".html" if html else "-latest.osm.pbf"
    return f"https://download.geofabrik.de/{region}{suffix}"


def make_local_paths(region: str, country: str = None, province: str = None):
    """
    Generate local paths for raw PBF, filtered PBF, and GeoJSON.
    Ensures directories exist.
    """
    # build subpath components (drop None)
    subpath = [normalize_area(p) for p in [region, country, province] if p]
    name = subpath[-1]  # last element is the filename stem

    # base directory: ./data/<region>/<country>/<province>
    basepath = Path("./data").joinpath(*subpath)
    basepath.mkdir(parents=True, exist_ok=True)

    input_pbf = basepath / f"{name}-latest.osm.pbf"
    filtered_pbf = basepath / f"{name}-roads.osm.pbf"
    geojson_file = basepath / f"{name}-roads.geojson"

    return input_pbf, filtered_pbf, geojson_file


# ----------------------------------------------------------------------
# URL + PATH GENERATION
# ----------------------------------------------------------------------
def iterate_areas():
    for region, countries in target_area.items():
        if not countries:
            # region-only
            url = build_url(region)
            yield region, None, None, url, make_local_paths(region)
        else:
            for country in countries:
                if country in PROVINCES:
                    for province in PROVINCES[country]:
                        url = build_url(region, country, province)
                        yield (
                            region,
                            country,
                            province,
                            url,
                            make_local_paths(region, country, province),
                        )
                else:
                    url = build_url(region, country)
                    yield region, country, None, url, make_local_paths(region, country)


# ----------------------------------------------------------------------
# EXAMPLE RUN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    for region, country, province, url, paths in iterate_areas():
        input_pbf, filtered_pbf, geojson_file = paths
        print(f"Region={region}, Country={country}, Province={province}")
        print(f"  URL: {url}")
        print(f"  Local paths:")
        print(f"    input_pbf: {input_pbf}")
        print(f"    filtered_pbf: {filtered_pbf}")
        print(f"    geojson_file: {geojson_file}")
        print()


# ----------------------------------------------------------------------
# TAGS TO KEEP
# ----------------------------------------------------------------------
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
