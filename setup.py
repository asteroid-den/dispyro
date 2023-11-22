import re

import setuptools

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requires = f.read().split()

with open("dispyro/__init__.py") as f:
    version = re.search(r'__version__ = "(?P<version>\d+\.\d+\.\d+)"', f.read()).group(
        "version"
    )

setuptools.setup(
    name="dispyro",
    version=version,
    author="asteroid-den",
    author_email="denbartolomee@gmail.com",
    description="Improved dispatching for Pyrogram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asteroid-den/dispyro/",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requires,
    python_requires=">=3.7",
    data_files=["requirements.txt"]
)
