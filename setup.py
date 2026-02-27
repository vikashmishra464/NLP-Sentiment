"""Setup script for sentiment analysis package."""
from setuptools import setup, find_packages

with open("README_MLOPS.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sentiment-analysis-mlops",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MLOps-enabled sentiment analysis with transformer models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sentiment-analysis-mlops",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sentiment-train=train:main",
            "sentiment-deploy=deploy:main",
            "sentiment-monitor=src.monitoring:main",
        ],
    },
)
