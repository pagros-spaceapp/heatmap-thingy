import math

import pyproj
import rasterio
import numpy as np

# coords func
def get_bounds(data):
    """ return in latlon """
    if not data.crs.is_valid:
        raise Exception('data source not valid')

    bound = data.bounds
    blon = sorted([bound.left, bound.right])
    blat = sorted([bound.top, bound.bottom])
    pt1 = (blon[0], blat[0])
    pt2 = (blon[1], blat[1])

    if data.crs.is_projected:
        transformer = pyproj.Transformer.from_crs(
                data.crs.to_proj4(),
                rasterio.crs.CRS.from_epsg(4326).to_proj4())
        pt1 = transformer.transform(pt1[0], pt1[1])
        pt2 = transformer.transform(pt2[0], pt2[1])
    return tuple([(pt1[i], pt2[i]) for i in range(2)])

def get_overlap(lons1, lats1, lons2, lats2):
    lons = (max(lons1[0], lons2[0]), min(lons1[1], lons2[1]))
    if lons[0]>lons[1]: return None, None

    lats = (max(lats1[0], lats2[0]), min(lats1[1], lats2[1]))
    if lats[0]>lats[1]: return None, None

    return lons, lats

# data func
def crop_data(data, lons, lats):
    lons0, lats0 = get_bounds(data)
    r_lon, r_lat = [abs(i) for i in data.res]

    d_lon = round((lons[1]-lons[0])/r_lon)
    d_lat = round((lats[1]-lats[0])/r_lat)

    s_lon = round((lons[0]-lons0[0])/r_lon)
    s_lat = round((lats[0]-lats0[0])/r_lat)

    # handle flipping
    grid = data.read()[0]
    if data.bounds.top>data.bounds.bottom: grid = np.flipud(grid)
    if data.bounds.left>data.bounds.right: grid = np.fliplr(grid)

    grid = grid[s_lat:s_lat+d_lat, s_lon:s_lon+d_lon]
    return np.ma.array(grid, mask=(grid==data.nodata))

def scale_img(img1, img2):
    w1, h1 = img1.shape
    w2, h2 = img2.shape
    W = int((w1*w2)/math.gcd(w1,w2))
    H = int((h1*h2)/math.gcd(h1,h2))

    new1 = np.kron(img1, np.ones((W//w1, H//h1)))
    new2 = np.kron(img2, np.ones((W//w2, H//h2)))
    return new1, new2

# filter
def img_log(data, err=1):
    return np.log(data+err)

def img_pow(data, power=1):
    return np.power(data, power)

# NOTE: grid and stuff
def write_tiff(outfile, grid, transform, nodata=0):
    # write to tiff file
    tiff = rasterio.open(
         outfile, 'w',
         driver='GTiff',
         height=grid.shape[0],
         width=grid.shape[1],
         count=1, dtype=grid.dtype,
         crs='+init=epsg:4236',
         transform=transform,
         nodata=nodata
    )

    # if masked, write the nodata back
    if type(grid) is np.ma.core.MaskedArray and nodata is not None:
        mask = np.array(grid.mask)
        grid.mask = np.zeros(grid.shape)
        grid = mask*tiff.nodata + (1-mask)*grid

    tiff.write(grid, 1)
    tiff.close()
