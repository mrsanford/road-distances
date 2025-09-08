import fiona
import rasterio
import distancerasters as dr
from utils.helpers import STATE
from download import state_normalized

# path to vector dataset
state = state_normalized(STATE)
GEOJSON_PATH = f"/data/{state}-highways.geojson"
# opening the shapefile
shp = fiona.open(GEOJSON_PATH, "r")
breakpoint

# resolution
pixel_size = 0.01  # pixel size in meters

# rasterizing the vector data and outputting to GeoTIFF
rv_array, affine = dr.rasterize(
    shp,
    pixel_size=pixel_size,
    bounds=shp.bounds,
    output=f"data/{state}-highways-raster.tif",
)

# manually exporting rasterized vector data (optional)
## dr.export_raster(rv_array, affine, f"data/{state}-highways-raster.tif")

# opening with rasterio
with rasterio.open(f"data/{state}-highways-raster.tif") as src:
    affine = src.transform
    rv_array = src.read(1)


def raster_conditional(rarray):
    return rarray == 1


# generate distance array and output to geotiff
my_dr = dr.DistanceRaster(
    rv_array,
    affine=affine,
    output_path="examples/linestrings_distance_raster.tif",
    conditional=raster_conditional,
)
