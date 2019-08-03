#!/bin/sh

./setup.py sdist
pip uninstall -y rtk-lookup
pip install dist/rtk-lookup-0.1.0.tar.gz
