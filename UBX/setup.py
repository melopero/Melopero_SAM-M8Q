#!/usr/bin/python
import setuptools

setuptools.setup(
    name="melopero_ubx",
    version="0.0.1",
    description="A module to create and parse messages of the UBX protocol",
    url="https://github.com/melopero/Melopero_SAM-M8Q",
    author="Melopero",
    author_email="info@melopero.com",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],
)

