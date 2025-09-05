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
echo "Files successfully written to:"
echo " - $PBF_PATH"
echo " - ${DATA_DIR}/${STATE_SLUG}_highways.pbf"
echo " - ${DATA_DIR}/${STATE_SLUG}_highways.geojson"

## Running in the terminal
# chmod +x osm_download.sh ## only run once(?)
# ./osm_download.sh

## Would like to get the names of different highway types in OSM
## Instal jq

