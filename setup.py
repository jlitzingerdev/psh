"""
Copyright 2019 Jason Litzinger
"""

from setuptools import setup, find_packages

setup(
    name="psh",
    version="0.1.0",
    description="A project for manipulating setup.py",
    author="Jason Litzinger",
    author_email="jlitzingerdev@gmail.com",
    package_dir={"": "src"},
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="dependency setuptools development",
    packages=find_packages(where="src"),
    install_requires=["click", "attrs"],
    extras_require={"dev": ["pylint", "pytest", "coverage", "black"]},
    entry_points={"console_scripts": ["psh=psh:cli"]},
)
