# MorseKOB Version 4 - Python

Written by Les Kerr, this is a Python library and programs that implement
the MorseKOB functionality. The library functions in pykob provide modules
and functions that can be used within a Python program to perform MorseKOB
operations.

The MKOB application provides a full graphical interface that allows the
station to connect to a MorseKOB wire on the Morse KOB server. Instructions
for running the MKOB application are in the MKOB-README.

## Getting Started
* Install the dependencies: `pip install -r requirements.txt`
* Run: ` python3 Configure.py -g YES -I KEY_SOUNDER  -A ON -a OFF`
* Warning: GPIO output is hardcoded in the kob.py file. Connect relais to GPI 23 or change the code.


* Running example: `python3 Sample.py`


