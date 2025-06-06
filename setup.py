from setuptools import setup, find_packages

setup(
    name="bridge-tools",
    version="0.1.0",
    description="A collection of tools for analysing the game of bridge",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "lxml>=4.6.0", 
        "click>=8.0.0"
    ],
    entry_points={
        "console_scripts": [
            "bridge-analyzer=src.main:analyze",
        ],
    },
)

