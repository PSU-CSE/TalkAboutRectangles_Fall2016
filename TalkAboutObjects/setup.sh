#!/bin/bash -e

echo "Start installation. It may take more than 10 mins"
pip install --upgrade pip
pip install colorama
pip install colormath
pip install configparser
pip install decorator
pip install Django
pip install nltk
pip install numpy
pip install python-dateutil
pip install scikit-learn
pip install scipy
pip install sklearn
pip install utils
pip install virtualenv
pip install virtualenvwrapper
python DjangoDB/manage.py migrate
