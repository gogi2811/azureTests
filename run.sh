#!/bin/bash
apt-get update &&
apt-get install -y apt-utils &&
apt-get install -y libzbar0 &&
apt-get install -y python-waitress &&
echo "HEllO" &&
# Install Python packages from requirements.txt
pip3 install -r requirements.txt &&
waitress-serve --listen=*:8000 app:app
