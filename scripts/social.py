# social.py
# Social cognition task - HCP

# import dependencies
import pathlib
import csv
import hashlib
import os
import numpy as np
from datetime import datetime
from utilities import define_keys, Trigger, getConfig, getDimensions
from psychopy import core, logging, visual, event
from utilities import define_keys, Trigger, getConfig, getDimensions, save_csv


# counterbalance helpers
def get_pair_seed(subject_id: str) -> int:
    """Deterministic seed based on subjID (stable across runs/machines)."""
    # Convert subject ID (e.g., ‘001’) into a pair index:
    # 001–002 -> seed 1
    # 003–004 -> seed 2
    # 005–006 -> seed 3
    # ...
    # 049–050 -> seed 25
    # Seed to decide stimulus order
    sid = int(subject_id)
    id_in_pair = sid % 2
    pair_index = (sid - 1) // 2 + 1   # groups of 2
    h = hashlib.md5(str(pair_index).encode("utf-8")).hexdigest()
    return int(h[:8], 16), id_in_pair

def pick_design_for_run(run: int, subj_id: str):
    """Half of subjects get D1 in run1, half D2 in run1 (deterministic)."""
    # Determined on subject pair so a given pair starts with the same design
    D1 = [1, 2, 2, 1, 2]
    D2 = [1, 1, 2, 1, 2]
    seedFlip, id_in_pair = get_pair_seed(subj_id)
    flip = (seedFlip % 2) == 1
    if run == 1:
        return (D2 if flip else D1), ("D2" if flip else "D1"), flip
    else:
        return (D1 if flip else D2), ("D1" if flip else "D2"), flip

def item_orders_for_subject(subj_id: str, session: str):
    seed, id_in_pair = get_pair_seed(subj_id)
    rng = np.random.default_rng(seed)
    order_m = rng.permutation(np.arange(1, 11))
    order_r = rng.permutation(np.arange(1, 11))

    if session == "01":
        if id_in_pair == 0:
            this_m = order_m[0:5]
            this_r = order_r[0:5]
        else:
            this_m = order_m[5:10]
            this_r = order_r[5:10]
    else:
        if id_in_pair == 0:
            this_m = order_m[5:10]
            this_r = order_r[5:10]
        else:
            this_m = order_m[0:5]
            this_r = order_r[0:5]
    return this_m, this_r


# Main task
def run_task(subject, session, language, demo, run_number):

    # get directories
    path_to_config = pathlib.Path(__file__).parent.parent
    filename = os.path.join(path_to_config, "config.json")
    configDirs = getConfig(filename)
    stimDir = os.path.join(configDirs['io_root_dir'], "stimuli", "social")

    # task name
    task = 'task-social_lang-{lang}_run-{r}'.format(lang=language, r=run_number)
    
    # Define keys
    setKeys = define_keys('0', '5', ['1','2', '3']) # social, not sure, no interaction
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
    rootLog = os.path.join(configDirs['io_root_dir'], "logs", "social")
    logName = 'sub-{subj}_ses-{sess}_{task}_{dt}.log'.format(subj=subject, sess=session, task=task, dt=datetimestr)
    log_filename = os.path.join(rootLog, logName)
    logFile = logging.LogFile(log_filename, level=logging.EXP)

    # set design for this run
    design, design_label, flip_flag = pick_design_for_run(int(run_number), subject)
    trialsPerRun = len(design)

    # set item order
    order_m_all, order_r_all = item_orders_for_subject(subject, session)
    if run_number == '1':
        items_m_run = order_m_all[:2].tolist()
        items_r_run = order_r_all[:3].tolist()
    else:
        items_m_run = order_m_all[2:].tolist()
        items_r_run = order_r_all[3:].tolist()

    # set prefixes and timing 
    condPrefs = ['mental', 'random']

    # demo
    if demo == 'demo':
        n_loops = range(1)
        fixDur = 2.0
        questDur = 3.0
    else:
        n_loops = range(trialsPerRun)    
        fixDur = 15.0
        questDur = 3.0

    # define behavioral arrays
    key_vec = [0] * trialsPerRun
    RT_vec = [0.0] * trialsPerRun
    items = [0] * trialsPerRun
    fix_onsets = [0.0] * trialsPerRun
    clip_onsets = [0.0] * trialsPerRun
    clip_duration = [0.0] * trialsPerRun
    question_onsets = [0.0] * trialsPerRun
    trialsOnsets = clip_onsets  # kept for compatibility

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
    instructionsFile = 'social_{lang}_instructions.txt'.format(lang=language)
    instructions_path = os.path.join(configDirs['io_root_dir'], 'instructions', instructionsFile)
    Txt.setText(open(instructions_path, 'r', encoding='utf-8').read())
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY instructions')
    win.flip()
    event.waitKeys(keyList=responseKey)

    # question: always the same
    quest_path = os.path.join(stimDir, f"response_screen_{language}.txt")
    
    # launch scan
    Trigger(mainClock, Txt, win, triggerKey)

    # Start experiment
    #event.clearEvents()
    used_m = used_r = 0
    clock_global = core.Clock()
    experimentStart = clock_global.getTime()

    try:
        for trial_idx in n_loops:
            # Fixation
            fixation.draw()
            win.logOnFlip(level=logging.EXP, msg='DISPLAY first fixation')
            win.flip()
            fix_onsets[trial_idx] = clock_global.getTime() - experimentStart
            fix_start = clock_global.getTime()
            while (clock_global.getTime() - fix_start) < fixDur:
                core.wait(0.01)

            # Determine condition + item
            trialT = design[trial_idx]
            if trialT == 1:
                numbeT = items_m_run[used_m]; used_m += 1
            else:
                numbeT = items_r_run[used_r]; used_r += 1
            items[trial_idx] = numbeT

            pref = condPrefs[trialT - 1]
            clip = os.path.join(stimDir, f"{pref}_{numbeT}.AVI")

            # Play until movie finishes or user presses a key
            dims = getDimensions(clip)
            targetWidth = 1024
            aspectRatio = dims[0] / dims[1]
            targetHeight = round(targetWidth / aspectRatio)
            this_message = 'DISPLAY clip: {numStim}_{cond}'.format(numStim=items[trial_idx], cond=design[trial_idx])
            win.logOnFlip(level=logging.EXP, msg=this_message)
            movie = visual.MovieStim(win, clip, loop=False, noAudio=False, name=f"{pref}_{numbeT}.AVI", size=(targetWidth,targetHeight))
            this_movie_duration = movie.duration
            clip_duration[trial_idx] = this_movie_duration
            movieOn = mainClock.getTime() # onset time
            movie.play()

            demo_end_time = movieOn + 5 if demo == 'demo' else float('inf')  # set the end time for the demo condition
            while movie.isPlaying and mainClock.getTime() < demo_end_time:
                movie.draw()
                win.flip()
                if breakKey[0] in event.getKeys():
                    break

            movie.stop()
            core.wait(0.005)

            # Response
            win.logOnFlip(level=logging.EXP, msg='OFF story')
            win.flip()
            question_onsets[trial_idx] = clock_global.getTime() - experimentStart
            Txt.setText(open(quest_path, 'r', encoding='utf-8').read())
            Txt.draw()
            this_message = 'DISPLAY question'
            win.logOnFlip(level=logging.EXP, msg=this_message)
            win.flip()

            # Response window
            response_start = clock_global.getTime()
            got_first = False
            key_vec[trial_idx] = 0
            RT_vec[trial_idx] = 0.0
            keyList = list(responseKey) + list(breakKey)

            while (clock_global.getTime() - response_start) < questDur:
                keys = event.getKeys(keyList=keyList, timeStamped=False)
                if keys:
                    if breakKey in keys:
                        raise KeyboardInterrupt
                    if not got_first:
                        if responseKey[0] in keys:
                            key_vec[trial_idx] = 1
                            RT_vec[trial_idx] = clock_global.getTime() - response_start
                            got_first = True
                        elif responseKey[1] in keys:
                            key_vec[trial_idx] = 2
                            RT_vec[trial_idx] = clock_global.getTime() - response_start
                            got_first = True
                core.wait(0.005)

            # Backup CSV
            tmp_csvName = 'sub-{subj}_ses-{sess}_{task}_{dt}_backup.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
            tmp_csv_filename = os.path.join(rootLog, tmp_csvName)
            save_csv(pathlib.Path(tmp_csv_filename), design, items, key_vec, RT_vec,
                     fix_onsets, clip_onsets, clip_duration, question_onsets)

        # Final fixation
        fixation.draw(); 
        win.logOnFlip(level=logging.EXP, msg='DISPLAY final fixation')
        win.flip()
        fix_end_start = clock_global.getTime()
        while (clock_global.getTime() - fix_end_start) < fixDur:
            core.wait(0.01)

        # Final save
        experimentEnd = clock_global.getTime()
        experimentDuration = experimentEnd - experimentStart
        meta = {
            "design_used_this_run": design_label,
            "subject_flip_flag": str(int(flip_flag)),
            "item_order_mental_all": ",".join(map(str, item_orders_for_subject(subject, session)[0])),
            "item_order_random_all": ",".join(map(str, item_orders_for_subject(subject, session)[1])),
            "items_mental_used_this_run": ",".join(map(str, items_m_run)),
            "items_random_used_this_run": ",".join(map(str, items_r_run)),
        }
          
        # need to calculate ips somewhere here as video durations are not perfectly 20s.
        total_vids_dur = sum(clip_duration)
        ips = ((trialsPerRun) * (fixDur + total_vids_dur + questDur) + (fixDur)) / 2.0

        final_csv = 'sub-{subj}_ses-{sess}_{task}_{dt}.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
        final_csv_filename = os.path.join(rootLog, final_csv)
        save_csv(pathlib.Path(final_csv_filename), design, items, key_vec, RT_vec,
                 fix_onsets, clip_onsets, clip_duration, question_onsets,
                 experiment_duration=experimentDuration, ips=ips, meta=meta)
        print(f"Final data saved to {final_csv}")

    except KeyboardInterrupt:
        abort_csv = 'sub-{subj}_ses-{sess}_{task}_{dt}_ABORT.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
        abort_csv_filename = os.path.join(rootLog, abort_csv)
        save_csv(pathlib.Path(abort_csv_filename), design, items, key_vec, RT_vec,
                 fix_onsets, clip_onsets, clip_duration, question_onsets)
        print(f"Experiment aborted, partial data saved to {abort_csv}")
        event.clearEvents(); win.close(); core.quit()

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