from setuptools import setup

setup(
    name="etl_worker",
    version="0.1.0",
    description="Retrieves data from https://api.wdpro.disney.go.com.",
    author="Erik R Berlin",
    author_email="erberlin.dev@gmail.com",
    license="MIT",
    packages=["etl_worker"],
    install_requires=["requests", "requests_cache"],
    python_requires=">=3.6",
)
