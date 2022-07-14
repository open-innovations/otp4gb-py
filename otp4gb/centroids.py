"""
``otp4gb.centroids`` -- Centroid Processing
--------------------------------------------

"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def load_centroids(path):
    data = pd.read_csv(path)
    geometry = data.apply(
        lambda x: Point([x.Longitude, x.Latitude]), axis=1)
    data=gpd.GeoDataFrame(data[['msoa11cd', 'msoa11nm']], geometry=geometry.values, crs='EPSG:4326')
    return data
