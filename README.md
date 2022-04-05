# pywebdav

WebDAV client library in Python.

# Installation
pywebdav can be installed with pip:
```
pip install git+https://github.com/anand2312/pywebdav.git
```

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
