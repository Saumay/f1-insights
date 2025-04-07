"""Setup file for F1 analysis utilities package."""

from setuptools import setup, find_packages

setup(
    name="f1_insights",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastf1",
        "pandas",
        "numpy",
        "matplotlib",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Utilities for F1 data analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/f1-insights",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 
