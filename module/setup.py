#!/usr/bin/python
import setuptools

setuptools.setup(
    name="melopero_samm8q",
    version="0.1.0",
    description="A module to easily access samm8q gps features",
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
    install_requires=["melopero_ubx", "smbus2>=0.4"]
)
