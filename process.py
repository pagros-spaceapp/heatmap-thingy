import rasterio
import numpy as np
Affine = rasterio.transform.Affine

import utils

def echo(msg):
    print('[log]', msg)

def mean_sd(data):
    u = np.mean(data)
    sd = np.sqrt(np.mean(np.power(data-u,2)))
    m = np.max(data)
    return u, sd, m

def get_ssim(data1, data2):
    kl, kc, ks = [0.00001]*3
    el, ec, es = 1, 1, 1

    def covar(data1, u1, data2, u2):
        return np.mean((data1-u1)*(data2-u2))

    def l2comp(v1, v2, k, L):
        c = (k*L)**2
        return (2*v1*v2 + c)/(v1**2 + v2**2 + c)

    def cocomp(s, v1, v2, k, L):
        c = (k*L)**2
        return (s + c)/(v1*v2 + c)

    # luminance
    lum1, con1, L1 = mean_sd(data1)
    lum2, con2, L2 = mean_sd(data2)

    L = max(L1, L2)
    Cl = l2comp(lum1, lum2, kl, L)
    Cc = l2comp(con1, con2, kc, L)

    s = covar(data1, lum1, data2, lum2)
    Cs = cocomp(s, con1, con2, ks, L)
    return np.prod([Cl**el, Cc**ec, Cs**es])

def get_norm(data):
    m, s, l = mean_sd(data)
    return (data-m)/s

def get_psnr(data1, data2):
    err = 10e-10
    L = max(np.max(data1), np.max(data2))**2
    return L/((np.mean((data1-data2)**2))+L)

def process(img1, img2, outfile):
    data1 = rasterio.open(img1)
    lons1, lats1 = utils.get_bounds(data1)

    data2 = rasterio.open(img2)
    lons2, lats2 = utils.get_bounds(data2)

    lons, lats = utils.get_overlap(lons1, lats1, lons2, lats2)
    if not lons or not lats:
        raise Exception(f'ERR no overlap: {lons1} {lats1} {lons2} {lats2}')

    crop1 = utils.crop_data(data1, lons, lats)
    crop2 = utils.crop_data(data2, lons, lats)

    new1, new2 = utils.scale_img(crop1, crop2)
    res = abs(int(new1.shape[0]/crop1.shape[0]) * data1.res[0])

    s = get_ssim(new1, new2)
    print(f'{img1}, {img2}, ssim, {s:.06f}')

    norm1, norm2 = get_norm(new1), get_norm(new2)
    p = get_psnr(norm1, norm2)
    print(f'{img1}, {img2}, pnsr, {p:.06f}')

    transform = Affine.translation(lons[0],lats[0])
    transform *= Affine.scale(res)

    utils.write_tiff(outfile, norm1*norm2,
            transform, nodata=data1.nodata)
