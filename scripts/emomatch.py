# emomatch.py
# Facial expression of emotion matching task inspired by Hariri task

# import dependencies
import pathlib
import csv
import hashlib
import glob
import os
import numpy as np
import random
from datetime import datetime
from utilities import define_keys, Trigger, getConfig, getDimensions
from psychopy import core, logging, visual, event
from utilities import define_keys, Trigger, getConfig, getDimensions, save_csv_emomatch_behav

""" 
HCP description

The participants are presented with blocks of trials that ask them to decide either which of two faces 
presented on the bottom of the screen match the face at the top of the screen, or which of two shapes 
presented at the bottom of the screen match the shape at the top of the screen. The faces have either 
angry or fearful expressions. 

Trials are presented in blocks of 6 trials of the same task (face or shape), with the stimulus presented for 2 s and a 1 s ITI. 
Each block is preceded by a 3 s task cue ('shape' or 'face'), so that each block is 21 s including the cue. 

Each of the two runs includes 3 face blocks and 3 shape blocks.
"""

# counterbalance/randomizaton helpers
def get_pair_seed(subject_id: str) -> int:
    """Deterministic seed based on subjID (stable across runs/machines)."""
    h = hashlib.md5(subject_id.encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def pick_design_for_subj(subj_id: str, run: int, n_loops):
    # Get random order
    seed = get_pair_seed(subj_id)
    rng = np.random.default_rng(seed)
    
    # list of possible miniblock configurations
    miniblocks = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 1, 0], [2, 0, 1]]

    # permute miniblock order
    order_mb = rng.permutation(np.arange(0, len(miniblocks)))
    miniblocks_perm = [miniblocks[i] for i in order_mb]
    
    if run == 1:
        return miniblocks_perm[0:n_loops]
    else:
        return miniblocks_perm[-n_loops:]

def item_orders_for_subject(subj_id: str, ses: str, run: str, numCb: int, numFaces_gen: int, numFaces_emo: int):
    seed = get_pair_seed(subj_id + ses + run) # randomize by subject ID, session, and run
    rng = np.random.default_rng(seed)
    order_cb = rng.permutation(np.arange(1, numCb+1))
    order_gen = rng.permutation(np.arange(1, numFaces_gen+1))
    order_emo = rng.permutation(np.arange(1, numFaces_emo+1))

    return order_cb, order_gen, order_emo

# Set probe, foil, and target IDs for each condition
def pick_items_checkerboard(order_cb, num_thesh, marginMin, marginMax, num_exemplar):
    
    item_array = []
    exemplar_array = []
    perceptualDiff_array = []
    probePropBlack_array = []
    foilPropBlack_array = []
    
    for idx, item in enumerate(order_cb):
        idx = int(idx)
        item = int(item)
        # find probe and pick exemplar
        probe = item
        probe_exemplar = random.randint(1,10)
        # pick foil: different item, different exemplar (the same exemplar looks too similar if thresh is too close)
        foil, perceptualDiff, probePropBlack, foilPropBlack = random_positive_integer_within_range_excluding_base(probe, num_thesh, marginMin, marginMax)
        perceptualDiff_array.append(perceptualDiff)
        probePropBlack_array.append(probePropBlack)
        foilPropBlack_array.append(foilPropBlack)
        foil_exemplar = random_positive_integer_within_range_excluding_base_and_other(probe_exemplar, num_exemplar, 0)
        # pick target: same item, different exemplar
        target = item
        target_exemplar = random_positive_integer_within_range_excluding_base_and_other(probe_exemplar, num_exemplar, 0)
        item_array.append([probe, foil, target])
        exemplar_array.append([probe_exemplar, foil_exemplar, target_exemplar])
    
    item_arraynp = np.array(item_array)
    item_padded = np.char.zfill(item_arraynp.astype(str), 2)
    exemplar_arraynp = np.array(exemplar_array)
    exemplar_padded = np.char.zfill(exemplar_arraynp.astype(str), 2)
    
    return item_padded, exemplar_padded, perceptualDiff_array, probePropBlack_array, foilPropBlack_array

def load_checkerboard_images(item_array, exemplar_array, image_dir, window, size):
    
    # number of images to load
    n_im_to_show = item_array.shape[0]
    n_im_per_trial = item_array.shape[1]
    
    # Set function output
    probe_filename = [None] * n_im_to_show
    probe_stims = {}
    foil_filename = [None] * n_im_to_show
    foil_stims = {}
    target_filename = [None] * n_im_to_show
    target_stims = {}
    
    # Load selected images for subject and session
    for idx in range(n_im_to_show):
        # probe
        this_item = item_array[idx][0]
        this_percent = 3 * int(this_item) + 18
        this_exemplar = exemplar_array[idx][0]
        probe_filename[idx] = f"masked_SHINEd_checkerboard_{this_item}_{this_percent}_{this_exemplar}.png"
        probe_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, probe_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        # foil
        this_item = item_array[idx][1]
        this_percent = 3 * int(this_item) + 18
        this_exemplar = exemplar_array[idx][1]
        foil_filename[idx] = f"masked_SHINEd_checkerboard_{this_item}_{this_percent}_{this_exemplar}.png"
        foil_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, foil_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        # target
        this_item = item_array[idx][2]
        this_percent = 3 * int(this_item) + 18
        this_exemplar = exemplar_array[idx][2]
        target_filename[idx] = f"masked_SHINEd_checkerboard_{this_item}_{this_percent}_{this_exemplar}.png"
        target_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, target_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        
    return probe_stims, foil_stims, target_stims, probe_filename, foil_filename, target_filename

def pick_items_gender(order_gen, numFaces):
    # format order vector to get probe ID and gender
    probe_id = np.where(order_gen >= numFaces+1, (order_gen - numFaces+1) % numFaces + 1, order_gen)
    n = len(probe_id)
    zeros_count = n // 2
    ones_count = n - zeros_count
    probe_gender = np.random.permutation([0] * zeros_count + [1] * ones_count)
    
    # set foil and target IDs
    # both need to be different from probe_id 
    foil_id = []
    target_id = []
    for idx, item in enumerate(probe_id):
        foil = random_positive_integer_within_range_excluding_base_and_other(item, numFaces, 0)
        foil_id.append(foil)
        target = random_positive_integer_within_range_excluding_base_and_other(item, numFaces, foil)
        target_id.append(target)
    
    # set foil and target gender
    foil_gender = 1 - probe_gender
    target_gender = probe_gender
    
    tmp = [np.array(item) for item in zip(*[probe_id, foil_id, target_id])]
    id_array = np.array([[int(x) for x in row] for row in tmp])
    id_padded = np.char.zfill(id_array.astype(str), 2)
    tmp = [np.array(item) for item in zip(*[probe_gender, foil_gender, target_gender])]
    gender_array = [[int(x) for x in row] for row in tmp]
    
    return id_padded, gender_array

def load_gender_images(id_array, gender_array, image_dir, window, size):
    
    # number of images to load
    n_im_to_show = id_array.shape[0]
    n_im_per_trial = id_array.shape[1]
    this_emo = 'NE'
    
    # Set function output
    probe_filename = [None] * n_im_to_show
    probe_stims = {}
    foil_filename = [None] * n_im_to_show
    foil_stims = {}
    target_filename = [None] * n_im_to_show
    target_stims = {}
    
    # Load selected images for subject and session
    for idx in range(n_im_to_show):
        # probe
        this_gender = 'FEM' if gender_array[idx][0] == 1 else 'MAL'
        this_id = id_array[idx][0]
        probe_filename[idx] = f"masked_SHINEd_{this_gender}{this_id}_{this_emo}.png"
        probe_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, probe_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        # foil
        this_gender = 'FEM' if gender_array[idx][1] == 1 else 'MAL'
        this_id = id_array[idx][1]
        foil_filename[idx] = f"masked_SHINEd_{this_gender}{this_id}_{this_emo}.png"
        foil_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, foil_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        # target
        this_gender = 'FEM' if gender_array[idx][2] == 1 else 'MAL'
        this_id = id_array[idx][2]
        target_filename[idx] = f"masked_SHINEd_{this_gender}{this_id}_{this_emo}.png"
        target_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, target_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        
    return probe_stims, foil_stims, target_stims, probe_filename, foil_filename, target_filename

def pick_items_emo(order_emo, numFaces):
    
    # format order vector to get probe ID, gender, and emotion  
    probe_id = np.where(order_emo >= numFaces+1, (order_emo - numFaces+1) % numFaces + 1, order_emo)
    n = len(probe_id)
    zeros_count = n // 2
    ones_count = n - zeros_count
    probe_gender = np.random.permutation([0] * zeros_count + [1] * ones_count)
    probe_emo = np.random.permutation([0] * zeros_count + [1] * ones_count)
    
    # set foil and target IDs
    # both need to be different from probe_id 
    foil_id = []
    target_id = []
    for idx, item in enumerate(probe_id):
        foil = random_positive_integer_within_range_excluding_base_and_other(item, numFaces, 0)
        foil_id.append(foil)
        target = random_positive_integer_within_range_excluding_base_and_other(item, numFaces, foil)
        target_id.append(target)
    
    # set foil and target gender: random
    foil_gender = np.random.permutation([0] * (n // 2) + [1] * (n // 2))
    target_gender = np.random.permutation([0] * (n // 2) + [1] * (n // 2))
    
    # set foil and target emotion
    # foil is different emotion, target is same emotion
    foil_emo= 1 - probe_emo
    target_emo = probe_emo
    
    tmp = [np.array(item) for item in zip(*[probe_id, foil_id, target_id])]
    id_array = np.array([[int(x) for x in row] for row in tmp])
    id_padded = np.char.zfill(id_array.astype(str), 2)
    tmp = [np.array(item) for item in zip(*[probe_gender, foil_gender, target_gender])]
    gender_array = [[int(x) for x in row] for row in tmp]
    tmp = [np.array(item) for item in zip(*[probe_emo, foil_emo, target_emo])]
    emo_array = [[int(x) for x in row] for row in tmp]
    
    return id_padded, gender_array, emo_array

def load_emo_images(id_array, gender_array, emo_array, image_dir, window, size):
    
    # number of images to load
    n_im_to_show = id_array.shape[0]
    n_im_per_trial = id_array.shape[1]
    
    # Set function output
    probe_filename = [None] * n_im_to_show
    probe_stims = {}
    foil_filename = [None] * n_im_to_show
    foil_stims = {}
    target_filename = [None] * n_im_to_show
    target_stims = {}
    
    # Load selected images for subject and session
    for idx in range(n_im_to_show):
        # probe
        this_gender = 'FEM' if gender_array[idx][0] == 1 else 'MAL'
        this_emo = 'AN' if emo_array[idx][0] == 1 else 'FE'
        this_id = id_array[idx][0]
        probe_filename[idx] = f"masked_SHINEd_{this_gender}{this_id}_{this_emo}.png"
        probe_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, probe_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        # foil
        this_gender = 'FEM' if gender_array[idx][1] == 1 else 'MAL'
        this_emo = 'AN' if emo_array[idx][1] == 1 else 'FE'
        this_id = id_array[idx][1]
        foil_filename[idx] = f"masked_SHINEd_{this_gender}{this_id}_{this_emo}.png"
        foil_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, foil_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        # target
        this_gender = 'FEM' if gender_array[idx][2] == 1 else 'MAL'
        this_emo = 'AN' if emo_array[idx][2] == 1 else 'FE'
        this_id = id_array[idx][2]
        target_filename[idx] = f"masked_SHINEd_{this_gender}{this_id}_{this_emo}.png"
        target_stims[idx] = visual.ImageStim(
            window,
            image=os.path.join(image_dir, target_filename[idx]),
            size=size,
            interpolate=True,
            autoLog=False
        )
        
    return probe_stims, foil_stims, target_stims, probe_filename, foil_filename, target_filename

def random_positive_integer_within_range_excluding_base(base_number, maximum_val, marginMin, marginMax):
    #scaling = 1.5
    probePropBlack = (3 * int(base_number) + 18) / 100
    while True:
        candidate = random.randint(1, maximum_val)
        candidatePropBlack = (3 * int(candidate) + 18) / 100
        diff = abs(probePropBlack - candidatePropBlack)
        if diff >= marginMin and diff <= marginMax and diff != 0:
            return candidate, diff, probePropBlack, candidatePropBlack

def random_positive_integer_within_range_excluding_base_and_other(base_number, maximum_val, exclude_other):
    maximum_val = int(maximum_val)
    while True:
        candidate = random.randint(1, maximum_val)
        if candidate != base_number and candidate != exclude_other:
            return candidate

# Main task
def run_task(subject, session, language, demo, run_number):

    # get directories
    path_to_config = pathlib.Path(__file__).parent.parent
    filename = os.path.join(path_to_config, "config.json")
    configDirs = getConfig(filename)
    stimDir = os.path.join(configDirs['io_root_dir'], "stimuli", "emomatch")

    # task name
    task = 'task-emomatch_lang-{lang}_run-{r}'.format(lang=language, r=run_number)

    # Define keys
    setKeys = define_keys('0', '5', ['1','2']) 
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
    rootLog = os.path.join(configDirs['io_root_dir'], "logs", "emomatch")
    logName = 'sub-{subj}_ses-{sess}_{task}_{dt}.log'.format(subj=subject, sess=session, task=task, dt=datetimestr)
    log_filename = os.path.join(rootLog, logName)
    logFile = logging.LogFile(log_filename, level=logging.EXP)

    # demo
    if demo == 'demo':
        restDur = 4.0
        readyDur = 1.0
        introBlockDur = 1.0
        stimDur = 3.0
        isiDur = 1.0
        fixDur = 3.0
        num_trials_per_cond = [2, 2, 2] # order always ['checker', 'gender', 'emo']
        n_loops = 1
    else:
        restDur = 12.0
        readyDur = 2.0
        introBlockDur = 3.0
        stimDur = 1.5
        isiDur = 1.0
        fixDur = 8.0
        num_trials_per_cond = [6, 6, 6] # order always ['checker', 'gender', 'emo']
        n_loops = 3
    
    # set design for this run
    condPrefs = ['checker', 'gender', 'emo']
    total_numtrials = sum(num_trials_per_cond) * n_loops
    block_order = pick_design_for_subj(subject, int(run_number), n_loops)
    run_this_block = np.array(block_order[int(session)-1])
        
    # set item order for this block
    numFaceItems = 18
    numSex = 2
    numFaces = numFaceItems / numSex # number of different identities per gender
    numCb = 21
    order_cb, order_gen, order_emo = item_orders_for_subject(subject, session, run_number, numCb, numFaces, numFaces)

    # Load all items we need into memory
    marginMin = 0.20
    marginMax = 0.40
    order_cb_trial = order_cb[0:num_trials_per_cond[0]]
    cb_items, cb_exemplars, perceptualDiff, probePropBlack, foilPropBlack = pick_items_checkerboard(order_cb_trial, 21, marginMin, marginMax, 10)

    order_gen_trial = order_gen[0:num_trials_per_cond[1]]
    identities_items1, gender_items1 = pick_items_gender(order_gen_trial, numFaces)

    order_emo_trial = order_emo[0:num_trials_per_cond[2]]
    identities_items2, gender_items2, emo_items2 = pick_items_emo(order_emo_trial, numFaces)

    # define behavioral arrays
    cond = [0] * total_numtrials  # cb | gender | emo
    trialNum = [0] * total_numtrials
    probeName = ['' for _ in range(total_numtrials)] # filename
    foilName = ['' for _ in range(total_numtrials)] # filename
    targetName = ['' for _ in range(total_numtrials)] # filename
    pDiff_for_cb = [0] * total_numtrials
    probePropBlack_for_cb = [0] * total_numtrials
    foilPropBlack_for_cb = [0] * total_numtrials
    block_onsets = [0.0] * total_numtrials  # start of block
    trial_onsets = [0.0] * total_numtrials  # start of trial
    targetLocation = [0] * total_numtrials  # target location
    key_vec = [0] * total_numtrials  # target response
    acc_vec = [0] * total_numtrials  # is response correct
    RT_vec = [0.0] * total_numtrials  # reaction time
    
    # display window & get size properties
    win = visual.Window(fullscr=True, color=[0.005, 0.005, 0.005], units='height', colorSpace='rgb')
    win.mouseVisible = False
    posProbe = (0, 0.18)
    posChoices = ((-0.18, -0.18), (0.18, -0.18))

    # text and fixation features
    sans = ['Arial', 'Gill Sans MT', 'Helvetica', 'Verdana']
    Txt = visual.TextStim(win, name='instruction', text='default text', font=sans, pos=(0, 0),
        height=0.03, wrapWidth=1100, color='black')
    fixation = visual.TextStim(win, name='fixation', text='+', font=sans, pos=(0, 0),
        height=float(.16), color='black')
    
    # Set text paths
    instructionsFile = 'emomatch_{lang}_instructions.txt'.format(lang=language)
    instructions_path = os.path.join(configDirs['io_root_dir'], 'instructions', instructionsFile)
    restFile = 'rest_{lang}.txt'.format(lang=language)
    rest_path = os.path.join(configDirs['io_root_dir'], 'instructions', restFile)
    readyFile = 'ready_{lang}.txt'.format(lang=language)
    ready_path = os.path.join(configDirs['io_root_dir'], 'instructions', readyFile)
    cbStartFile = 'emomatch_checkerBlock_{lang}.txt'.format(lang=language)
    cbStart_path = os.path.join(configDirs['io_root_dir'], 'instructions', cbStartFile)
    genderStartFile = 'emomatch_genderBlock_{lang}.txt'.format(lang=language)
    genderStart_path = os.path.join(configDirs['io_root_dir'], 'instructions', genderStartFile)
    emoStartFile = 'emomatch_emoBlock_{lang}.txt'.format(lang=language)
    emoStart_path = os.path.join(configDirs['io_root_dir'], 'instructions', emoStartFile)

    # display instructions
    Txt.setText(open(instructions_path, 'r', encoding='utf-8').read())
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY instructions')
    win.flip()
    event.waitKeys(keyList=responseKey)
    
    # launch scan
    Trigger(mainClock, Txt, win, triggerKey)

    # Start experiment
    clock_global = core.Clock()
    experimentStart = clock_global.getTime()
    trial_counter = 0

    # Fixation
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY fixation')
    win.flip()
    fix_start = clock_global.getTime()
    while (clock_global.getTime() - fix_start) < fixDur:
        core.wait(0.01)

    try:
        #for block_num, this_block in enumerate(run_this_block):
        for block_num, this_block in enumerate(block_order):
            for miniblock_num, this_miniblock in enumerate(this_block):
                this_n_trials = num_trials_per_cond[this_miniblock]
                n_loops_trials = range(this_n_trials)

                if this_miniblock == 0:
                    this_probe, this_foil, this_target, probe_filename, foil_filename, target_filename = load_checkerboard_images(
                        cb_items, 
                        cb_exemplars, 
                        os.path.join(stimDir, condPrefs[this_miniblock]),
                        win,
                        0.4)
                    this_block_path = cbStart_path
                elif this_miniblock == 1:
                    this_probe, this_foil, this_target, probe_filename, foil_filename, target_filename = load_gender_images(
                        identities_items1, 
                        gender_items1, 
                        os.path.join(stimDir, condPrefs[this_miniblock]),
                        win,
                        0.4)
                    this_block_path = genderStart_path
                elif this_miniblock == 2:
                    this_probe, this_foil, this_target, probe_filename, foil_filename, target_filename = load_emo_images(
                        identities_items2, 
                        gender_items2, 
                        emo_items2, 
                        os.path.join(stimDir, condPrefs[this_miniblock]),
                        win,
                        0.4)
                    this_block_path = emoStart_path
                else:
                    print(f"Invalid block number - not a valid condition number {this_miniblock}")
                    event.clearEvents(); win.close(); core.quit()

                # pick target/foil positions
                n = len(this_target)
                zeros_count = n // 2
                ones_count = n - zeros_count
                foil_location = np.random.permutation([0] * zeros_count + [1] * ones_count)
                target_location = 1 - foil_location

                # Get ready for the next block...
                if block_num == 0:
                    win.logOnFlip(level=logging.EXP, msg='OFF fixation')
                    win.flip()
                Txt.setText(open(ready_path, 'r', encoding='utf-8').read())
                Txt.draw()
                win.logOnFlip(level=logging.EXP, msg='DISPLAY get ready')
                win.flip()
                ready_start = clock_global.getTime()
                while (clock_global.getTime() - ready_start) < readyDur:
                    core.wait(0.01)
                win.logOnFlip(level=logging.EXP, msg='OFF get ready')
                win.flip()

                # Announce next block
                Txt.setText(open(this_block_path, 'r', encoding='utf-8').read())
                Txt.draw()
                win.logOnFlip(level=logging.EXP, msg='DISPLAY block start')
                win.flip()
                block_start = clock_global.getTime()
                while (clock_global.getTime() - block_start) < introBlockDur:
                    core.wait(0.01)
                win.logOnFlip(level=logging.EXP, msg='OFF block start')
                win.flip()
                
                # start of experiment loop for this block
                blockLoop_start = clock_global.getTime()
                block_onsets[trial_counter] = blockLoop_start - experimentStart # start of block

                for trial_idx in n_loops_trials:
                    
                    # Fill response matrix
                    cond[trial_counter] = this_miniblock
                    trialNum[trial_counter] = trial_idx
                    probeName[trial_counter] = probe_filename[trial_idx]
                    foilName[trial_counter] = foil_filename[trial_idx]
                    targetName[trial_counter] = target_filename[trial_idx]
                    targetLocation[trial_counter] = target_location[trial_idx]+1 # add one to align with keypress
                    if this_miniblock == 0:
                        pDiff_for_cb[trial_counter] = perceptualDiff[trial_idx]
                        probePropBlack_for_cb[trial_counter] = probePropBlack[trial_idx]
                        foilPropBlack_for_cb[trial_counter] = foilPropBlack[trial_idx]
                    else:
                        pDiff_for_cb[trial_counter] = 0
                        probePropBlack_for_cb[trial_counter] = 0
                        foilPropBlack_for_cb[trial_counter] = 0
                    
                    # Prepare trial
                    probeStim = this_probe[trial_idx]
                    probeStim.pos = posProbe
                    probeStim.draw()

                    foilStim = this_foil[trial_idx]
                    foilStim.pos = posChoices[foil_location[trial_idx]]
                    foilStim.draw()

                    targetStim = this_target[trial_idx]
                    targetStim.pos = posChoices[target_location[trial_idx]]
                    targetStim.draw()

                    # Show trial
                    win.logOnFlip(level=logging.EXP, msg='DISPLAY trial condition ' + condPrefs[this_miniblock])
                    win.flip()
                    stimOnScreen = clock_global.getTime()
                    trial_onsets[trial_counter] = stimOnScreen - experimentStart  # start of trial

                    # Response window
                    response_start = clock_global.getTime()
                    got_first = False
                    key_vec[trial_counter] = 0
                    RT_vec[trial_counter] = 0.0
                    keyList = list(responseKey) + list(breakKey)
                    while (clock_global.getTime() - response_start) < stimDur:
                        keys = event.getKeys(keyList=keyList, timeStamped=False)
                        if keys:
                            if breakKey in keys:
                                raise KeyboardInterrupt
                            if not got_first:
                                if responseKey[0] in keys:
                                    key_vec[trial_counter] = 1
                                    RT_vec[trial_counter] = clock_global.getTime() - response_start
                                    got_first = True
                                elif responseKey[1] in keys:
                                    key_vec[trial_counter] = 2
                                    RT_vec[trial_counter] = clock_global.getTime() - response_start
                                    got_first = True
                        core.wait(0.005)

                    # Stimulus off
                    win.logOnFlip(level=logging.EXP, msg='OFF trial condition ' + condPrefs[this_miniblock])
                    win.flip()
                    core.wait(isiDur)

                    # response accuracy
                    respAcc = key_vec[trial_counter] == targetLocation[trial_counter]
                    acc_vec[trial_counter] = 1 if respAcc == True else 0

                    # Backup CSV
                    tmp_csvName = 'sub-{subj}_ses-{sess}_{task}_{dt}_backup.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
                    tmp_csv_filename = os.path.join(rootLog, tmp_csvName)
                    save_csv_emomatch_behav(pathlib.Path(tmp_csv_filename), 
                            cond, trialNum, probeName, foilName, targetName, 
                            pDiff_for_cb, probePropBlack_for_cb, foilPropBlack_for_cb,
                            block_onsets, trial_onsets, targetLocation, 
                            key_vec, acc_vec, RT_vec)

                    trial_counter += 1

                # inter-block rest period
                Txt.setText(open(rest_path, 'r', encoding='utf-8').read())
                Txt.draw()
                win.logOnFlip(level=logging.EXP, msg='DISPLAY rest')
                win.flip()
                rest_start = clock_global.getTime()
                while (clock_global.getTime() - rest_start) < restDur:
                    core.wait(0.01)
                win.logOnFlip(level=logging.EXP, msg='OFF rest')
                win.flip()

        # Final save
        experimentEnd = clock_global.getTime()
        experimentDuration = experimentEnd - experimentStart
        final_csv = 'sub-{subj}_ses-{sess}_{task}_{dt}.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
        final_csv_filename = os.path.join(rootLog, final_csv)
        save_csv_emomatch_behav(pathlib.Path(final_csv_filename), 
                        cond, trialNum, probeName, foilName, targetName, 
                        pDiff_for_cb, probePropBlack_for_cb, foilPropBlack_for_cb,
                        block_onsets, trial_onsets, targetLocation, 
                        key_vec, acc_vec, RT_vec)
        print(f"Final data saved to {final_csv}")
        
    except KeyboardInterrupt:
        abort_csv = 'sub-{subj}_ses-{sess}_{task}_{dt}_ABORT.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
        abort_csv_filename = os.path.join(rootLog, abort_csv)
        save_csv_emomatch_behav(pathlib.Path(abort_csv_filename), 
                        cond, trialNum, probeName, foilName, targetName, 
                        pDiff_for_cb, probePropBlack_for_cb, foilPropBlack_for_cb,
                        block_onsets, trial_onsets, targetLocation, 
                        key_vec, acc_vec, RT_vec)
        print(f"Experiment aborted, partial data saved to {abort_csv}")
        event.clearEvents(); win.close(); core.quit()
    
    # Fixation
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY fixation')
    win.flip()
    fix_start = clock_global.getTime()
    while (clock_global.getTime() - fix_start) < fixDur:
        core.wait(0.01)
    win.logOnFlip(level=logging.EXP, msg='OFF fixation')
    win.flip()

    # display end of task screen
    endFile = '{lang}_end.txt'.format(lang=language)
    end_path = os.path.join(configDirs['io_root_dir'], "instructions", endFile)
    Txt.setText(open(end_path, 'r', encoding='utf-8').read())
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY end')
    win.flip()
    event.waitKeys(keyList=breakKey)
    core.wait(0.1)
    
    # clean up
    event.clearEvents()
    win.close()
    core.quit()