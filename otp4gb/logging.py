"""
``otp4gb.logging`` -- Common logging config
--------------------------------------------
"""

import logging
import os
import sys

from otp4gb.config import LOG_DIR

FORMAT_STRING = '%(asctime)s.%(msecs)03d:%(levelname)s:%(processName)s:%(module)s:%(message)s'

logging.basicConfig(format=FORMAT_STRING,
                    datefmt='%H:%M:%S')

flat_formatter = logging.Formatter(FORMAT_STRING, '%H:%M:%S')

stderr_handler = logging.StreamHandler(stream=sys.stderr)
stderr_handler.setFormatter(flat_formatter)


def file_handler_factory(filename, dir=LOG_DIR, level=logging.INFO):
    if not os.path.exists(dir):
        os.makedirs(dir)
    handler = logging.FileHandler(os.path.join(dir, filename), mode='w')
    handler.setFormatter(flat_formatter)
    handler.setLevel(level)
    return handler


def get_logger(*args, **kwargs):
    logger = logging.getLogger(*args, **kwargs)
    return logger
