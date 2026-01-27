################################################################
## log to tsv conversion for task: emoinf
## 
## example usage:
"""
python emoinf_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    pilot06 \
    02 \
    02
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
run = sys.argv[5]

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
mask = df_log["event_details"].eq("DISPLAY first fixation")
if mask.any():
    first_idx = mask.idxmax()  # index of first True
    df_filter0 = df_log.loc[first_idx:]
else:
    df_filter0 = df_log.copy()  # or raise an error if this must exist
# 0.2 Remove last row (keypress to end task)
df_filter0 = df_filter0.iloc[:-1]

# 1) Fixation cross filter
df_fixation = df_filter0[
    df_filter0["event_details"].isin(["DISPLAY first fixation", "OFF first fixation", 'DISPLAY final fixation', 'DISPLAY end'])
]

# 2) Questions on/off filter
df_question = df_filter0[
    df_filter0["event_details"].str.startswith(("DISPLAY story"), na=False) | 
    df_filter0["event_details"].isin(["OFF story"])
]

# 3) Response filter
df_response = df_filter0[
    df_filter0["event_details"].str.startswith(("DISPLAY question"), na=False) |
    df_filter0["event_details"].str.contains(r"Keypress:\s*(?!5)\S+", regex=True, na=False)
]

# Here, force the df to have the format display - reponse - display - response - etc to account for randomly pressed buttons.
# If a button is pressed before the first response screen is shown, it is discarded. 
first_display_idx = df_response[df_response['event_details'] == 'DISPLAY question'].first_valid_index()
df_response = df_response.loc[first_display_idx:]
# test: df_response = df_response.drop(258)

# In case of multiple button presses after a response screen is shown, we only consider the first. 
display_mask = df_response['event_details'] == 'DISPLAY question'
# Create a cumulative sum of DISPLAY question occurrences to group rows
group_ids = display_mask.cumsum()
# Create a new df with the grouping
df_with_groups = df_response.copy()
df_with_groups['group_id'] = group_ids
# For each group, keep only the first Keypress row (if any)
result_rows = []
for group_id, group_df in df_with_groups.groupby('group_id'):
    # Get the first DISPLAY question row (always keep it)
    display_row = group_df[group_df['event_details'] == 'DISPLAY question']
    # Get Keypress rows in this group
    keypress_rows = group_df[group_df['event_details'].str.startswith('Keypress:')]
    # Keep the first Keypress row if it exists
    if not keypress_rows.empty:
        first_keypress = keypress_rows.iloc[0:1]  # First row only
        # Combine display row and first keypress row
        group_result = pd.concat([display_row, first_keypress])
    else:
        # If no keypress rows, put -1
        keypress_tmp = display_row.copy()
        keypress_tmp["event_type"] = "DATA"
        keypress_tmp["event_details"] = "Keypress: -1"
        group_result = pd.concat([display_row, keypress_tmp])
    result_rows.append(group_result)

# Combine all results
df_filtered = pd.concat(result_rows)
# Remove the temporary group_id column
df_response = df_filtered.drop('group_id', axis=1)


## reformat fixation dataframe
df_fixation_rf = pd.DataFrame(columns=["onset", "duration", "trial_type", "condition", "response", "accuracy", "stimulus_id"])
mask = df_fixation["event_details"].eq("DISPLAY first fixation") | df_fixation["event_details"].eq("DISPLAY final fixation")
df_fixation_rf["onset"] = df_fixation.loc[mask==True,"time"]
df_fixation_rf["duration"] = df_fixation.loc[mask==False,"time"].values - df_fixation.loc[mask==True,"time"].values
df_fixation_rf["trial_type"] = "fixation"
df_fixation_rf["condition"] = "fixation"
df_fixation_rf["response"] = "na"
df_fixation_rf["accuracy"] = "na"
df_fixation_rf["stimulus_id"] = "cross"


## reformat questions dataframe
df_question_rf = pd.DataFrame(columns=["onset", "duration", "trial_type", "condition", "response", "accuracy", "stimulus_id"])
mask = df_question["event_details"].str.startswith(("DISPLAY story"), na=False)
df_question_rf["onset"] = df_question.loc[mask==True,"time"]
df_question_rf["duration"] = df_question.loc[mask==False,"time"].values - df_question.loc[mask==True,"time"].values
df_question_rf["trial_type"] = "stimulus"
condition_full = df_question.loc[mask==True,"event_details"].values
last_chars = [s[-1] for s in condition_full]
df_question_rf["condition"] = ['emotional' if x == '1' else 'physical' for x in last_chars]
df_question_rf["response"] = "na"
df_question_rf["accuracy"] = "na"
item_number = [s.split('_')[0].split()[-1] for s in condition_full]
df_question_rf["stimulus_id"] = item_number


## reformat response dataframe
df_response_rf = pd.DataFrame(columns=["onset", "duration", "trial_type", "condition", "response", "accuracy", "stimulus_id"])
mask = df_response["event_details"].str.startswith(("DISPLAY"), na=False)
df_response_rf["onset"] = df_response.loc[mask==True,"time"]
df_response_rf["duration"] = df_response.loc[mask==False,"time"].values - df_response.loc[mask==True,"time"].values
df_response_rf["trial_type"] = "response"
df_response_rf["condition"] = df_question_rf["condition"].values
response_full = df_response.loc[mask==False,"event_details"].values
df_response_rf["response"] = [s[-1] for s in response_full]
df_response_rf["accuracy"] = "na" 
df_response_rf["stimulus_id"] = "resp_screen" 


## Merge the dfs
df_bids = pd.concat([df_fixation_rf, df_question_rf, df_response_rf], ignore_index=False)

# Reset index to show original row numbers as a column
df_bids = df_bids.reset_index()
df_bids = df_bids.rename(columns={'index': 'original_row_number'})
df_bids = df_bids.sort_values('original_row_number').reset_index(drop=True)
df_bids = df_bids.drop(columns=['original_row_number'])

## Write to tsv
out_file = '{out_here}/{id_here}_task-emoinf_run-{run_here}_events.tsv'.format(out_here=outpath, id_here=bids_id, run_here=run)
df_bids.to_csv(out_file, sep='\t', index=False)
