from setuptools import setup, find_packages

setup(
    name="integrator",
    version="0.01",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mytool=integrator.main:main',
        ],
    },
)