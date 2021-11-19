"""
This empty file will tell pytest this src/ directory is part of the PYTHONPATH.
Without it all tests won't be able to import packages in the src/ directory, hence all of them will fail.

Because we don't have an __init__.py in the src/ folder, this won't be identified as a module by the pypi setup,
hence the conftest.py file won't be part of the packaged py-bot-starter
"""
