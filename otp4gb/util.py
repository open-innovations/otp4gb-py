"""
``otp4gb.util`` -- Utilities
---------------------------------------------
"""

import datetime
import time


class Timer:
    def __init__(self):
        self.tic = time.perf_counter()

    def __str__(self) -> str:
        toc = time.perf_counter()
        return str(datetime.timedelta(seconds=(toc - self.tic)))


def chunker(input_list, chunk_size=100):
    return [input_list[i:i+chunk_size] for i in range(0, len(input_list), chunk_size)]
