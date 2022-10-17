import os
import sys

ROOT_DIR = ""
if getattr(sys, 'frozen', False):
    ROOT_DIR = f"{os.path.dirname(sys.executable)}/"
elif __file__:
    ROOT_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/"

GAME_WIDTH = 640
GAME_HEIGHT = 480

GRAVITY = 1

DEBUG = False

PHASE_DURATION = 20000
SUSPICION_THRESHOLD = 100