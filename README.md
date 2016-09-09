# TalkAboutRectangles_Fall2016 README #

### What is this repository for? ###

* This repository maintains the code required to run and develop the TalkAboutObjects game

### How do I get set up? ###

#### On a Mac: ####
----------------------
1. Ensure you have git installed on your mac. If you don't checkout this link for how to set it up: [How to install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. Clone this repository
3. In a terminal, navigate to the directory this readme is located in and run a "git pull" to make sure everything is up to date.
4. ensure you have python2.7 installed on your machine along with pip, the python application manager (should have both by default on a mac)
5. Check the file located at /TalkAboutObjects/DjangoDB/DjangoDB/settings.py and make sure the paramter "USE_POSTGRES" is equal to "False". This ensures you are using a local version of the database.
```USE_POSTGRES = False```
6. from within the /TalkAboutObjects directory, run "pip install -r requirements.txt" this will install all of the necessary python applications if they aren't already on your machine
7. run the following command:
```python DjangoDB/manage.py migrate```
 This will setup the sqlite database on your machine to be ready to play the game.
8. run the following from within the TalkAboutObjects directory ```./RunGame.sh```. This script begins the game for you.
9. That's all it takes, you should now be set to play the game!

#### On Windows: ####
-------------------------
1. Ensure you have git installed on your pc. If you don't checkout this link for how to set it up: [How to install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. Clone this repository
3. In a terminal, navigate to the directory this readme is located in and run a "git pull" to make sure everything is up to date.
4. Make sure you have python 2.7 installed on your machine. If you don't, there are several options to download python. Downloading Anaconda includes python 2.7 and many very useful
packages. Here's the link to download Anaconda: https://www.continuum.io/downloads
5. Install pip. Pip makes installing python packages very easy. Here's the link to the download: https://pip.pypa.io/en/latest/installing/
6. Check the file located at /TalkAboutObjects/DjangoDB/DjangoDB/settings.py and make sure the paramter "USE_POSTGRES" is equal to "False". This ensures you are using a local version of the database.
```USE_POSTGRES = False```
7. from within the /TalkAboutObjects directory, run "pip install -r requirements.txt" this will install all of the necessary python applications if they aren't already on your machine
8. run the following command:
```python DjangoDB/manage.py migrate```
This will setup the sqlite database on your machine to be ready to play the game.
9. run the following from within the TalkAboutObjects directory ```./RunGame.sh```. This script begins the game for you.
10. That's all it takes, you should now be set to play the game!
