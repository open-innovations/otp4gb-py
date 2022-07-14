"""
``otp4gb.gtfs_filter`` -- Invoke ``gtfs_filter``
---------------------------------------------------
"""
import logging
import operator
import os
import shutil
import subprocess

from otp4gb.config import BIN_DIR, ASSET_DIR, PREPARE_MAX_HEAP

logger = logging.getLogger(__name__)


def filter_gtfs_files(gtfs_files, output_dir, date=None, extents=None):
    location = ":".join([str(x) for x in operator.itemgetter(
        'min_lat', 'min_lon', 'max_lat', 'max_lon')(extents)])
    logger.debug(location)

    timetable_files = [os.path.join(ASSET_DIR, f)
                       for f in gtfs_files]

    for timetable_file in timetable_files:
        gtfs_filter(timetable_file,
                    output_dir=output_dir,
                    location_filter=location,
                    date_filter=date
                    )


def gtfs_filter(timetable_file, output_dir, location_filter, date_filter):
    logger.debug(timetable_file)
    temp_folder = 'zip_tmp'
    jar_file = os.path.join(BIN_DIR, 'gtfs-filter-0.1.jar')

    name_base = os.path.splitext(os.path.basename(timetable_file))[0]
    logger.info('Processing GTFS file %s', name_base)
    output_file = os.path.join(output_dir, name_base + '_filtered')

    command = [
        'java',
        '-Xmx{}'.format(PREPARE_MAX_HEAP),
        '-jar', jar_file,
        timetable_file,
        '-d', date_filter,
        '-l', location_filter,
        '-o', temp_folder
    ]

    logger.debug(command)
    subprocess.run(' '.join(command), shell=True)
    shutil.make_archive(output_file, 'zip', temp_folder)
    shutil.rmtree(temp_folder)
