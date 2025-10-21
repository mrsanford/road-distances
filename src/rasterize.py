#!/usr/bin/env python3
import argparse
import logging
import fiona
from shapely.geometry import shape
import distancerasters as dr
from utils.helpers import normalize_area
from utils.utils_loggers import setup_logger
from pathlib import Path


# --- Argument parsing ---
parser = argparse.ArgumentParser(description="Build highway distance raster.")
parser.add_argument("--region", required=True)
parser.add_argument("--country", required=True)
parser.add_argument("--province", default=None)
parser.add_argument("--data-dir", default="data")
parser.add_argument("--pixel-degrees", type=float, default=0.008983)
args = parser.parse_args()

# --- Normalize inputs ---
region = normalize_area(args.region)
country = normalize_area(args.country)
province = normalize_area(args.province) if args.province else None
pixel_size = args.pixel_degrees
data_dir = Path(args.data_dir)

# --- Construct base path ---
if province:
    basepath = data_dir / region / country / province
    slug = province
else:
    basepath = data_dir / region / country
    slug = country

# --- Unified filenames ---
geojson_file = basepath / f"{slug}_highways.geojson"
out_mask = basepath / f"{slug}_highways-mask-4326.tif"
out_dist = basepath / f"{slug}_highways-distance-4326.tif"

# --- Logging setup ---
logger = setup_logger(
    __name__, log_file=f"{region}_distance_raster.log", level=logging.INFO
)
logger.info(f"Region = {region}, Country = {country}, Province = {province or 'None'}")
logger.info(f"Input GeoJSON (expected): {geojson_file}")
logger.info(f"Output Distance Raster: {out_dist}")

# --- Ensure GeoJSON exists ---
if not geojson_file.exists():
    # adapting old file naming schema (if some old files exist)
    alt_patterns = [
        f"{slug}-highways.geojson",
        f"{slug}-latest_highways.geojson",
        f"{slug}-latest-highways.geojson",
        f"{slug}_highways.geojson",  # fallback to normalized underscore
    ]
    for pattern in alt_patterns:
        alt_path = basepath / pattern
        if alt_path.exists():
            logger.warning(f"Primary GeoJSON not found; using alternate: {alt_path}")
            geojson_file = alt_path
            break
    else:
        raise FileNotFoundError(
            f"Could not find GeoJSON file: {geojson_file}\n"
            f"Tried alternates:\n"
            + "\n".join([f" - {basepath / p}" for p in alt_patterns])
        )

# --- Rasterization ---
with fiona.open(geojson_file, "r") as src:
    bounds = src.bounds
    shapes = [shape(feature["geometry"]) for feature in src if feature.get("geometry")]

rv_array, affine = dr.rasterize(
    shapes,
    pixel_size=pixel_size,
    bounds=bounds,
    output=None,
)


def raster_conditional(rarray):
    return rarray == 1


dr_obj = dr.DistanceRaster(
    rv_array,
    affine=affine,
    conditional=raster_conditional,
    output_path=out_dist,
)

dist = dr_obj.dist_array
logger.info(f"Raster array shape: {rv_array.shape}, dtype: {rv_array.dtype}")
logger.info(f"Distance raster written to: {out_dist} (array shape: {dist.shape})")
