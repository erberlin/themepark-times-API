from setuptools import setup

setup(
    name="data_access",
    version="0.1.1",
    description="DB access package for themepark-times-API project.",
    author="Erik R Berlin",
    author_email="erberlin.dev@gmail.com",
    license="MIT",
    packages=["data_access"],
    install_requires=["redis"],
)
