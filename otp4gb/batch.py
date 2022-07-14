"""
``otp4gb.batch`` -- Batch Operations
--------------------------------------------
"""
import logging
import operator
import os
import pandas as pd
from multiprocessing import get_logger

from otp4gb.geo import buffer_geometry, get_valid_json, parse_to_geo, sort_by_descending_time
from otp4gb.logging import stderr_handler
from otp4gb.net import api_call


logger = get_logger()
logger.setLevel(level=logging.INFO)
logger.addHandler(stderr_handler)


def build_run_spec(name_key, modes, centroids, arrive_by, travel_time_max, travel_time_step, max_walk_distance, server):
    items = []
    for _, destination in centroids.iterrows():
        name = destination[name_key]
        location = [destination.geometry.y, destination.geometry.x]
        for mode in modes:
            cutoffs = [('cutoffSec', str(c*60))
                       for c in range(travel_time_step, travel_time_max+1, travel_time_step)]
            query = [
                ('fromPlace', ','.join([str(x) for x in location])),
                ('mode', mode),
                ('date', arrive_by.date()),
                ('time', arrive_by.time()),
                ('maxWalkDistance', str(max_walk_distance)),
                ('arriveby', 'false'),
            ] + cutoffs
            url = server.get_url('isochrone', query=query)
            batch_spec = {
                'name': name,
                'travel_time': arrive_by,
                'url': url,
                'mode': mode,
                'destination': destination,
            }
            items.append(batch_spec)
    return items


def setup_worker(config):
    global output_dir, centroids, buffer_size, FILENAME_PATTERN, name_key
    output_dir = config.get('output_dir')
    centroids = config.get('centroids')
    buffer_size = config.get('buffer_size')
    FILENAME_PATTERN = config.get('FILENAME_PATTERN')
    name_key = config.get('name_key')


def run_batch(batch_args):
    logger.debug('args = %s', batch_args)
    url, name, mode, travel_time, destination = operator.itemgetter(
        'url', 'name', 'mode', 'travel_time', 'destination')(batch_args)

    logger.info('Processing %s for %s', mode, name)

    #   Calculate travel isochrone up to a number of cutoff times (1 to 90 mins)
    logger.debug('Getting URL %s', url)
    data = api_call(url)

    data = parse_to_geo(data)

    data = buffer_geometry(data, buffer_size=buffer_size)

    data = sort_by_descending_time(data)
    largest = data.loc[[0]]

    origins = centroids.clip(largest)
    origins = origins.assign(travel_time='')

    # Set working directory
    os.chdir(output_dir)

    # Calculate all possible origins within travel time by minutes
    for i in range(data.shape[0]):
        row = data.iloc[[i]]
        journey_time = int(row.time)
        logger.debug('Journey time %s', journey_time)
        geojson_file = FILENAME_PATTERN.format(
            location_name=name,
            mode=mode,
            buffer_size=buffer_size,
            arrival_time=travel_time,
            journey_time=journey_time/60,
        )
        # Write isochrone
        with open(geojson_file, 'w') as f:
            f.write(get_valid_json(row))

        covered_indexes = origins.clip(row).index
        logger.debug('Mode %s for %s covers %s centroids in %s seconds',
                     mode, name,
                     len(covered_indexes), int(row.time))
        updated_times = pd.DataFrame(
            {'travel_time': journey_time}, index=covered_indexes)
        origins.update(updated_times)

    travel_time_matrix = pd.DataFrame({
        'OriginName': origins[name_key],
        'OriginLatitude': origins.geometry.y,
        'OriginLongitude': origins.geometry.x,
        'DestinationName': name,
        'DestinationLatitude': destination.geometry.y,
        'DestinationLongitide': destination.geometry.x,
        'Mode': mode,
        'Minutes': origins.travel_time/60,
    })
    # Drop duplicate source / destination
    travel_time_matrix = travel_time_matrix[~(
        travel_time_matrix['OriginName'] == travel_time_matrix['DestinationName'])]

    logger.debug('Travel Matrix ==>\n%s', travel_time_matrix)

    # Convert to native python list
    travel_time_matrix = travel_time_matrix.to_dict(orient='records')

    logger.info('Completing %s for %s', mode, name)

    return travel_time_matrix
