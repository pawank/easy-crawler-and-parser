#!/bin/bash -

virtualenv --python=/usr/bin/python3 dev
source dev/bin/activate
pip3 install -r requirements.txt
export PATH="./drivers:$PATH"
#python main.py
