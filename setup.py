from setuptools import setup, find_packages


setup(
    name = "execution_engine",
    packages=find_packages(where='execution_engine', include=["interface", "core"]),
    package_dir={"": "execution_engine"},
    version='1.0.0'
)
