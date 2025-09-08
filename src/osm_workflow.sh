#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
DEFAULT_STATE="Puerto Rico"
PY_FILE="src/download.py"
DATA_DIR="data"
FEATURE="highways"
# ---------------

STATE="${1:-$DEFAULT_STATE}"
STATE_SLUG=$(echo "$STATE" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')
PBF_PATH="${DATA_DIR}/${STATE_SLUG}-latest.osm.pbf"

# --- Download OSM data for target US state/territory (PR is default) ---
python3 "$PY_FILE" --state "$STATE"
# --- Run Osmium commands for highway extraction and exporting to GeoJSON ---
osmium fileinfo -e "$PBF_PATH"
## --- Extract highways ---
osmium tags-filter "$PBF_PATH" w/highway \
  -o "${DATA_DIR}/${STATE_SLUG}_highways.pbf" --overwrite
## --- Export to GeoJSON ---
osmium export "${DATA_DIR}/${STATE_SLUG}_highways.pbf" \
  -o "${DATA_DIR}/${STATE_SLUG}_highways.geojson" --overwrite
  ## Alternate for only lines (no points or polygons)
  # osmium export "${DATA_DIR}/${STATE_SLUG}_highways.pbf" \
  # --geometry-types lines \
  # -o "${DATA_DIR}/${STATE_SLUG}_highways.geojson" --overwrite
## -- Building distance raster --
python3 src/make_raster.py \
  --state "$STATE" \
  --data-dir "$DATA_DIR" \
  --pixel-meters 15 ## could change later, might be related to zoom_level
## --- Logging location ---
echo "Files successfully written to:"
echo " - $PBF_PATH"
echo " - ${DATA_DIR}/${STATE_SLUG}_highways.pbf"
echo " - ${DATA_DIR}/${STATE_SLUG}_highways.geojson"

## Running in the terminal
### chmod +x src/osm_workflow.sh
### ./src/osm_workflow.sh

# figure out the right size for the raster
# doing the whole world, might have to change the workflow
# using distance-raster library
# might need to make some tag changes
# noexit -- maybe not needed
# opening geojson with fiona with breakpoint -- if it does take a longtime
# make the breakpoint after the fiona open run line


# would it be bad to only use line data where highway=* and leave out points and polygons