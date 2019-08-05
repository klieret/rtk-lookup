#!/usr/bin/env python

from setuptools import setup, find_packages

with open('readme.md') as readme_file:
    readme = readme_file.read()
    setup(
        name='rtk-lookup',
        version='0.1.0',
        author='Kilian Lieret',
        author_email='kilian.lieret@arcor.de',
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
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: OS Independent",
        ]
    )
