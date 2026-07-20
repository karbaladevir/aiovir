from setuptools import setup, find_packages

setup(
    name="aiovir",
    version="0.1.0",
    description="Async Python client for Virasty messenger with AES-GCM encryption",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "cryptography>=41.0.0",
        "msgpack>=1.0.0",
    ],
    extras_require={
        "proxy": ["aiohttp-socks>=0.8.0"],
    },
    python_requires=">=3.8",
)