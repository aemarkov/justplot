#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name='JustPlot',
    version='0.1',
    license='MIT',
    description='Simplt data plotter with GUI',
    author='Markov Alex',
    author_email='markovalex95@gmail.com',
    packages=setuptools.find_packages(),
    scripts=['justplot'],
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'PyQt5',
        'pyqtgraph',
        'pandas',
        'numpy'
    ],
)