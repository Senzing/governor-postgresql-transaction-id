#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# governor.py
# -----------------------------------------------------------------------------

import logging
import time

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

        # Instance variables.

        self.counter = 0
        self.stride = 500
        self.sleep_time = 15

    def govern(self, *args, **kwargs):
        """
        Do the actual "governing".
        Do not return until the governance has been completed.
        The caller of govern() waits synchronously.
        """

        # Faux governance.  Replace with actual governance.

        self.counter += 1

        if self.counter % self.stride == 0:
            logging.info("Sample Governor is sleeping {0} seconds on record {1}. Hint: {2}. Replace the Governor class with your code.".format(self.sleep_time, self.counter, self.hint))
            time.sleep(self.sleep_time)

    def cleanup(self, *args, **kwargs):
        '''  Tasks to perform when shutting down, e.g., close DB connections '''
        return

if __name__ == '__main__':
    pass
