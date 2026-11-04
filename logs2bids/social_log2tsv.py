################################################################
## log to tsv conversion for task: social
##
## example usage:
"""
python social_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    023 \
    02 \
    1 \
    1p9mm
"""
## Rows: fixation (condition n/a), stimulus (clip) and response (question
## screen, condition of the clip before it), each with the duration it was
## shown. response_time is the time of the first keypress after the question
## appeared. accuracy: 1 = mental clip answered "1" (social) or random clip
## answered "3" (no interaction), 0 = any other answer, n/a = no answer.
## Shared rules: log2tsv_common.py (same folder).
################################################################

import numpy as np

from log2tsv_common import check_durations, cli, story_task_events, write_events

TASK = "social"
CONDITIONS = {"1": "mental", "2": "random"}              # 'DISPLAY clip: <item>_<code>'
CORRECT_KEY = {"mental": "1", "random": "3"}             # keys: 1 social, 2 not sure, 3 no interaction
EXPECTED = {"fixation": 15.0, "response": 3.0}           # social.py: fixDur, questDur (clips vary in length)

if __name__ == "__main__":
    infile, out_file = cli(TASK)
    events = story_task_events(infile, "clip", CONDITIONS)
    resp = events["trial_type"] == "response"
    answered = resp & events["response"].notna()
    events["accuracy"] = np.nan
    events.loc[answered, "accuracy"] = (
        events.loc[answered, "response"] == events.loc[answered, "condition"].map(CORRECT_KEY)
    ).astype(int)
    check_durations(events, EXPECTED, source=infile)
    print(f"wrote {write_events(events, out_file)}")
