#!/usr/bin/env python

from setuptools import setup, find_packages

with open('readme.md') as readme_file:
    readme = readme_file.read()
    setup(
        name='rtk-lookup',
        version='0.1.0',
        author='Kilian Lieret',
        description="A command line program that helps looking up kanji in James Heisig's book",
        license='AGPLv3.0+',
        long_description=readme,
        long_description_content_type='text/markdown',
        url='https://github.com/klieret/kanji-lookup',
        packages=find_packages(),
        python_requires='>=3.5',
        include_package_data=True,
        entry_points={
            'console_scripts': ['rtk = rtklookup.lookup:main']
        }
    )
