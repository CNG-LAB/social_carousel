# cross.py

import pathlib
import os
from datetime import datetime
from utilities import define_keys, Trigger, getConfig
from psychopy import visual, event, core

def run_task(subject_id, session, language, demo):
    
    # get directories
    path_to_config = pathlib.Path(__file__).parent.parent
    print('ello this is path')
    print(path_to_config)
    filename = os.path.join(path_to_config, "config.json")
    configDirs = getConfig(filename)

    # task name
    task = 'rest-fixation_lang-' + language
    
    # Define keys
    setKeys = define_keys('0', '5', ['1','2','3'])
    breakKey = setKeys['break']
    triggerKey = setKeys['trigger']
    responseKey = setKeys['response']
    
    # Get date and time for log name
    now = datetime.now()
    datetimestr = now.strftime("%Y.%m.%d_%H.%M.%S")
    
    # set up main clock & logging features
    mainClock = core.Clock()
    logging.setDefaultClock(mainClock)
    logging.console.setLevel(logging.ERROR)
    
    # create log
    rootLog = os.path.join(configDirs['io_root_dir'], "logs")
    logName = 'sub-' + subject + '_ses-' + session + '_' + task + '_' + datetimestr + '.log'
    log_filename = os.path.join(rootLog, logName)
    logFile = logging.LogFile(log_filename, level=logging.EXP)
    
    # display window & get size properties
    win = visual.Window(fullscr=True, color='black', units='height')
    win.mouseVisible = False
    win.color = 'black'
    
    # text and fixation features
    sans = ['Arial', 'Gill Sans MT', 'Helvetica', 'Verdana']
    Txt = visual.TextStim(win, name='instruction', text='default text', font=sans, pos=(0, 0),
        height=float(.04), wrapWidth=1100, color='white')
    fixation = visual.TextStim(win, name='fixation', text='+', font=sans, pos=(0, 0), height=float(.08),
        color='black')
    
    # display RS instructions
    instructionsFile = 'cross_' + language + '_instructions.txt'
    instructions_path = os.path.join(configDirs['io_root_dir'], 'instructions', instructionsFile)
    Txt.setText(open(instructions_path, 'r').read())
    Txt.draw()
    win.flip()
    event.waitKeys(keyList=responseKey)
    
    # launch scan
    Trigger(mainClock, Txt, win, triggerKey)
    
    # display RS fixation cross
    RS_FixCross = visual.TextStim(win, name='RS fixation cross', text='+', font=sans, pos=(0, 0),
        height=float(.16), color='gray')
    RS_FixCross.draw()
    win.flip()
    
    # get onset time of gray fixation cross
    fixOn = mainClock.getTime()
    
    # display fixation for six minutes
    if demo == yes:
        RS_scanDur = 5
    else:
        RS_scanDur = 360
    fixDur = fixOn + RS_scanDur
    clock = core.Clock()
    while clock.getTime() < fixDur:
        if breakKey in event.getKeys(): # check for escape
            core.quit()
        core.wait(0.1)  # small pause so CPU doesn’t max out
        
    # display end of task screen
    endFile = language + '_end.txt'
    end_path = os.path.join(configDirs['io_root_dir'], 'instructions', endFile)
    Txt.setText(open(end_path, 'r').read())
    Txt.draw()
    win.flip()
    event.waitKeys(keyList=breakKey)
    core.wait(0.1)
    
    # clean up
    event.clearEvents()
    win.close()
    core.quit()

