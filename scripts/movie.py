# movie.py
# SoCo: Movie watching BOLD sequences
# Three movie choices: - cloudy: Partly cloudy
#                      - lotr: Lord of the Rings
#                      - TBD

# import dependencies
import pathlib
import os
from datetime import datetime
from utilities import define_keys, Trigger, getConfig, getDimensions
from psychopy import core, logging, visual, event
from psychopy.visual import MovieStim

# Main task
def run_task(subject, session, language, demo, movie_name):

    # get directories
    path_to_config = pathlib.Path(__file__).parent.parent
    filename = os.path.join(path_to_config, "config.json")
    configDirs = getConfig(filename)

    # task name
    task = 'rest-movie-{mn}_lang-{lang}'.format(mn=movie_name, lang=language)
    
    # Define keys
    setKeys = define_keys('0', '5', ['1','2','3'])
    breakKey = setKeys['break']
    triggerKey = setKeys['trigger']
    responseKey = setKeys['response']
    
    # Fetch movie name
    rootMovie = os.path.join(configDirs['io_root_dir'], "stimuli", "movies")
    if 'cloudy' in movie_name:
        movieFilename = 'partly_cloudy.mp4'
        clip = os.path.join(rootMovie, movieFilename)
    elif 'lotr' in movie_name:
        movieFilename = 'council_of_elrond_{lang}.mp4'.format(lang=language)
        clip = os.path.join(rootMovie, movieFilename)
    
    # Get date and time for log name
    now = datetime.now()
    datetimestr = now.strftime("%Y.%m.%d_%H.%M.%S")
    
    # set up main clock & logging features
    mainClock = core.Clock()
    logging.setDefaultClock(mainClock)
    logging.console.setLevel(logging.ERROR)
    
    # create log
    rootLog = os.path.join(configDirs['io_root_dir'], "logs", "movies")
    logName = 'sub-{subj}_ses-{sess}_{task}_{dt}.log'.format(subj=subject, sess=session, task=task, dt=datetimestr)
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
    fixation = visual.TextStim(win, name='fixation', text='+', font=sans, pos=(0, 0),
        height=float(.16), color='gray')
    
    # display instructions
    instructionsFile = 'movie_{lang}_instructions.txt'.format(lang=language)
    instructions_path = os.path.join(configDirs['io_root_dir'], 'instructions', instructionsFile)
    Txt.setText(open(instructions_path, 'r', encoding='utf-8').read())
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY instructions')
    win.flip()
    event.waitKeys(keyList=responseKey)
    
    # launch scan
    Trigger(mainClock, Txt, win, triggerKey)
    
    # display RS fixation cross
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY fixation cross')
    win.flip()
    clock = core.Clock()
    core.wait(2)
    
    # Play until movie finishes or user presses a key
    dims = getDimensions(clip)
    targetWidth = 1024
    aspectRatio = dims[0] / dims[1]
    targetHeight = round(targetWidth / aspectRatio)
    win.logOnFlip(level=logging.EXP, msg='DISPLAY movie')
    movie = visual.MovieStim(win, clip, loop=False, noAudio=False, name=movie_name, size=(targetWidth,targetHeight))
    movieOn = mainClock.getTime() # onset time
    movie.play()

    demo_end_time = movieOn + 5 if demo == 'demo' else float('inf')  # set the end time for the demo condition
    while movie.isPlaying and mainClock.getTime() < demo_end_time:
        movie.draw()
        win.flip()
        if breakKey[0] in event.getKeys():
            break

    movie.stop()
    
    # small break if lotr
    if 'lotr' in movie_name:
        core.wait(2)
    
    # display end of task screen
    endFile = '{lang}_end.txt'.format(lang=language)
    end_path = os.path.join(configDirs['io_root_dir'], "instructions", endFile)
    with open(end_path, 'r', encoding='utf-8') as f:
        Txt.setText(f.read())
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY end')
    win.flip()
    event.waitKeys(keyList=breakKey)
    core.wait(0.1)
    
    # clean up
    event.clearEvents()
    win.close()
    core.quit()