"""Setup configuration for rag_module package."""

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent
if here.name == "rag_module":
    packages = ["rag_module"] + [f"rag_module.{p}" for p in find_packages()]
else:
    packages = find_packages()

setup(
    name="rag_module",
    version="0.1.0",
    description="RAG module for semantic search with ChromaDB and OpenAI",
    author="Rahimov Imran",
    author_email="mr.rahimov.imran@gmail.com",
    packages=packages,
    python_requires=">=3.11,<4.0",
    install_requires=[
        "numpy>=2.3.4",
        "chromadb>=1.3.4",
        "openai>=2.7.1",
        "langchain>=1.0.5",
        "langchain-core>=1.0.4",
        "langchain-community>=0.4.1",
        "langchain-chroma>=1.0.0",
        "langchain-openai>=1.0.2",
        "tiktoken>=0.12.0",
        "python-dotenv>=1.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.2",
            "pytest-asyncio>=0.23.7",
            "pytest-mock>=3.15.1",
            "pytest-cov>=6.0.0",
            "ruff>=0.7.1",
            "mypy>=1.11.2",
            "black>=24.10.0",
        ],
    },
)
