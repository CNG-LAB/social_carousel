# beliefs.py
# Saxe false beliefs

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
def subject_seed(subj_id: str) -> int:
    """Deterministic seed based on subjID (stable across runs/machines)."""
    h = hashlib.md5(subj_id.encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def pick_design_for_run(run: int, subj_id: str):
    """Half of subjects get D1 in run1, half D2 in run1 (deterministic)."""
    D1 = [1, 2, 2, 1, 2, 1, 2, 1, 1, 2]
    D2 = [2, 1, 2, 1, 1, 2, 2, 1, 2, 1]
    flip = (subject_seed(subj_id) % 2) == 1
    if run == 1:
        return (D2 if flip else D1), ("D2" if flip else "D1"), flip
    else:
        return (D1 if flip else D2), ("D1" if flip else "D2"), flip

def item_orders_for_subject(subj_id: str):
    """Deterministic item order per condition (1..10) for this subject."""
    rng = np.random.default_rng(subject_seed(subj_id))
    order_b = rng.permutation(np.arange(1, 11))
    order_p = rng.permutation(np.arange(1, 11))
    return order_b, order_p


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

    # # set design for this run
    # design, design_label, flip_flag = pick_design_for_run(int(run_number), subject)
    # trialsPerRun = len(design)

    # # set item order
    # order_b_all, order_p_all = item_orders_for_subject(subject)
    # if run_number == '1':
    #     items_b_run = order_b_all[:5].tolist()
    #     items_p_run = order_p_all[:5].tolist()
    # else:
    #     items_b_run = order_b_all[5:].tolist()
    #     items_p_run = order_p_all[5:].tolist()

    # # set prefixes and timing 
    # condPrefs = ['b', 'p']

    # # demo
    # if demo == 'demo':
    #     n_loops = range(1)
    #     fixDur = 2
    #     storyDur = 4 
    #     questDur = 2 
    # else:
    #     n_loops = range(trialsPerRun)    
    #     fixDur = 12.0
    #     storyDur = 10.0
    #     questDur = 4.0

    # # define behavioral arrays
    # key_vec = [0] * trialsPerRun
    # RT_vec = [0.0] * trialsPerRun
    # items = [0] * trialsPerRun
    # fix_onsets = [0.0] * trialsPerRun
    # story_onsets = [0.0] * trialsPerRun
    # question_onsets = [0.0] * trialsPerRun
    # trialsOnsets = story_onsets  # kept for compatibility

    # ips = ((trialsPerRun) * (fixDur + storyDur + questDur) + (fixDur)) / 2.0

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
    if run_number == '1':
        instructionsFile = 'emomatch_faces_{lang}_instructions.txt'.format(lang=language)
    else:
        instructionsFile = 'emomatch_shapes_{lang}_instructions.txt'.format(lang=language) 
    instructions_path = os.path.join(configDirs['io_root_dir'], 'instructions', instructionsFile)
    Txt.setText(open(instructions_path, 'r').read())
    Txt.draw()
    win.logOnFlip(level=logging.EXP, msg='DISPLAY instructions')
    win.flip()
    event.waitKeys(keyList=responseKey)
    
    # launch scan
    Trigger(mainClock, Txt, win, triggerKey)

    # # Start experiment
    # #event.clearEvents()
    # used_b = used_p = 0
    # clock_global = core.Clock()
    # experimentStart = clock_global.getTime()

    # try:
    #     for trial_idx in n_loops:
    #         # Fixation
    #         fixation.draw()
    #         win.logOnFlip(level=logging.EXP, msg='DISPLAY first fixation')
    #         win.flip()
    #         fix_onsets[trial_idx] = clock_global.getTime() - experimentStart
    #         fix_start = clock_global.getTime()
    #         while (clock_global.getTime() - fix_start) < fixDur:
    #             core.wait(0.01)

    #         # Determine condition + item
    #         trialT = design[trial_idx]
    #         if trialT == 1:
    #             numbeT = items_b_run[used_b]; used_b += 1
    #         else:
    #             numbeT = items_p_run[used_p]; used_p += 1
    #         items[trial_idx] = numbeT

    #         pref = condPrefs[trialT - 1]
    #         story_path = os.path.join(stimDir, f"{numbeT}{pref}_story_{language}.txt")
    #         quest_path = os.path.join(stimDir, f"{numbeT}{pref}_question_{language}.txt")

    #         # Story
    #         win.logOnFlip(level=logging.EXP, msg='OFF first fixation')
    #         win.flip()
    #         story_onsets[trial_idx] = clock_global.getTime() - experimentStart
    #         Txt.setText(open(story_path, 'r').read())
    #         Txt.draw()
    #         win.logOnFlip(level=logging.EXP, msg='DISPLAY story')
    #         win.flip()
    #         story_start_abs = clock_global.getTime()
    #         while (clock_global.getTime() - story_start_abs) < storyDur:
    #             core.wait(0.005)

    #         # Question
    #         win.logOnFlip(level=logging.EXP, msg='OFF story')
    #         win.flip()
    #         question_onsets[trial_idx] = clock_global.getTime() - experimentStart
    #         Txt.setText(open(quest_path, 'r').read())
    #         Txt.draw()
    #         win.logOnFlip(level=logging.EXP, msg='DISPLAY question')
    #         win.flip()

    #         # Response window
    #         response_start = clock_global.getTime()
    #         got_first = False
    #         key_vec[trial_idx] = 0
    #         RT_vec[trial_idx] = 0.0
    #         keyList = list(responseKey) + list(breakKey)

    #         while (clock_global.getTime() - response_start) < questDur:
    #             keys = event.getKeys(keyList=keyList, timeStamped=False)
    #             if keys:
    #                 if breakKey in keys:
    #                     raise KeyboardInterrupt
    #                 if not got_first:
    #                     if responseKey[0] in keys:
    #                         key_vec[trial_idx] = 1
    #                         RT_vec[trial_idx] = clock_global.getTime() - response_start
    #                         got_first = True
    #                     elif responseKey[1] in keys:
    #                         key_vec[trial_idx] = 2
    #                         RT_vec[trial_idx] = clock_global.getTime() - response_start
    #                         got_first = True
    #             core.wait(0.005)

    #         # Backup CSV
    #         tmp_csvName = 'sub-{subj}_ses-{sess}_{task}_{dt}_backup.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
    #         tmp_csv_filename = os.path.join(rootLog, tmp_csvName)
    #         save_csv(pathlib.Path(tmp_csv_filename), design, items, key_vec, RT_vec,
    #                  fix_onsets, story_onsets, question_onsets)

    #     # Final fixation
    #     fixation.draw(); 
    #     win.logOnFlip(level=logging.EXP, msg='DISPLAY final fixation')
    #     win.flip()
    #     fix_end_start = clock_global.getTime()
    #     while (clock_global.getTime() - fix_end_start) < fixDur:
    #         core.wait(0.01)

    #     # Final save
    #     experimentEnd = clock_global.getTime()
    #     experimentDuration = experimentEnd - experimentStart
    #     meta = {
    #         "design_used_this_run": design_label,
    #         "subject_flip_flag": str(int(flip_flag)),
    #         "item_order_belief_all": ",".join(map(str, item_orders_for_subject(subject)[0])),
    #         "item_order_photo_all": ",".join(map(str, item_orders_for_subject(subject)[1])),
    #         "items_b_used_this_run": ",".join(map(str, items_b_run)),
    #         "items_p_used_this_run": ",".join(map(str, items_p_run)),
    #     }
    #     final_csv = 'sub-{subj}_ses-{sess}_{task}_{dt}.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
    #     final_csv_filename = os.path.join(rootLog, final_csv)
    #     save_csv(pathlib.Path(final_csv_filename), design, items, key_vec, RT_vec,
    #              fix_onsets, story_onsets, question_onsets,
    #              experiment_duration=experimentDuration, ips=ips, meta=meta)
    #     print(f"Final data saved to {final_csv}")

    # except KeyboardInterrupt:
    #     abort_csv = 'sub-{subj}_ses-{sess}_{task}_{dt}_ABORT.csv'.format(subj=subject, sess=session, task=task, dt=datetimestr)
    #     abort_csv_filename = os.path.join(rootLog, abort_csv)
    #     save_csv(pathlib.Path(abort_csv_filename), design, items, key_vec, RT_vec,
    #              fix_onsets, story_onsets, question_onsets)
    #     print(f"Experiment aborted, partial data saved to {abort_csv}")
    #     event.clearEvents(); win.close(); core.quit()

    # # display end of task screen
    # endFile = '{lang}_end.txt'.format(lang=language)
    # end_path = os.path.join(configDirs['io_root_dir'], "instructions", endFile)
    # with open(end_path, 'r') as f:
    #     Txt.setText(f.read())
    # Txt.draw()
    # win.logOnFlip(level=logging.EXP, msg='DISPLAY end')
    # win.flip()
    # event.waitKeys(keyList=breakKey)
    # core.wait(0.1)
    
    # clean up
    event.clearEvents()
    win.close()
    core.quit()