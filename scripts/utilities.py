# utilities.py
# Utilities for social carousel 

# import dependencies
import sys
import os
import subprocess
import time
from psychopy import core, logging, visual, event
from psychopy.visual import TextBox2
import cv2
import json
import csv
from pathlib import Path


def define_keys(bk, tk, rk):
    breakKey = bk
    triggerKey = tk
    responseKey = rk
    return{'break': breakKey, 'trigger': triggerKey, 'response': responseKey}

def Trigger(clock, Txt, win, triggerKey):
    Txt.setText('waiting for scanner...')
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY waiting for trigger')
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


# ---------- CSV writer ----------
def save_csv(path: Path, design, items, key_vec, RT_vec,
             fix_onsets, story_onsets, question_onsets,
             *, experiment_duration=None, ips=None, meta=None):
    """Write the current dataset + optional metadata rows to a CSV file."""
    trials_per_run = len(design)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "trial",
            "design(1=belief,2=photo)",
            "itemNum",
            "key(1/2)",
            "RT(s)",
            "fix_onset_s",
            "story_onset_s",
            "question_onset_s"
        ])
        for t in range(trials_per_run):
            w.writerow([
                t + 1, design[t], items[t],
                key_vec[t], f"{RT_vec[t]:.4f}",
                f"{fix_onsets[t]:.3f}",
                f"{story_onsets[t]:.3f}",
                f"{question_onsets[t]:.3f}"
            ])
        # metadata block (empty line + key/value rows)
        if any(v is not None for v in (experiment_duration, ips, meta)):
            w.writerow([])
        if experiment_duration is not None:
            w.writerow(["experimentDuration_s", f"{experiment_duration:.3f}"])
        if ips is not None:
            w.writerow(["ips", f"{ips:.3f}"])
        if meta:
            for key, value in meta.items():
                w.writerow([key, value])
