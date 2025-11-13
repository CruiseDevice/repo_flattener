"""
Setup script for repo-flattener
"""

from setuptools import setup, find_packages

setup(
    name="repo-flattener",
    version="0.2.1",
    packages=find_packages(),
    license="MIT",
    entry_points={
        'console_scripts': [
            'repo-flattener=repo_flattener.cli:main',
        ],
    },
    python_requires='>=3.6',
)