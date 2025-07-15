# governor-postgresql-transaction-id

## Synopsis

`senzing_governor.py` contains a `Governor` class that can be used to govern the behavior of
programs like:

1. [stream-loader.py]
1. [redoer.py]

when used with PostgreSQL database.

## Overview

The `senzing_governor.py` in this repository monitors the age of the PostgreSQL Transaction IDs
to determine when to pass back control to the caller.

Essentially it does the following SQL statement:

```sql
SELECT age(datfrozenxid) FROM pg_database WHERE datname = (%s);
```

If the age is greater than a high-watermark, [SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK],
then the Governor waits until the watermark recedes to a low-watermark,
[SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK].

The lowering of the watermark must be done manually by using PostgreSQL
[VACUUM](https://www.postgresql.org/docs/current/sql-vacuum.html).

### Contents

1. [Preamble]
   1. [Legend]
1. [Expectations]
1. [Test using Command Line Interface]
   1. [Prerequisites for CLI]
   1. [Download]
   1. [Environment variables for CLI]
   1. [Run command]
1. [Configuration]
1. [References]

## Preamble

At [Senzing], we strive to create GitHub documentation in a
"[don't make me think]" style. For the most part, instructions are copy and paste.
Whenever thinking is needed, it's marked with a "thinking" icon :thinking:.
Whenever customization is needed, it's marked with a "pencil" icon :pencil2:.
If the instructions are not clear, please let us know by opening a new
[Documentation issue] describing where we can improve. Now on with the show...

### Legend

1. :thinking: - A "thinker" icon means that a little extra thinking may be required.
   Perhaps there are some choices to be made.
   Perhaps it's an optional step.
1. :pencil2: - A "pencil" icon means that the instructions may need modification before performing.
1. :warning: - A "warning" icon means that something tricky is happening, so pay attention.

## Expectations

- **Space:** This repository and demonstration require 10 KB free disk space.
- **Time:** Budget 20 minutes to get the demonstration up-and-running, depending on CPU and network speeds.
- **Background knowledge:** This repository assumes a working knowledge of:
  - [PostgreSQL]

## Test using Command Line Interface

### Prerequisites for CLI

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. Install system dependencies:
   1. Use `apt` based installation for [Debian, Ubuntu and others]
      1. See [apt-packages.txt] for list
   1. Use `yum` based installation for [Red Hat, CentOS, openSuse and others].
      1. See [yum-packages.txt] for list
1. Install Python dependencies:
   1. See [requirements.txt] for list
      1. [Installation hints]

### Download

1. Get a local copy of [senzing_governor.py] and programs that test the governor.

   1. :pencil2: Specify a director of where to download files.
      Example:

      ```console
      export SENZING_GOVERNOR_PROJECT_DIR=~/test-governor
      ```

   1. Make project directory.
      Example:

      ```console
      mkdir -p ${SENZING_GOVERNOR_PROJECT_DIR}
      ```

   1. Download files.
      Example:

      ```console
      curl -X GET \
        --output ${SENZING_GOVERNOR_PROJECT_DIR}/senzing_governor.py \
        https://raw.githubusercontent.com/Senzing/governor-postgresql-transaction-id/main/src/senzing_governor.py

      curl -X GET \
        --output ${SENZING_GOVERNOR_PROJECT_DIR}/senzing_governor_tester.py \
        https://raw.githubusercontent.com/Senzing/governor-postgresql-transaction-id/main/src/senzing_governor_tester.py

      chmod +x ${SENZING_GOVERNOR_PROJECT_DIR}/senzing_governor_tester.py

      curl -X GET \
        --output ${SENZING_GOVERNOR_PROJECT_DIR}/senzing_governor_tester_context_manager.py \
        https://raw.githubusercontent.com/Senzing/governor-postgresql-transaction-id/main/src/senzing_governor_tester_context_manager.py

      chmod +x ${SENZING_GOVERNOR_PROJECT_DIR}/senzing_governor_tester_context_manager.py
      ```

1. :thinking: **Alternative:** The entire git repository can be downloaded by following instructions at
   [Clone repository]

### Environment variables for CLI

1. Update `PYTHONPATH`.
   Example:

   ```console
   export PYTHONPATH=${PYTHONPATH}:${SENZING_GOVERNOR_PROJECT_DIR}
   ```

1. :pencil2: Identify PostgreSQL database.
   The format of the URL can be seen at [SENZING_DATABASE_URL]
   Example:

   ```console
   export SENZING_GOVERNOR_DATABASE_URLS=postgresql://postgres:postgres@localhost:5432/G2
   ```

   1. :thinking: **Optional:** Multiple databases can be specified in a list.
      Example:

      ```console
      export SENZING_GOVERNOR_DATABASE_URLS=postgresql://postgres:postgres@localhost:5432/G2,postgresql://postgres:postgres@localhost:5432/G2-RES
      ```

   1. :thinking: **Optional:** The comma is used as a list item separator. If a different separator is needed it can be specified.
      Example:

      ```console
      export SENZING_GOVERNOR_LIST_SEPARATOR="+"
      export SENZING_GOVERNOR_DATABASE_URLS="postgresql://postgres:postgres@localhost:5432/G2+postgresql://postgres:postgres@localhost:5432/G2-RES"
      ```

### Run command

1. Run the command.
   Example:

   ```console
   ${SENZING_GOVERNOR_PROJECT_DIR}/senzing_governor_tester.py
   ```

1. For more examples of use, see [Examples of CLI].

## Configuration

Configuration values specified by environment variable or command line parameter.

- **[SENZING_GOVERNOR_DATABASE_URLS]**
- **[SENZING_GOVERNOR_INTERVAL]**
- **[SENZING_GOVERNOR_LIST_SEPARATOR]**
- **[SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK]**
- **[SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK]**
- **[SENZING_GOVERNOR_PROJECT_DIR]**
- **[SENZING_GOVERNOR_WAIT]**

## References

- [Development]
- [Errors]
- [Examples]

[apt-packages.txt]: packages/apt-packages.txt
[Clone repository]: docs/development.md#clone-repository
[Configuration]: #configuration
[Debian, Ubuntu and others]: https://en.wikipedia.org/wiki/List_of_Linux_distributions#Debian-based
[Development]: docs/development.md
[Documentation issue]: https://github.com/Senzing/template-python/issues/new?template=documentation_request.md
[don't make me think]: https://github.com/Senzing/knowledge-base/blob/main/WHATIS/dont-make-me-think.md
[Download]: #download
[Environment variables for CLI]: #environment-variables-for-cli
[Errors]: docs/errors.md
[Examples of CLI]: docs/examples.md#examples-of-cli
[Examples]: docs/examples.md
[Expectations]: #expectations
[Installation hints]: https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-python-dependencies.md
[Legend]: #legend
[PostgreSQL]: https://github.com/Senzing/knowledge-base/blob/main/WHATIS/postgresql.md
[Preamble]: #preamble
[Prerequisites for CLI]: #prerequisites-for-cli
[Red Hat, CentOS, openSuse and others]: https://en.wikipedia.org/wiki/List_of_Linux_distributions#RPM-based
[redoer.py]: https://github.com/Senzing/redoer/blob/main/redoer.py
[References]: #references
[requirements.txt]: requirements.txt
[Run command]: #run-command
[SENZING_DATABASE_URL]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_database_url
[SENZING_GOVERNOR_DATABASE_URLS]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_database_urls
[SENZING_GOVERNOR_INTERVAL]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_interval
[SENZING_GOVERNOR_LIST_SEPARATOR]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_list_separator
[SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_high_watermark
[SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_postgresql_high_watermark
[SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_low_watermark
[SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_postgresql_low_watermark
[SENZING_GOVERNOR_PROJECT_DIR]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_project_dir
[SENZING_GOVERNOR_WAIT]: https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_governor_wait
[senzing_governor.py]: src/senzing_governor.py
[Senzing]: https://senzing.com
[stream-loader.py]: https://github.com/Senzing/stream-loader/blob/main/stream-loader.py
[Test using Command Line Interface]: #test-using-command-line-interface
[yum-packages.txt]: packages/yum-packages.txt
