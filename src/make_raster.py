import fiona
import logging
from shapely.geometry import shape
import distancerasters as dr
from utils.helpers import STATE, normalize_area

# config
state = normalize_area(STATE)
IN_PATH = f"data/{state}_highways.geojson"
OUT_MASK = f"data/{state}_highways-mask-4326.tif"
OUT_DIST = f"data/{state}_highways-distance-4326.tif"
# pixel_size = 0.044915  # ~5km at equator
pixel_size = 0.008983  # ~1km at equator
# instantiate logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


with fiona.open(IN_PATH, "r") as src:
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
    output_path=OUT_DIST,
)

dist = dr_obj.dist_array
logger.info(f"rv_array shape: {rv_array.shape}, dtype: {rv_array.dtype}")
# for writing the mask raster to file
# logger.info(f"Raster Mask written to {OUT_MASK}")
logger.info(f"Distance Raster written to {OUT_DIST} with array shape {dist.shape}")
