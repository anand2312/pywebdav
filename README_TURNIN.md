# pywebdav

WebDAV client library in Python.
pywebdav can be used both as a library, and as a CLI.

# Installation
Requirements: Python >= 3.8

1) Clone/unzip this repository.

2) Create a virtual environment and activate it
```
python3 -m virtualenv venv
```
```
source venv/bin/activate # on Linux
.\venv\Scripts\activate # on Windows
```

3) Install requirements:
```
pip install -r requirements.txt
```
(Alternatively, if you use the Poetry package manager, it can do steps 2 and 3 for you with the `poetry install` command._)

# Usage
## As a CLI
pywebdav can be invoked as a CLI:
```
python -m pywebdav --help
```

It offers 2 commands:
1) request: Make a WebDAV request to a specified URL.
2) shell: Start a shell session. Run commands like cd, ls etc using WebDAV requests. (This is easier to use)

Run
```
python -m pywebdav request --help
python -m pywebdav shell --help
```
for detailed instructions for each command.

## As a library
pywebdav offers both synchronous and asynchronous clients, and some utility functions to parse responses.
There is a short example in the demo.py file.

# Running Tests
Tests have been implemented using the `pytest` framework.
To run the tests, run:
```
pytest
```
