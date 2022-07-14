"""
``otp4gb.osmconvert`` -- Invoke ``osmconvert``
---------------------------------------------
"""

import logging
import operator
import os
import subprocess

from otp4gb.config import BIN_DIR, ROOT_DIR

logger = logging.getLogger(__name__)
DOCKER = 'OSMCONVERT_DOCKER' in os.environ


def _command(input, bounds, output):
    command = [os.path.join(BIN_DIR, 'osmconvert64.exe')]
    if DOCKER:
        output = output.replace(ROOT_DIR, '/mnt')
        input = input.replace(ROOT_DIR, '/mnt')
        command = [
            'docker', 'run', '--rm',
            '-v', '{}:/mnt'.format(ROOT_DIR),
            'phdax/osmtools',
            'osmconvert',
        ]
    args = [
        input,
        '-b={}'.format(bounds),
        '--complete-ways',
        '-o={}'.format(output),
    ]
    return command + args


def osm_convert(input, output, extents):
    bounds = ','.join([str(x) for x in operator.itemgetter(
        'min_lon', 'min_lat', 'max_lon', 'max_lat')(extents)])
    logger.debug(bounds)

    expr = _command(input, bounds, output)
    logger.info('Running osmconvert')
    logger.debug('commandline = %s', ' '.join(expr))
    subprocess.run(expr, check=True)
