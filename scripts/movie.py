# movie.py
# SoCo: Movie watching BOLD sequences
# Three movie choices: - Partly cloudy
#                      - LotR
#                      - TBD

# import dependencies
import sys
import os
import subprocess
import time
from psychopy import core, logging, visual, event
from psychopy.visual import MovieStim
from datetime import datetime
import cv2

def define_keys():
    breakKey = ['0']
    triggerKey = ['5']
    responseKey = ['1', '2', '3']
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

def run_task(subject_id, session):
    win = visual.Window([800, 600], color="grey")

    msg = visual.TextStim(
        win,
        text=f"Movie watching\nSubject: {subject_id}\nSession: {session}\n\nPress any key to start.",
        font="Arial"
    )
    msg.draw()
    win.flip()
    event.waitKeys()

    # Example differing behavior for run 1 vs run 2
    stim_text = "ello this is movie"

    stim = visual.TextStim(win, text=stim_text, font="Arial")
    stim.draw()
    win.flip()
    core.wait(2)

    win.close()