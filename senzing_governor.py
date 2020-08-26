#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# governor.py
# -----------------------------------------------------------------------------

import logging
import time
import os
import threading

__all__ = []
__version__ = "1.0.0"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2020-08-26'
__updated__ = '2020-08-26'

SENZING_PRODUCT_ID = "5017"  # See https://github.com/Senzing/knowledge-base/blob/master/lists/senzing-product-ids.md
log_format = '%(asctime)s %(message)s'


class Governor:

    def __init__(self, g2_engine=None, hint=None, *args, **kwargs):

        # Store parameters in instance variables.

        self.g2_engine = g2_engine
        self.hint = hint

        # Configure logging.

        log_format = '%(asctime)s %(message)s'
        logging.basicConfig(format=log_format, level=logging.INFO)
        logging.info("Using governor-postgresql-transaction-id Governor. Version: {0} Updated: {1}".format(__version__, __updated__))

        # Instance variables.

        self.counter = 0
        self.counter_lock = threading.Lock()
        self.sleep_time = int(os.getenv("SENZING_GOVERNOR_SLEEP", 15))
        self.stride = int(os.getenv("SENZING_GOVERNOR_STRIDE", 500))

    def govern(self, *args, **kwargs):
        """
        Do the actual "governing".
        Do not return until the governance has been completed.
        The caller of govern() waits synchronously.
        """

        # Faux governance.  Replace with actual governance.

        with self.counter_lock:
            self.counter += 1

            if self.counter % self.stride == 0:
                logging.info("Sample Governor is sleeping {0} seconds on record {1}. Hint: {2}.".format(self.sleep_time, self.counter, self.hint))
                time.sleep(self.sleep_time)

    def cleanup(self, *args, **kwargs):
        '''  Tasks to perform when shutting down, e.g., close DB connections '''
        return


if __name__ == '__main__':
    pass
