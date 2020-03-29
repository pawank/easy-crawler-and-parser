#!/bin/bash -

virtualenv --python=/usr/bin/python3 dev
source dev/bin/activate
pip3 install -r requirements.txt
#python main.py
