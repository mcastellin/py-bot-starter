# How to setup this project for development


## Setup a virtual environment

First, create and activate a new virtual environment in the `venv/` directory into the project's folder structure
```bash
python3 -m venv venv/
. ./venv/bin/activate
pip3 install --upgrade pip
pip3 install build
```

Build the `py-bot-starter` package
```bash
python3 -m build
```

The build step will generate the wheel file and `.tar.gz` archive. To test the artefacts locally, you can simply install 
the generated `py_bot_starter-*.whl` file into another virtual environment.
```bash
cd ~/my-test-project
python3 -m venv venv/
pip3 install --upgrade pip
pip3 install ~/py-bot-starter/dist/py_bot_starter-X.Y.Z-py3-none-any.whl
```

