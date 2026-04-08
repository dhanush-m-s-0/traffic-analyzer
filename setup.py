"""Traffic Analyzer package configuration."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="traffic-analyzer",
    version="0.1.0",
    author="Traffic Analyzer Team",
    description="Comprehensive traffic analyzer powered by Agentic AI with Groq and LangChain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dhanush-m-s-0/traffic-analyzer",
    packages=find_packages(exclude=["tests*", "notebooks*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "traffic-analyzer=cli.main:cli",
        ],
    },
)
