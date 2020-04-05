#!/bin/bash -

virtualenv --python=/usr/bin/python3 dev
source dev/bin/activate
pip3 install -r requirements.txt
apt-get install google-chrome-stable
mkdir drivers
wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip
export PATH="./drivers:$PATH"
#nohup xvfb-run -a ./chromedriver &
#python main.py
