################################################################
## log to tsv conversion for task: movie watching
##
## example usage (the movie name is the BIDS task label, e.g. lotr):
"""
python movie_log2tsv.py \
    /path/to/log.log \
    /output/tsv/here \
    023 \
    02 \
    lotr \
    1p9mm
"""
## Rows: fixation (condition n/a) and movie (condition movie, stimulus_id =
## the movie name), each with the duration it was shown: until the next screen
## change in the log (e.g. the end screen). No responses: response,
## response_time and accuracy are n/a.
## Shared rules: log2tsv_common.py (same folder).
################################################################

from log2tsv_common import check_counts, events_file, parse_args, passive_task_events, write_events

if __name__ == "__main__":
    a = parse_args("movie_log2tsv.py", ["infile", "outpath", "sub", "ses", "movie", "acq"],
                   "/path/to/log.log /output/tsv/here 023 02 lotr 1p9mm")
    events = passive_task_events(a["infile"], "fixation cross", {
        "fixation cross": dict(trial_type="fixation", stimulus_id="cross"),
        "movie": dict(trial_type="movie", condition="movie", stimulus_id=a["movie"]),
    })
    check_counts(events, {"movie": 1}, source=a["infile"])
    out_file = events_file(a["outpath"], a["sub"], a["ses"], a["movie"], a["acq"])
    print(f"wrote {write_events(events, out_file)}")
