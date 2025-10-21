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
    Constructs consistent local paths for OSM .pbf and derived files.
    Automatically creates directories if they don't exist.

    Returns:
        (input_pbf, output_pbf, output_geojson)
    """
    # normalizing filenames
    region_slug = normalize_area(region)
    country_slug = normalize_area(country) if country else None
    province_slug = normalize_area(province) if province else None
    base_dir = Path("data") / region_slug
    if country_slug:
        base_dir = base_dir / country_slug
    if province_slug:
        base_dir = base_dir / province_slug
    # checking base directory existence
    base_dir.mkdir(parents=True, exist_ok=True)
    # building filenames
    if province_slug:
        name_part = province_slug
    elif country_slug:
        name_part = country_slug
    else:
        name_part = region_slug
    input_pbf = base_dir / f"{name_part}-latest.osm.pbf"
    output_pbf = base_dir / f"{name_part}_highways_drivable.pbf"
    output_geojson = base_dir / f"{name_part}_highways.geojson"
    return input_pbf, output_pbf, output_geojson


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
        print(" Local paths:")
        print(f"    input_pbf: {input_pbf}")
        print(f"    filtered_pbf: {filtered_pbf}")
        print(f"    geojson_file: {geojson_file}")


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
