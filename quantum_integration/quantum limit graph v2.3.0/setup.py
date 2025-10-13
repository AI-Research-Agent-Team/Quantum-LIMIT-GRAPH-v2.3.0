# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Setup script for Quantum LIMIT-GRAPH v2.3.0
"""

from setuptools import setup, find_packages
import os

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='quantum-limit-graph',
    version='2.3.0',
    author='AI Research Agent Team',
    author_email='contact@example.com',
    description='Multilingual Quantum Research Agent with LIMIT-GRAPH Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/quantum-limit-graph',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'quantum-limit-graph=sample_quantum_limit-graph:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
