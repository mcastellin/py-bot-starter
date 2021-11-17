import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-bot-starter",
    version="0.0.2",
    author="Manuel Castellin",
    author_email="castellin.manuel@gmail.com",
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
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
