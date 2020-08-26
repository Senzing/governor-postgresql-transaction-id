#! /usr/bin/env python3

import logging
import time
import os
import threading

import senzing_governor
from senzing_governor import Governor

__all__ = []
__version__ = "1.0.0"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2020-08-26'
__updated__ = '2020-08-26'

log_format = '%(asctime)s %(message)s'

# -----------------------------------------------------------------------------
# Class: ExampleThread
# -----------------------------------------------------------------------------


class ExampleThread(threading.Thread):

    def __init__(self, governor, counter_max):
        threading.Thread.__init__(self)
        self.counter = 0
        self.counter_max = counter_max
        self.governor = governor

    def run(self):
        while self.counter < self.counter_max:
            self.counter += 1
            self.governor.govern()
            logging.info("{0}".format(threading.current_thread().name))

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------


if __name__ == '__main__':

    # Configure logging.

    log_level = logging.INFO
    logging.basicConfig(format=log_format, level=log_level)
    logging.info("Governor file: {0}".format(senzing_governor.__file__))

    # Create Governor.

    governor = Governor(hint="Tester")

    # Create threads.

    threads = []
    for i in range(0, 5):
        thread = ExampleThread(governor, 1000)
        thread.name = "{0}-thread-{1}".format(ExampleThread.__name__, i)
        threads.append(thread)

    # Start threads.

    for thread in threads:
        thread.start()

    # Collect inactive threads.

    for thread in threads:
        thread.join()

    # Done with Governor.

    governor.close()
