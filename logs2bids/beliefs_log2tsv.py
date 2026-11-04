################################################################
## log to tsv conversion for task: beliefs
##
## example usage:
"""
python beliefs_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    023 \
    02 \
    1 \
    1p9mm
"""
## Rows: fixation (condition n/a), stimulus (story) and response (question
## screen), each with the duration it was shown. response_time is the time of
## the first keypress after the question appeared; n/a without a keypress.
## Shared rules: log2tsv_common.py (same folder).
################################################################

from log2tsv_common import check_durations, cli, story_task_events, write_events

TASK = "beliefs"
CONDITIONS = {"1": "belief", "2": "photo"}               # 'DISPLAY story: <item>_<code>'
EXPECTED = {"fixation": 12.0, "stimulus": 15.0, "response": 5.0}   # beliefs.py: fixDur, storyDur, questDur

if __name__ == "__main__":
    infile, out_file = cli(TASK)
    events = story_task_events(infile, "story", CONDITIONS, response_item=True)
    check_durations(events, EXPECTED, source=infile)
    print(f"wrote {write_events(events, out_file)}")
