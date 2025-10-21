#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
DEFAULT_REGION="North America"
DEFAULT_COUNTRY="Canada"
DEFAULT_PROVINCE=""  # optional (empty means whole country)
PY_FILE="src/download.py"
DATA_DIR="data"
FEATURE="highways"
# ---------------

REGION="${1:-$DEFAULT_REGION}"
COUNTRY="${2:-$DEFAULT_COUNTRY}"
PROVINCE="${3:-$DEFAULT_PROVINCE}"

# --- Normalizing path names (helpers.py) ---
REGION_SLUG=$(PYTHONPATH=src python3 - <<EOF
from utils.helpers import normalize_area
print(normalize_area("$REGION"))
EOF
)
COUNTRY_SLUG=$(PYTHONPATH=src python3 - <<EOF
from utils.helpers import normalize_area
print(normalize_area("$COUNTRY"))
EOF
)
if [[ -n "$PROVINCE" ]]; then
  PROVINCE_SLUG=$(PYTHONPATH=src python3 - <<EOF
from utils.helpers import normalize_area
print(normalize_area("$PROVINCE"))
EOF
)
  SLUG="$PROVINCE_SLUG"
  PBF_PATH="${DATA_DIR}/${REGION_SLUG}/${COUNTRY_SLUG}/${PROVINCE_SLUG}/${PROVINCE_SLUG}-latest.osm.pbf"
else
  SLUG="$COUNTRY_SLUG"
  PBF_PATH="${DATA_DIR}/${REGION_SLUG}/${COUNTRY_SLUG}/${COUNTRY_SLUG}-latest.osm.pbf"
fi
mkdir -p "$(dirname "$PBF_PATH")"

# downloading osm data
PYTHONPATH=src python3 "$PY_FILE" \
  --region "$REGION" \
  --country "$COUNTRY" \
  ${PROVINCE:+--province "$PROVINCE"}

# running osmium commands
osmium fileinfo -e "$PBF_PATH"
## extracting target highway types
osmium tags-filter "$PBF_PATH" \
  w/highway=motorway,trunk,primary,secondary,tertiary \
  -o "${PBF_PATH%.osm.pbf}_highways_drivable.pbf" --overwrite
## exporting to geojson
osmium export "${PBF_PATH%.osm.pbf}_highways_drivable.pbf" \
  -o "${PBF_PATH%.osm.pbf}_highways.geojson" --overwrite
# Alternate if you want strictly line geometries:
# osmium export "${PBF_PATH%.osm.pbf}_highways_drivable.pbf" \
#   --geometry-types lines \
#   -o "${PBF_PATH%.osm.pbf}_highways.geojson" --overwrite

## building the raster
PYTHONPATH=src python3 src/rasterize.py \
  --region "$REGION" \
  --country "$COUNTRY" \
  ${PROVINCE:+--province "$PROVINCE"} \
  --data-dir "$DATA_DIR" \
  --pixel-degrees 0.0005
## adding logging
echo "Files successfully written to:"
echo " - $PBF_PATH"
echo " - ${PBF_PATH%.osm.pbf}_highways_drivable.pbf"
echo " - ${PBF_PATH%.osm.pbf}_highways.geojson"

## Usage examples:
### chmod +x src/osm_workflow.sh
### ./src/osm_workflow.sh "Africa" "Nigeria"
### ./src/osm_workflow.sh "South America" "Brazil"

# figure out the right size for the raster
# doing the whole world, might have to change the workflow
# using distance-raster library
# might need to make some tag changes
# noexit -- maybe not needed
# opening geojson with fiona with breakpoint -- if it does take a longtime
# make the breakpoint after the fiona open run line
# would it be bad to only use line data where highway=* and leave out points and polygons

# work on visuals
# discerning between roads
# increase comfortability in adjusting
# motorway, trunk, primary, secondary, tertiary

# running this on HPC
# 5 km might be ok but aim for 1 km
# aiming for km^2 cells
