"""
Setup configuration for nano-stochastic-model package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nano-stochastic-model",
    version="0.1.0",
    author="Based on Dr. Matthew Celnik's PhD thesis",
    description="Stochastic population balance model for nano-particulate formation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/nano-stochastic-model",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.4",
            "pytest-cov>=2.12.0",
        ],
    },
)
