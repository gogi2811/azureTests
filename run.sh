#!/bin/bash
apt-get update &&
apt-get install -y apt-utils &&
apt-get install libzbar0
apt-get install -y python-waitress
waitress-serve --listen=*:8000 app:app
