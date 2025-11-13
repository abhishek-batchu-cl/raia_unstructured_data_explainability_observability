"""Setup script for RAIA Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="raia",
    version="1.0.0",
    author="RAIA Team",
    author_email="raia@example.com",
    description="Responsible AI Analytics & Agent Evaluation - Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raia/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiofiles>=23.0.0",
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "kafka": ["aiokafka>=0.10.0"],
        "langchain": ["langchain>=0.1.0"],
        "otlp": ["opentelemetry-api>=1.20.0", "opentelemetry-sdk>=1.20.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "ruff>=0.1.0",
        ],
    },
)
