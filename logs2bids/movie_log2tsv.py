################################################################
## log to tsv conversion for task: movie
## 
## example usage:
"""
python movie_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    pilot06 \
    02 \
    lotr \
    1p9mm
"""
################################################################

## libraries and functions
import sys
import pandas as pd
import numpy as np

## Read inputs
infile = sys.argv[1] 
outpath = sys.argv[2]
subj = sys.argv[3]
ses = sys.argv[4]
movie = sys.argv[5]
acq = sys.argv[6]

# log parser
def read_log_to_dataframe(log_file_path):
    data = []
    with open(log_file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            # Split into at most 3 parts (time, event_type, details)
            parts = line.split(maxsplit=2)
            if len(parts) != 3:
                # Skip or handle malformed lines
                continue
            time_str, event_type, event_details = parts
            try:
                time_val = float(time_str)
            except ValueError:
                time_val = None  # or continue to skip bad lines
            data.append({
                "time": time_val,
                "event_type": event_type,
                "event_details": event_details
            })
    df = pd.DataFrame(data, columns=["time", "event_type", "event_details"])
    return df

## Read task log
df_log = read_log_to_dataframe(infile)
bids_id = 'sub-{subject}_ses-{session}'.format(subject=subj, session=ses)

## Clean up df_log: filter each component then reorder by onset time.

# 0) Common to all:
# 0.1 remove everything before "DISPLAY first fixation" (scan not yet started)
mask = df_log["event_details"].eq("DISPLAY fixation cross")
if mask.any():
    first_idx = mask.idxmax()  # index of first True
    df_filter0 = df_log.loc[first_idx:]
else:
    df_filter0 = df_log.copy()  # or raise an error if this must exist
# 0.2 Remove last row (keypress to end task)
df_filter0 = df_filter0.iloc[:-1]

# 1) all events filter
df_fixation = df_filter0[
    df_filter0["event_details"].isin(["DISPLAY fixation cross", "DISPLAY movie", "DISPLAY end"])
]

## reformat dataframe
df_fixation_rf = pd.DataFrame(columns=["onset", "duration", "trial_type", "condition", "response", "accuracy", "stimulus_id"])

mask_onset_cross = df_fixation["event_details"].eq("DISPLAY fixation cross")
mask_onset_movie = df_fixation["event_details"].eq("DISPLAY movie")
mask_end = df_fixation["event_details"].eq("DISPLAY end")

onset1 = df_fixation.loc[mask_onset_cross==True,"time"]
onset2 = df_fixation.loc[mask_onset_movie==True,"time"]
df_fixation_rf["onset"] = np.concatenate([onset1, onset2])

duration1 = df_fixation.loc[mask_onset_movie==True,"time"].values - df_fixation.loc[mask_onset_cross==True,"time"].values
duration2 = df_fixation.loc[mask_end==True,"time"].values - df_fixation.loc[mask_onset_movie==True,"time"].values
df_fixation_rf["duration"] = np.concatenate([duration1, duration2])

df_fixation_rf["trial_type"] = ["fixation", "movie"]
df_fixation_rf["condition"] = ["fixation", "movie"]
df_fixation_rf["response"] = ["na", "na"]
df_fixation_rf["accuracy"] = ["na", "na"]
df_fixation_rf["stimulus_id"] = ["cross", movie]


## rename for simplicity
df_bids = df_fixation_rf


## Write to tsv
out_file = '{out_here}/{id_here}_task-{movie_here}_acq-{acq_here}_events.tsv'.format(out_here=outpath, id_here=bids_id, movie_here=movie, acq_here=acq)
df_bids.to_csv(out_file, sep='\t', index=False)