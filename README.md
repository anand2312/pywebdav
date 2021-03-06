# pywebdav

WebDAV client library in Python.
pywebdav can be used both as a library, and as a CLI.

# Installation
Requirements: Python >= 3.8

All the commands must be run in the same directory as this file.

1) Create a virtual environment and activate it
```
python3 -m virtualenv venv
```
```
source venv/bin/activate # on Linux
.\venv\Scripts\activate # on Windows
```

2) Install requirements:
```
pip install -r requirements.txt
pip install -e .  # install pywebdav locally
```
Alternatively, if you use the Poetry package manager you can use:
```
poetry install
poetry shell
```
to do steps 1 and 2.

# Usage
## As a CLI
pywebdav can be invoked as a CLI:
```
python -m pywebdav --help
```

It offers 2 commands:
1) shell: Start a shell session. Run commands like cd, ls etc using WebDAV requests. (This is easier to use)
2) request: Make a WebDAV request to a specified URL.

Run
```
python -m pywebdav request --help
python -m pywebdav shell --help
```
for detailed instructions for each command.

Examples: The following commands will make requests to demo.owncloud.com \
```
python -m pywebdav shell --host demo.owncloud.com -u demo -pw demo --path remote.php/dav/files/demo
```
```
python -m pywebdav request PROPFIND https://demo.owncloud.com/remote.php/dav/files/demo -u demo -pw demo
```

**Note**: 1) Pass the `--debug` flag to the CLI commands to view more info on the requests being made. \
2) The shell does not care if you `cd` into a directory that doesn't exist; it'll raise errors when you try running some commands in a directory that doesn't exist. You can use the `mkdir` command to create a new directory, and then run
commands in it. \
3) The server gets reset every hour, so you may encounter some 404s if you use these commands at that time.

## As a library
pywebdav offers both synchronous and asynchronous clients, and some utility functions to parse responses.
There is a short example in the demo.py file.

# Running Tests
Tests have been implemented using the `pytest` framework.
To run the tests, run:
```
pytest -rxXs
```

# Navigating source code
The source code lies in the pywebdav directory, and the tests in the tests directory.
```
pywebdav
 ??? _async
 ??? ??? __init__.py
 ??? _sync
 ??? ??? __init__.py
 ??? cli.py
 ??? shell_client.py
 ??? types.py
 ??? utils.py
 ??? _unasync_compat.py
 ??? __init__.py
 ??? __main__.py
```
1) The synchronous client is automatically generated from the async client code that I write. The AsyncWebDAVClient
is in the `_async/__init__.py` file, and the generated client is in the `_sync/__init__.py` file.
The Client classes offer a general `request` method to run any sort of request, and some helper functions to run other requests:
    - propfind
    - get
    - put
    - move
    - copy

2) `types.py` contain some types that are used in the codebase. (DAVResponse, Resource etc)
3) `utils.py` contain some utility functions:
    - `response_to_resources`: To be used with a PROPFIND request; it parses the response XML into `Resource` objects
4) `cli.py` contains the code behind the CLI interface, while `shell_client.py` contains some helper methods to run the
shell commands like `ls`, `cd` etc.


Similar to the client code, the tests for the synchronous client is also automatically generated, from the tests that I
wrote for the asynchronous client. They lie in the `tests/_sync` and `tests/_async` directories respectively.

## NOTES
1) Some parts of this code has been inspired by: \
https://github.com/amnong/easywebdav \
https://github.com/owncloud/pyocclient
