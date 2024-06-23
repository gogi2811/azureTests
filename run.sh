#!/bin/bash
apt-get update &&
echo "Installing apt-utils..."
apt-get install -y apt-utils &&

# Install the zbar library
echo "Installing libzbar0..."
apt-get install -y libzbar0 &&

# Install waitress using apt
echo "Installing python-waitress..."
apt-get install -y python-waitress &&

# Install pip if not already installed
echo "Installing python3-pip..."
apt-get install -y python3-pip &&

# Install Python packages from requirements.txt
echo "Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt &&

python -m waitress-serve --listen=*:8000 app:app
