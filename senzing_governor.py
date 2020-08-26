#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# governor.py
# -----------------------------------------------------------------------------

import logging
import os
import psycopg2
import string
import threading
import time
from urllib.parse import urlparse

__all__ = []
__version__ = "1.0.0"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2020-08-26'
__updated__ = '2020-08-26'

SENZING_PRODUCT_ID = "5017"  # See https://github.com/Senzing/knowledge-base/blob/master/lists/senzing-product-ids.md
log_format = '%(asctime)s %(message)s'

# Lists from https://www.ietf.org/rfc/rfc1738.txt

safe_character_list = ['$', '-', '_', '.', '+', '!', '*', '(', ')', ',', '"'] + list(string.ascii_letters)
unsafe_character_list = ['"', '<', '>', '#', '%', '{', '}', '|', '\\', '^', '~', '[', ']', '`']
reserved_character_list = [';', ',', '/', '?', ':', '@', '=', '&']


class Governor:

    # -------------------------------------------------------------------------
    # Interior methods for database URL parsing
    # -------------------------------------------------------------------------

    def translate(self, map, astring):
        new_string = str(astring)
        for key, value in map.items():
            new_string = new_string.replace(key, value)
        return new_string

    def get_unsafe_characters(self, astring):
        result = []
        for unsafe_character in unsafe_character_list:
            if unsafe_character in astring:
                result.append(unsafe_character)
        return result

    def get_safe_characters(self, astring):
        result = []
        for safe_character in safe_character_list:
            if safe_character not in astring:
                result.append(safe_character)
        return result

    def parse_database_url(self, original_senzing_database_url):
        ''' Given a canonical database URL, decompose into URL components. '''

        result = {}

        # Get the value of SENZING_DATABASE_URL environment variable.

        senzing_database_url = original_senzing_database_url

        # Create lists of safe and unsafe characters.

        unsafe_characters = self.get_unsafe_characters(senzing_database_url)
        safe_characters = self.get_safe_characters(senzing_database_url)

        # Detect an error condition where there are not enough safe characters.

        if len(unsafe_characters) > len(safe_characters):
            logging.error(message_error(730, unsafe_characters, safe_characters))
            return result

        # Perform translation.
        # This makes a map of safe character mapping to unsafe characters.
        # "senzing_database_url" is modified to have only safe characters.

        translation_map = {}
        safe_characters_index = 0
        for unsafe_character in unsafe_characters:
            safe_character = safe_characters[safe_characters_index]
            safe_characters_index += 1
            translation_map[safe_character] = unsafe_character
            senzing_database_url = senzing_database_url.replace(unsafe_character, safe_character)

        # Parse "translated" URL.

        parsed = urlparse(senzing_database_url)
        schema = parsed.path.strip('/')

        # Construct result.

        result = {
            'user': self.translate(translation_map, parsed.username),
            'password': self.translate(translation_map, parsed.password),
            'host': self.translate(translation_map, parsed.hostname),
            'port': self.translate(translation_map, parsed.port),
            'dbname': self.translate(translation_map, schema),
        }

        # Return result.

        return result

    # -------------------------------------------------------------------------
    # Internal methods.
    # -------------------------------------------------------------------------

    def get_current_watermark(self, connection, database_name):

        connection.execute(self.sql_stmt, [database_name])
        result = connection.fetchone()[0]
        return result

    # -------------------------------------------------------------------------
    # Public API methods.
    #  - govern()
    #  - cleanup()
    # -------------------------------------------------------------------------

    def __init__(self, g2_engine=None, hint=None, *args, **kwargs):

        # Store parameters in instance variables.

        self.g2_engine = g2_engine
        self.hint = hint

        # Configure logging.

        log_format = '%(asctime)s %(message)s'
        logging.basicConfig(format=log_format, level=logging.INFO)
        logging.info("Using governor-postgresql-transaction-id Governor. Version: {0} Updated: {1}".format(__version__, __updated__))

        # Instance variables.

        list_seperator = os.getenv("SENZING_GOVERNOR_LIST_SEPARATOR", ',')
        self.counter = 0
        self.counter_lock = threading.Lock()
        self.high_watermark = int(os.getenv("SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK", 1000000000))
        self.low_watermark = int(os.getenv("SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK", max(self.high_watermark - 100000000, 0)))
        self.sleep_time = int(os.getenv("SENZING_GOVERNOR_SLEEP", 15))
        self.sql_stmt = "SELECT age(datfrozenxid) FROM pg_database WHERE datname = (%s);"
        self.stride = int(os.getenv("SENZING_GOVERNOR_STRIDE", 500))

        # Make a list of database SQL connection string

        sql_connections = os.getenv("SENZING_GOVERNOR_SQL_CONNECTIONS", "")
        self.sql_connection_strings = sql_connections.split(list_seperator)

        # Make database connections.

        self.database_connections = {}
        for database_connection_string in self.sql_connection_strings:

            parsed_database_url = self.parse_database_url(database_connection_string)
            connection = psycopg2.connect(**parsed_database_url)
            connection.set_session(autocommit=True, isolation_level='READ UNCOMMITTED', readonly=True)
            cursor = connection.cursor()

            self.database_connections[database_connection_string] = {
                'parsed_database_url': parsed_database_url,
                'connection': connection,
                'cursor': cursor,
            }

    def govern(self, *args, **kwargs):
        """
        Do the actual "governing".
        Do not return until the governance has been completed.
        The caller of govern() waits synchronously.
        """

        # counter_lock serialized threads.

        with self.counter_lock:
            self.counter += 1

            # Only make expensive check after N (stride) records have been read.

            if self.counter % self.stride == 0:
                logging.info("senzing-{0}0000I Governor is checking PostgreSQL Transaction IDs after {1} inserts.".format(SENZING_PRODUCT_ID, self.counter))

                # Go through each database connection to determine if watermark is above high_watermark.

                for database_connection in self.database_connections.values():

                    print(database_connection)

                    connection = database_connection.get("cursor")
                    database_name = database_connection.get("parsed_database_url", {}).get("dbname")
                    watermark = self.get_current_watermark(connection, database_name)
                    if watermark > self.high_watermark:

                        # Wait until watermark is below low_watermark.

                        while watermark > self.low_watermark:
                            logging.info("senzing-{0}0000I Governor waiting for watermark to go from {1} to {2}.".format(SENZING_PRODUCT_ID, watermark, self.low_watermark))
                            time.sleep(self.sleep_time)
                            watermark = self.get_current_watermark(connection, database_name)

    def cleanup(self, *args, **kwargs):
        '''  Tasks to perform when shutting down, e.g., close DB connections '''

        for database_connection in self.database_connections:
            database_connection.get('cursor').close()
            database_connection.get('connection').close()
        return


if __name__ == '__main__':
    pass
