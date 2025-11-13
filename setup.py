"""
RAIA - Responsible AI Analytics & Agent Evaluation
Complete production-grade instrumentation and evaluation framework for agentic systems.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="raia",
    version="1.0.0",
    author="RAIA Contributors",
    author_email="",
    description="Complete production-grade instrumentation and evaluation framework for agentic systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/raia",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "tools", "tools.*"]),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "aiofiles>=23.0.0",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "langchain": [
            "langchain>=0.1.0",
            "langchain-core>=0.1.0",
        ],
        "langgraph": [
            "langgraph>=0.0.20",
        ],
        "kafka": [
            "aiokafka>=0.10.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
        ],
        "all": [
            "langchain>=0.1.0",
            "langchain-core>=0.1.0",
            "langgraph>=0.0.20",
            "aiokafka>=0.10.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agent evaluation monitoring observability langchain langgraph instrumentation",
    project_urls={
        "Documentation": "https://github.com/yourusername/raia",
        "Source": "https://github.com/yourusername/raia",
        "Bug Reports": "https://github.com/yourusername/raia/issues",
    },
)
