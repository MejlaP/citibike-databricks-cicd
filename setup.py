from setuptools import setup, find_packages

setup(
    name="dab_project", # Name of the package as it will be installed (pip show dab_project)
    version="0.0.2",  # Package version — bump this when the code changes and is redistributed
    description="This contains the code in the ./src directory of project",
    author="Milos",
    packages=find_packages(where="./src"),  # Auto-discover all packages (folders with __init__.py) under src/
    package_dir={"": "./src"},  # Tells setuptools that the package root is "src/", not the project root —
                                # so "citibike" and "utils" are found as top-level packages inside src/
    install_requires=["setuptools"] # Dependencies needed for this package to work (just setuptools itself here)
)