################################################################
## log to tsv conversion for task: emoinf
##
## example usage:
"""
python emoinf_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    023 \
    02 \
    1 \
    1p9mm
"""
## Rows: fixation (condition n/a), stimulus (story) and response (rating
## screen, condition of the story before it), each with the duration it was
## shown. response_time is the time of the first keypress after the rating
## screen appeared; n/a without a keypress.
## Shared rules: log2tsv_common.py (same folder).
################################################################

from log2tsv_common import check_durations, cli, story_task_events, write_events

TASK = "emoinf"
CONDITIONS = {"1": "emotional", "2": "physical"}         # 'DISPLAY story: <item>_<code>'
EXPECTED = {"fixation": 12.0, "stimulus": 15.0, "response": 5.0}   # emoinf.py: fixDur, storyDur, responseDur

if __name__ == "__main__":
    infile, out_file = cli(TASK)
    events = story_task_events(infile, "story", CONDITIONS)
    check_durations(events, EXPECTED, source=infile)
    print(f"wrote {write_events(events, out_file)}")
