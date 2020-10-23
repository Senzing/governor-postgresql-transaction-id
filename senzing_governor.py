#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# senzing_governor.py
#
# Class: Governor
#
# An example Senzing Governor plugin that detects transaction ID age (XID) in a
# Postgres database.  If the age is above a "high watermark",
# SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK, then the threads are paused
# until the age is less than a "low watermark",
# SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK.
# Once the XID age is below the "low watermark", the threads resume processing.
#
# XID age is reduced with the Postgres vacuum command. This example doesn't
# attempt to issue the vacuum command.  The user running the Governor may not
# have the privileges to do so. When the age threshold is detected, a manual step
# of issuing the postgres vacuum command is required.
# Reference: https://www.postgresql.org/docs/current/sql-vacuum.html
#
# This example uses the native Python Postgres driver psycopg2.
# Full details on installation: https://www.psycopg.org/docs/install.html
# --------------------------------------------------------------------------------------------------------------

import logging
import os
import psycopg2
import string
import threading
import time
import json
from urllib.parse import urlparse

__all__ = []
__version__ = "1.0.3"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2020-08-26'
__updated__ = '2020-10-23'

SENZING_PRODUCT_ID = "5017"  # See https://github.com/Senzing/knowledge-base/blob/master/lists/senzing-product-ids.md
log_format = '%(asctime)s %(message)s'

# Lists from https://www.ietf.org/rfc/rfc1738.txt

safe_character_list = ['$', '-', '_', '.', '+', '!', '*', '(', ')', ',', '"'] + list(string.ascii_letters)
unsafe_character_list = ['"', '<', '>', '#', '%', '{', '}', '|', '\\', '^', '~', '[', ']', '`']
reserved_character_list = [';', ',', '/', '?', ':', '@', '=', '&']


class Governor:

    # -------------------------------------------------------------------------
    # Internal methods for database URL parsing.
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
            logging.error("There are not enough safe characters to do the translation. Unsafe Characters: {0}; Safe Characters: {1}".format(unsafe_characters, safe_characters))
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
            'dbname': self.translate(translation_map, schema),
            'host': self.translate(translation_map, parsed.hostname),
            'password': self.translate(translation_map, parsed.password),
            'port': self.translate(translation_map, parsed.port),
            'user': self.translate(translation_map, parsed.username),
        }

        # Return result.

        return result

    # -------------------------------------------------------------------------
    # Internal methods for accessing database.
    # -------------------------------------------------------------------------

    def get_current_watermark(self, cursor, database_name):

        cursor.execute(self.sql_stmt, [database_name])
        return cursor.fetchone()[0]

    # -------------------------------------------------------------------------
    # Support for Python Context Manager.
    # -------------------------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # -------------------------------------------------------------------------
    # Public API methods.
    #  - govern()
    #  - close()
    # -------------------------------------------------------------------------

    def __init__(
        self,
        database_urls=None,
        high_watermark=1000000000,
        hint="",
        interval=100000,
        list_separator=',',
        low_watermark=200000000,
        check_time_interval_in_seconds=5,
        wait_time=60,
        *args,
        **kwargs
    ):

        logging.info("senzing-{0}0001I Using governor-postgresql-transaction-id Governor. Version: {1} Updated: {2}".format(SENZING_PRODUCT_ID, __version__, __updated__))

        # Instance variables. Precedence: 1) OS Environment variables, 2) parameters

        self.counter = 0
        self.counter_lock = threading.Lock()

        # Database connection string. Precedence: 1) SENZING_GOVERNOR_DATABASE_URLS, 2) SENZING_DATABASE_URL, 3) SENZING_ENGINE_CONFIGURATION_JSON 4) parameters
        self.database_urls = database_urls
        if os.getenv("SENZING_ENGINE_CONFIGURATION_JSON") is not None:
            config_dict = json.loads(os.getenv("SENZING_ENGINE_CONFIGURATION_JSON"))
            self.database_urls = config_dict["SQL"]["CONNECTION"]
        self.database_urls = os.getenv("SENZING_DATABASE_URL", self.database_urls)
        self.database_urls = os.getenv("SENZING_GOVERNOR_DATABASE_URLS", self.database_urls)

        self.high_watermark = int(os.getenv("SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK", high_watermark))
        self.hint = os.getenv("SENZING_GOVERNOR_HINT", hint)
        self.interval = int(os.getenv("SENZING_GOVERNOR_INTERVAL", interval))
        self.list_separator = os.getenv("SENZING_GOVERNOR_LIST_SEPARATOR", list_separator)
        self.low_watermark = int(os.getenv("SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK", low_watermark))
        self.sql_stmt = "SELECT age(datfrozenxid) FROM pg_database WHERE datname = (%s);"
        self.check_time_interval_in_seconds = int(os.getenv("SENZING_GOVERNOR_CHECK_TIME_INTERVAL_IN_SECONDS", check_time_interval_in_seconds))
        self.wait_time = int(os.getenv("SENZING_GOVERNOR_WAIT", wait_time))
        logging.info("senzing-{0}0002I SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK: {1}; SENZING_GOVERNOR_INTERVAL: {2}; SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK {3}; SENZING_GOVERNOR_WAIT: {4}; SENZING_GOVERNOR_HINT: {5}".format(SENZING_PRODUCT_ID, self.high_watermark, self.interval, self.low_watermark, self.wait_time, self.hint))

        # Synthesize variables.

        self.next_check_time = time.time() + self.check_time_interval_in_seconds

        # Make database connections.

        self.database_connections = {}
        if self.database_urls:
            sql_connection_strings = self.database_urls.split(self.list_separator)
            for database_connection_string in sql_connection_strings:

                parsed_database_url = self.parse_database_url(database_connection_string)

                # Only "postgresql://" databases are monitored.

                schema = database_connection_string.split(':')[0]
                if schema != "postgresql":
                    logging.info("senzing-{product_id}0701W SENZING_GOVERNOR_DATABASE_URLS contains a non-postgres URL:  {schema}://{user}:xxxxxxxx@{host}:{port}/{dbname}".format(product_id=SENZING_PRODUCT_ID, schema=schema, **parsed_database_url))
                    continue

                # Create connection.

                logging.info("senzing-{product_id}0003I Governor monitoring {schema}://{user}:xxxxxxxx@{host}:{port}/{dbname}".format(product_id=SENZING_PRODUCT_ID, schema=schema, **parsed_database_url))
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

        # counter_lock serializes threads.

        with self.counter_lock:
            self.counter += 1

            # Only make expensive checks after "interval" records have been read.

            if (self.counter % self.interval == 0) or (time.time() > self.next_check_time):

                # Reset timer.

                self.next_check_time = time.time() + self.check_time_interval_in_seconds

                # Go through each database connection to determine if watermark is above high_watermark.

                for database_connection in self.database_connections.values():
                    cursor = database_connection.get("cursor")
                    database_name = database_connection.get("parsed_database_url", {}).get("dbname")
                    watermark = self.get_current_watermark(cursor, database_name)
                    logging.info("senzing-{0}0004I Governor is checking PostgreSQL Transaction IDs. Database: {1}; Current XID: {2}; High watermark XID: {3}".format(SENZING_PRODUCT_ID, database_name, watermark, self.high_watermark))
                    if watermark > self.high_watermark:

                        # If above high watermark, wait until watermark is below low_watermark.

                        while watermark > self.low_watermark:
                            logging.info("senzing-{0}0005I Governor waiting {1} seconds for {2} database age(XID) to go from current value of {3} to low watermark of {4}.".format(SENZING_PRODUCT_ID, self.wait_time, database_name, watermark, self.low_watermark))
                            time.sleep(self.wait_time)
                            watermark = self.get_current_watermark(cursor, database_name)

    def close(self, *args, **kwargs):
        '''  Tasks to perform when shutting down, e.g., close DB connections '''

        for database_connection in self.database_connections.values():
            database_connection.get('cursor').close()
            database_connection.get('connection').close()
        logging.info("senzing-{0}0006I Governor closed.".format(SENZING_PRODUCT_ID))


if __name__ == '__main__':
    pass
