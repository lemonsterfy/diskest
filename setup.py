from setuptools import setup, find_packages
import os

# Read the contents from README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    required = f.read().splitlines()

# Read dev requirements from requirements-dev.txt
with open("requirements-dev.txt") as f:
    dev_required = f.read().splitlines()
    # Remove any reference to requirements.txt
    dev_required = [req for req in dev_required if not req.startswith("-r ")]

setup(
    name="diskest",
    version="0.1.0",
    author="lemonsterfy",
    author_email="lemonsterfy@gmail.com",
    description="Advanced Disk Benchmark Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lemonsterfy/diskest",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=required,
    extras_require={
        "dev": dev_required,
    },
    entry_points={
        "console_scripts": [
            "diskest=diskest.cli.commands:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "diskest": ["data/*.yaml"],
    },
)
