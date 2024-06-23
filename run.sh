#!/bin/bash
apt-get update &&
echo "Installing apt-utils..."
apt-get install -y apt-utils &&

# Install the zbar library
echo "Installing libzbar0..."
apt-get install -y libzbar0 &&

# Install the cv2 library
echo "Installing cv2..."
apt-get install ffmpeg libsm6 libxext6  -y

# Install waitress using apt
echo "Installing python-waitress..."
apt-get install -y python-waitress &&

# Install pip if not already installed
echo "Installing python3-pip..."
apt-get install -y python3-pip &&

# Install Python packages from requirements.txt
echo "Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt &&

gunicorn --bind=0.0.0.0 --timeout 600 app:app
