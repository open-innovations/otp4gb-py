"""
``otp4gb.geo`` -- Geographic Operations
--------------------------------------------

"""
import geopandas as gpd
import json
from geojson_rewind import rewind


def parse_to_geo(text):
    data = json.loads(text)
    crs = data['crs']['properties']['name']
    data = gpd.GeoDataFrame.from_features(data, crs=crs)
    return data


def buffer_geometry(data, buffer_size):
    new_geom = data.geometry.to_crs('EPSG:23030')
    buffered_geom = new_geom.buffer(buffer_size)
    data.geometry = buffered_geom.to_crs(data.crs).simplify(
        tolerance=0.0001, preserve_topology=True)
    return data


def sort_by_descending_time(data):
    return data.sort_values(by='time', ascending=False)


def get_valid_json(data):
    return rewind(data.to_json())
