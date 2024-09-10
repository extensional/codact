from setuptools import setup, find_packages

setup(
    name="codact",
    version="0.01",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'codact=codact.main:main',
        ],
    },
)