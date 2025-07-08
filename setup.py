# setup.py
from setuptools import setup, find_packages

setup(
    name="va-assistant",
    version="1.0.0",
    description="Assistant Virtuel Conversationnel - Phase 1",
    author="VA Team",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "sentence-transformers>=2.2.2",
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.3",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "va=va_assistant.main:app",
        ],
    },
    python_requires=">=3.13",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13",
    ],
)