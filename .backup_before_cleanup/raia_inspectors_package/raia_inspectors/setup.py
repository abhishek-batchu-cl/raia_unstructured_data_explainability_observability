"""
Setup script for raia-inspectors.

This is provided for backward compatibility.
Modern installations should use pyproject.toml via pip.
"""

from setuptools import setup, find_packages

setup(
    name="raia-inspectors",
    version="1.0.0",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.10",
)
