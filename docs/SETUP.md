# How to setup this project for development


## Setup a virtual environment

First, create and activate a new virtual environment with pipenv
```bash
python3 -m pip install --upgrade pipenv
pipenv install --dev
```

Build the `py-bot-starter` package
```bash
pipenv run python -m build
```

The build step will generate the wheel file and `.tar.gz` archive. To test the artefacts locally, you can simply install 
the generated `py_bot_starter-*.whl` file into another virtual environment.
```bash
cd ~/my-test-project
python3 -m venv venv/
pip3 install --upgrade pip
pip3 install --force-reinstall ~/py-bot-starter/dist/py_bot_starter-X.Y.Z-py3-none-any.whl
```

## Update project requirements

We use `pipenv` and `pipenv-setup` to manage project requirements. When during development we update the content of the
`Pipfile` and `Pipfile.lock`, dependencies in the `setup.py` need to be updated too.
To do this just run `pipenv-setup sync` and commit the updated setup file in the repo:

```bash
pipenv run pipenv-setup sync
```