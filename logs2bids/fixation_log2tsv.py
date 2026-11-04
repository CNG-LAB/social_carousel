################################################################
## log to tsv conversion for task: rest (fixation)
##
## example usage:
"""
python fixation_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    023 \
    02 \
    1p9mm
"""
## Rows: fixation (condition n/a), with the duration it was shown: until the
## next screen change in the log (e.g. the end screen). No responses:
## response, response_time and accuracy are n/a. Output: task-rest.
## Shared rules: log2tsv_common.py (same folder).
################################################################

from log2tsv_common import check_counts, events_file, parse_args, passive_task_events, write_events

if __name__ == "__main__":
    a = parse_args("fixation_log2tsv.py", ["infile", "outpath", "sub", "ses", "acq"],
                   "/path/to/log.log /output/tsv/here 023 02 1p9mm")
    events = passive_task_events(a["infile"], "fixation cross", {
        "fixation cross": dict(trial_type="fixation", stimulus_id="cross"),
    })
    check_counts(events, {"fixation": 1}, source=a["infile"])
    out_file = events_file(a["outpath"], a["sub"], a["ses"], "rest", a["acq"])
    print(f"wrote {write_events(events, out_file)}")
