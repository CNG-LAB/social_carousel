################################################################
## log to tsv conversion for task: emomatch
##
## example usage (the .log and .csv of a run share their name; give either):
"""
python emomatch_log2tsv.py \
    /path/to/sub-023_ses-02_task-emomatch_lang-de_run-1_<date>.csv \
    /output/tsv/here \
    023 \
    02 \
    1 \
    1p9mm
"""
## Timing of every screen comes from the PsychoPy log; responses, accuracy
## and stimulus files from the task's csv (matched trial by trial; the script
## stops if trial counts or conditions disagree). Rows:
##   fixation  fixation cross at the start and end of the run (condition n/a)
##   rest      'PAUSE' screen after each block                 (condition n/a)
##   cue       'get ready' and block-instruction screens       (condition cue)
##   stimulus  matching trials: condition checker / gender / emotion, with
##             response, response_time (s) and accuracy from the csv
##             (n/a when no key was pressed)
## Fixation and rest are left unmodelled by the first level (the baseline);
## cue screens are modelled as their own regressor.
## Shared rules: log2tsv_common.py (same folder).
################################################################

from pathlib import Path

import numpy as np
import pandas as pd

from log2tsv_common import (after_trigger, check_durations, cli, read_log, screens,
                            write_events)

TASK = "emomatch"
CONDITIONS = {"checker": "checker", "gender": "gender", "emo": "emotion"}  # log 'trial condition <x>'
CSV_CODES = {0: "checker", 1: "gender", 2: "emotion"}                      # csv condition(0=checker,1=gender,2=emo)
# emomatch.py: fixDur, restDur, readyDur, introBlockDur, stimDur
EXPECTED = {"fixation": 8.0, "rest": 12.0, "get_ready": 2.0, "instructions": 3.0, "stimulus": 1.5}
EXTRA_COLUMNS = ["trial_number", "target_location", "probe_id", "foil_id", "target_id"]


def log_and_csv(infile):
    p = Path(infile)
    log, csv = p.with_suffix(".log"), p.with_suffix(".csv")
    for f in (log, csv):
        if not f.exists():
            raise FileNotFoundError(f"{f} not found (the .log and .csv of a run must share their name)")
    return log, csv


def emomatch_events(log_path, csv_path):
    sc = screens(after_trigger(read_log(log_path), "fixation"))
    beh = pd.read_csv(csv_path)
    cond_col = next(c for c in beh.columns if c.startswith("condition"))

    trials = sc[sc["label"].str.startswith("trial condition ")].reset_index(drop=True)
    log_cond = trials["label"].str.split().str[-1].map(CONDITIONS)
    csv_cond = beh[cond_col].map(CSV_CODES)
    if len(trials) != len(beh) or not (log_cond.values == csv_cond.values).all():
        raise ValueError(f"log ({len(trials)} trials) and csv ({len(beh)} rows) do not match trial by trial: "
                         f"{log_path} / {csv_path}")
    lag = (trials["onset"] - beh["trialOnsetTime"]).abs().max()
    if lag > 0.05:
        raise ValueError(f"log and csv trial onsets differ by up to {lag:.3f} s: not the same run?")

    answered = beh["keyPress"].isin([1, 2])
    trial_rows = pd.DataFrame({
        "onset": trials["onset"], "duration": trials["duration"], "trial_type": "stimulus",
        "condition": log_cond,
        "response": beh["keyPress"].where(answered).astype("Int64").astype("string"),
        "response_time": beh["RT(s)"].where(answered),
        "accuracy": beh["accuracy"].where(answered),
        "stimulus_id": beh["probeFileName"],
        "trial_number": beh["condTrialNumber"], "target_location": beh["targetLocation"],
        "probe_id": beh["probeFileName"], "foil_id": beh["foilFileName"], "target_id": beh["targetFileName"],
    })

    other = []
    trial_onsets = trials["onset"].to_numpy()
    for s in sc.itertuples(index=False):
        if s.label == "fixation":
            other.append(dict(onset=s.onset, duration=s.duration, trial_type="fixation", stimulus_id="cross"))
        elif s.label == "rest":
            other.append(dict(onset=s.onset, duration=s.duration, trial_type="rest", stimulus_id="pause_screen"))
        elif s.label == "get ready":
            other.append(dict(onset=s.onset, duration=s.duration, trial_type="cue", condition="cue",
                              stimulus_id="get_ready"))
        elif s.label == "block start":
            nxt = np.searchsorted(trial_onsets, s.onset)       # the block this screen announces
            block = log_cond.iloc[nxt] if nxt < len(log_cond) else "unknown"
            other.append(dict(onset=s.onset, duration=s.duration, trial_type="cue", condition="cue",
                              stimulus_id=f"{block}_instructions"))
    events = pd.concat([pd.DataFrame(other), trial_rows], ignore_index=True)
    if events["duration"].isna().any():
        raise ValueError(f"{log_path}: an event has no end: was the run aborted?")
    return events.sort_values("onset", kind="stable", ignore_index=True)


if __name__ == "__main__":
    infile, out_file = cli(TASK, usage_infile="/path/to/run.csv")
    log_path, csv_path = log_and_csv(infile)
    events = emomatch_events(log_path, csv_path)
    check = events.assign(kind=np.where(events["trial_type"] == "cue",
                                        np.where(events["stimulus_id"] == "get_ready", "get_ready", "instructions"),
                                        events["trial_type"]))
    check_durations(check, EXPECTED, by="kind", source=str(log_path))
    print(f"wrote {write_events(events, out_file, extra_columns=EXTRA_COLUMNS)}")
