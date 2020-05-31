import pyproj
import rasterio

img1 = 'data/img1.tif'
img2 = 'data/img2.tif'

def get_bounds(data):
    """ return in latlon """
    if not data.crs.is_valid:
        raise Exception('data source not valid')

    bound = data.bounds
    pt1 = (bound.left, bound.top)
    pt2 = (bound.right, bound.bottom)

    if data.crs.is_projected:
        transformer = pyproj.Transformer.from_crs(
                data.crs.to_proj4(),
                rasterio.crs.CRS.from_epsg(4326).to_proj4())
        pt1 = transformer.transform(pt1[0], pt1[1])
        pt2 = transformer.transform(pt2[0], pt2[1])
    return tuple([(pt1[i], pt2[i]) for i in range(2)])

data = rasterio.open(img1)
lons, lats = get_bounds(data)
