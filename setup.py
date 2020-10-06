"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='vqa_engine',
    version='0.0.1',
    description='VQA Question Engine',
    author='Carlos E. Jimenez',
    author_email='carlosej@cs.princeton.edu',
    packages=find_packages(),
    python_requires='>=3.7, <4',
    install_requires=[
    ],
)