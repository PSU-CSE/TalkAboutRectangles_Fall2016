# TalkAboutRectangles_Fall2016 README #

### What is this repository for? ###

* This repository maintains the code required to run and develop the TalkAboutRectangles game. The long-range purpose of the game is to collect data of different ways people refer to things, depending on what they see in the context. The near-term goal is to develop methods to translate between subjective, context-dependent meanings of natural language expressions and the precise, formal representation of a set of rectangles represented in terms of their size, position in a 2D grid, color, and shape.

### How do I get set up? ###

#### On Windows: ####
-------------------------
1.Install git from https://git-scm.com/downloads

2.Clone this repository: git clone https://github.com/PSU-CSE/TalkAboutRectangles_Fall2016.git

3.In a Command Prompt(run as administrator), navigate to the directory this readme is located in and run a "git pull" to make sure everything is up to date.

4.Install python 2.7 from https://www.python.org/downloads/

5.Install pip by typing python get-pip.py under TalkAboutRectangles folder in Command Prompt(run as administrator)

6.run setupWindows.sh located under TalkAboutRectangles folder by typing . Please make sure that you run it with premission to install package!!

	(for windows run it from command line as administrator(right click), find the TalkAboutRectangles/setupWindows.sh)
	(for Linux: sudo -H sh setup.sh)
	
7.Execute the following commands: python DjangoDB/manage.py shell

	>>> execfile("initialize.py")
	>>> import ApplicationGUI
   
This will start a Django console, add the current working directory to the system path, and start the game.

#### On a Mac: ####
----------------------
1.Install git from https://git-scm.com/downloads

2.Clone this repository: git clone https://github.com/PSU-CSE/TalkAboutRectangles_Fall2016.git

3.In a terminal, navigate to the directory this readme is located in and run a "git pull" to make sure everything is up to date.

4.Make sure that you have python 2.7 and pip install on you device   (should have by default on a mac)

5.Run setupMac.sh in terminal by typing "sh setup.sh" under TalkAboutRectangles folder. Please make sure that you run it with premission to install package!! (for Linux: sudo -H sh setup.sh)

6.Execute the following commands: python DjangoDB/manage.py shell

	>>> execfile("initialize.py")
	>>> import ApplicationGUI
   
This will start a Django console, add the current working directory to the system path, and start the game.


#### Trouble Shooting: ####
----------------------

Error Message:
setup.sh: line 4: pip: command not found
Solution:
Install pip by typing python get-pip.py under TalkAboutRectangles folder in Terminal (Command Prompt)

Error Message:
....(many red lines before the last line)
OSError: [Errno 13] Permission denied: '....' (A directory under python)
(or)
WindowsError: [Error 5] Access is denied: '....' (A directory under python)
Solution:
Make sure that you give the permission (you need to run it as an administrator) and try to run setup.sh again.

Error Message:
cannot install package platform error
Solution:
Run the setup.sh instead of setupWindows.sh (setupMac.sh) in the same way.
