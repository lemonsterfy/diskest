from setuptools import setup


def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
)
