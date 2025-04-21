from setuptools import setup, find_packages

setup(
    name="krauler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'telethon==1.34.0',
        'PySocks==1.7.1',
        'python-dotenv==1.0.0',
        'asyncio==3.4.3',
        'pandas==2.2.1',
        'setuptools>=78.1.0'
    ],
) 