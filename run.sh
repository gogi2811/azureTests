#!/bin/bash
apt-get update &&
apt-get install -y apt-utils &&
apt-get install libzbar0
python -m waitress-serve --listen=*:8000 app:app
