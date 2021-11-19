from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    install_requires=[
        "certifi==2021.10.8",
        "charset-normalizer==2.0.7; python_version >= '3'",
        "idna==3.3; python_version >= '3'",
        "pymongo==3.12.1",
        "pytelegrambotapi==4.2.0",
        "requests==2.26.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "urllib3==1.26.7; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
    ],
    name="py-bot-starter",
    version="0.0.0",
    author="Manuel Castellin",
    author_email="manuel@castellinconsulting.com",
    description="A Telegram bot framework to implement and deploy a bot in minutes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcastellin/py-bot-starter",
    project_urls={
        "Bug Tracker": "https://github.com/mcastellin/py-bot-starter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
)
