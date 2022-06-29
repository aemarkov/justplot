#!/usr/bin/env python3

import setuptools
from pathlib import Path

# The text of the README file
README = Path('README.md').read_text()

setuptools.setup(
    name='justplot-qt',
    version='0.2.0',
    description='Simplt data plotter with GUI',
    long_description_content_type='text/markdown',
    long_description=README,
    url='https://github.com/Garrus007/justplot',
    author='Markov Alex',
    author_email='markovalex95@gmail.com',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 5 - Production/Stable"
    ],
    license='MIT',
    packages=setuptools.find_packages(),
    scripts=['justplot'],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'PyQt5',
        'pyqtgraph',
        'pandas'
    ],
)
