# utilities.py
# Utilities for social carousel 

# import dependencies
import sys
import os
import subprocess
import time
from psychopy import core, logging, visual, event
from psychopy.visual import MovieStim
import cv2
import json

def define_keys(bk, tk, rk):
    breakKey = bk
    triggerKey = tk
    responseKey = rk
    return{'break': breakKey, 'trigger': triggerKey, 'response': responseKey}

def Trigger(clock, Txt, win, triggerKey):
    Txt.setText('waiting for scanner...')
    Txt.draw()
    win.flip()
    event.waitKeys(keyList=triggerKey)
    clock.reset()

def getDimensions(clip):
    vid = cv2.VideoCapture(clip)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    return(width, height)

def getConfig(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return(config)
