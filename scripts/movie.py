# movie.py
# SoCo: Movie watching BOLD sequences
# Three movie choices: - Partly cloudy
#                      - LotR
#                      - TBD

# import dependencies
import pathlib
import os
from datetime import datetime
from utilities import define_keys, Trigger, getConfig
from psychopy import core, logging, visual, event
from psychopy.visual import MovieStim


def run_task(subject, session, language, demo, movie_name):

    # task name
    task = 'rest-movie-' + movie_name + '_lang-' + language
    
    # Define keys
    breakKey = define_keys()['break']
    triggerKey = define_keys()['trigger']
    responseKey = define_keys()['response']
    
    # Fetch movie name
    if 'cloudy' in movie_name:
        rootMovie = os.path.join(mainDir, "videos")
        movieFilename = 'partly_cloudy.mp4'
        # movieName = "partly_cloudy.mp4"
        clip = os.path.join(rootMovie, movieFilename)
    elif 'lotr' in movie_name:
        rootMovie = os.path.join(mainDir, "videos")
        movieFilename = 'council_of_elrond_' + language + '.mp4'
        # movieName = "council_of_elrond.mp4"
        clip = os.path.join(rootMovie, movieFilename)
    
    # Get date and time for log name
    now = datetime.now()
    datetimestr = now.strftime("%Y.%m.%d_%H.%M.%S")
    
    # set up main clock & logging features
    mainClock = core.Clock()
    logging.setDefaultClock(mainClock)
    logging.console.setLevel(logging.ERROR)
    
    # create log
    rootLog = os.path.join(mainDir, "logs")
    logName = 'sub-' + subject + '_ses-' + session + '_' + task + '_' + datetimestr + '.log'
    # logName = "sub-" + subject + "_ses-" + session + "_" + task + "_" + datetimestr + ".log"
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
    
    # display instructions
    instructionsFile = language + '_instructions_movie.txt'
    instructions_path = os.path.join(mainDir, 'instructions', instructionsFile)
    Txt.setText(open(instructions_path, 'r').read())
    Txt.draw()
    win.flip()
    event.waitKeys(keyList=responseKey)
    
    # launch scan
    Trigger(mainClock, Txt, win, triggerKey)
    
    # display RS fixation cross
    RS_FixCross = visual.TextStim(win, name='fixation cross', text='+', font=sans, pos=(0, 0),
        height=float(.16), color='gray')
    RS_FixCross.draw()
    win.flip()
    fixOn = mainClock.getTime() # onset time
    clock = core.Clock()
    core.wait(2)
    
    # Play until movie finishes or user presses a key
    dims = getDimensions(clip)
    targetWidth = 1024
    aspectRatio = dims[0] / dims[1]
    targetHeight = round(targetWidth / aspectRatio)
    movie = visual.MovieStim(win, clip, loop=False, noAudio=False, name=movie_name, size=(targetWidth,targetHeight))
    movieOn = mainClock.getTime() # onset time
    movie.play()
    while movie.isPlaying:
        movie.draw()
        win.flip()
        if breakKey[0] in event.getKeys():
            break
    movie.stop()
    
    # small break if lotr
    if 'lotr' in movie_name:
        core.wait(2)
    
    # display end of task screen
    endFile = language + '_end.txt'
    end_path = os.path.join(mainDir, 'instructions', endFile)
    #Txt.setText(open(end_path, 'r').read())
    with open(end_path, 'r') as f:
        Txt.setText(f.read())
    Txt.draw()
    win.flip()
    event.waitKeys(keyList=breakKey)
    core.wait(0.1)
    
    # clean up
    event.clearEvents()
    win.close()
    core.quit()