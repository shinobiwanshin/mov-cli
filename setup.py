"""
mov-cli package setup.
"""

from setuptools import setup, find_packages

setup(
    name="mov-cli",
    version="1.0.0",
    description="🎬 Search and stream movies from the terminal.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="mov-cli contributors",
    url="https://github.com/mov-cli/mov-cli",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "rich>=13.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "mov-cli=mov_cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Video",
    ],
)
