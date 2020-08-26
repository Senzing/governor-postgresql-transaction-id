# governor-postgresql-transaction-id

## Synopsis

`senzing_governor.py` contains a `Governor` class that can be used to govern the behavior of
programs like:

1. [stream-loader.py](https://github.com/Senzing/stream-loader/blob/master/stream-loader.py)
1. [redoer.py](https://github.com/Senzing/redoer/blob/master/redoer.py)

when used with PostgreSQL database.

## Overview

The `senzing_governor.py` in this repository monitors the age of the PostgreSQL Transaction IDs
to determine when to pass back control to the caller.

Essentially it does the following SQL statement:

```sql
SELECT age(datfrozenxid) FROM pg_database WHERE datname = (%s);
```

If the age is greater than a high-watermark,
[SENZING_GOVERNOR_POSTGRESQL_HIGH_WATERMARK](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_governor_postgresql_high_watermark),
then the Governor waits until the watermark recedes to a low-watermark,
[SENZING_GOVERNOR_POSTGRESQL_LOW_WATERMARK](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_governor_postgresql_low_watermark),

The lowering of the watermark must be done manually by using PostgreSQL
[VACUUM](https://www.postgresql.org/docs/current/sql-vacuum.html).

### Contents

1. [Preamble](#preamble)
    1. [Legend](#legend)
1. [Expectations](#expectations)
1. [Test using Command Line Interface](#test-using-command-line-interface)
    1. [Prerequisites for CLI](#prerequisites-for-cli)
    1. [Download](#download)
    1. [Environment variables for CLI](#environment-variables-for-cli)
    1. [Run command](#run-command)
1. [Develop](#develop)
    1. [Prerequisites for development](#prerequisites-for-development)
    1. [Clone repository](#clone-repository)
1. [Examples](#examples)
    1. [Examples of CLI](#examples-of-cli)
1. [Advanced](#advanced)
    1. [Configuration](#configuration)
1. [Errors](#errors)
1. [References](#references)

## Preamble

At [Senzing](http://senzing.com),
we strive to create GitHub documentation in a
"[don't make me think](https://github.com/Senzing/knowledge-base/blob/master/WHATIS/dont-make-me-think.md)" style.
For the most part, instructions are copy and paste.
Whenever thinking is needed, it's marked with a "thinking" icon :thinking:.
Whenever customization is needed, it's marked with a "pencil" icon :pencil2:.
If the instructions are not clear, please let us know by opening a new
[Documentation issue](https://github.com/Senzing/template-python/issues/new?template=documentation_request.md)
describing where we can improve.   Now on with the show...

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
  - [PostgreSQL](https://github.com/Senzing/knowledge-base/blob/master/WHATIS/postgresql.md)

## Test using Command Line Interface

### Prerequisites for CLI

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. Install system dependencies:
    1. Use `apt` based installation for Debian, Ubuntu and
       [others](https://en.wikipedia.org/wiki/List_of_Linux_distributions#Debian-based)
        1. See [apt-packages.txt](src/apt-packages.txt) for list
    1. Use `yum` based installation for Red Hat, CentOS, openSuse and
       [others](https://en.wikipedia.org/wiki/List_of_Linux_distributions#RPM-based).
        1. See [yum-packages.txt](src/yum-packages.txt) for list
1. Install Python dependencies:
    1. See [requirements.txt](requirements.txt) for list
        1. [Installation hints](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-python-dependencies.md)

### Download

1. Get a local copy of
   [senzing_governor.py](senzing_governor.py).
   Example:

    1. :pencil2: Specify where to download files.
       Example:

        ```console
        export SENZING_PROJECT_DIR=~/test-governor
        ```

    1. Make project directory.
       Example:

        ```console
        mkdir -p ${SENZING_PROJECT_DIR}
        ```

    1. Download files.
       Example:

        ```console
        curl -X GET \
          --output ${SENZING_PROJECT_DIR}/senzing_governor.py \
          https://raw.githubusercontent.com/Senzing/governor-postgresql-transaction-id/master/senzing_governor.py

        curl -X GET \
          --output ${SENZING_PROJECT_DIR}/senzing_governor_tester.py \
          https://raw.githubusercontent.com/Senzing/governor-postgresql-transaction-id/master/senzing_governor_tester.py

        curl -X GET \
          --output ${SENZING_PROJECT_DIR}/senzing_governor_tester_context_manager.py \
          https://raw.githubusercontent.com/Senzing/governor-postgresql-transaction-id/master/senzing_governor_tester_context_manager.py
        ```

1. :thinking: **Alternative:** The entire git repository can be downloaded by following instructions at
   [Clone repository](#clone-repository)

### Environment variables for CLI

1. Update `PYTHONPATH`.
   Example:

    ```console
    export PYTHONPATH=${PYTHONPATH}:${SENZING_PROJECT_DIR}
    ```

1. Identify PostgreSQL database.
   Example:

    ```console
    export SENZING_GOVERNOR_SQL_CONNECTIONS=postgresql://postgres:postgres@localhost:5432/G2
    ```

### Run command

1. Run the command.
   Example:

   ```console
   ${SENZING_PROJECT_DIR}/senzing_governor_tester.py
   ```

1. For more examples of use, see [Examples of CLI](#examples-of-cli).

## Develop

The following instructions are used when modifying and building the Docker image.

### Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [git](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-git.md)

### Clone repository

For more information on environment variables,
see [Environment Variables](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md).

1. Set these environment variable values:

    ```console
    export GIT_ACCOUNT=senzing
    export GIT_REPOSITORY=governor-postgresql-transaction-id
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

1. Using the environment variables values just set, follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/clone-repository.md) to install the Git repository.

## Examples

### Examples of CLI

The following examples require initialization described in
[Test using Command Line Interface](#test-using-command-line-interface).

1. Run the command that uses Python Context Manager approach.
   Example:

   ```console
   ${SENZING_PROJECT_DIR}/senzing_governor_tester_context_manager.py
   ```

## Advanced

### Configuration

Configuration values specified by environment variable or command line parameter.

- **[SENZING_GOVERNOR_SQL_CONNECTIONS](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_governor_sql_connections)**
- **[SENZING_PROJECT_DIR](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_project_dir)**

## Errors

1. See [docs/errors.md](docs/errors.md).

## References
