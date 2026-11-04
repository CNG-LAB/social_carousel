"""Shared helpers for the <task>_log2tsv.py scripts (PsychoPy log -> BIDS events.tsv).

Keep this file in the same folder as the four scripts. Rules used for every task:

* Times are those of the PsychoPy log after the scanner trigger: the log's
  clock restarts at the trigger, so onset 0 is the first scanner pulse.
* A screen starts at its "DISPLAY ..." line and lasts until the next screen
  change (the next DISPLAY or OFF line), so ``duration`` is how long it was
  actually shown. Durations are compared with the nominal ones of the task
  script and a warning is printed when they differ by more than 0.5 s.
* A response is the first keypress (other than the scanner trigger "5" and the
  abort key "0") while the response screen is shown. ``response_time`` is
  measured from the onset of that screen. Without a keypress, ``response``,
  ``response_time`` and ``accuracy`` are n/a.
* Missing values are written as n/a, as BIDS requires.
* Fixation has condition n/a: it is not modelled (the implicit baseline).

Tasks with responses use story_task_events (beliefs, emoinf, social) or their
own code (emomatch); runs without responses (rest, movies) use
passive_task_events.
"""

import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

NA = "n/a"
NON_RESPONSE_KEYS = {"5", "0"}   # scanner trigger, abort key
COLUMNS = ["onset", "duration", "trial_type", "condition", "response", "response_time",
           "accuracy", "stimulus_id"]
INTEGER_COLUMNS = ("accuracy", "trial_number", "target_location")
DURATION_TOLERANCE = 0.5         # s


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def read_log(path):
    """PsychoPy log -> DataFrame with columns time, level, msg."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(maxsplit=2)
            if len(parts) != 3:
                continue
            try:
                t = float(parts[0])
            except ValueError:
                continue
            rows.append((t, parts[1], parts[2]))
    return pd.DataFrame(rows, columns=["time", "level", "msg"])


def after_trigger(log, first_screen):
    """The log from the first 'DISPLAY <first_screen>' line on (the first screen after the trigger)."""
    hits = log.index[log["msg"] == f"DISPLAY {first_screen}"]
    if len(hits) == 0:
        raise ValueError(f"no 'DISPLAY {first_screen}' line in the log: is this the right task?")
    return log.loc[hits[0]:].reset_index(drop=True)


def screens(log):
    """One row per screen: onset, duration (until the next screen change) and label
    (the text after 'DISPLAY '). The last screen has no end and gets duration NaN."""
    changes = log[(log["level"] == "EXP") & log["msg"].str.match(r"^(DISPLAY|OFF) ")]
    end = changes["time"].shift(-1)
    shown = changes["msg"].str.startswith("DISPLAY ")
    out = pd.DataFrame({
        "onset": changes.loc[shown, "time"],
        "duration": (end - changes["time"])[shown],
        "label": changes.loc[shown, "msg"].str[len("DISPLAY "):],
    })
    return out.reset_index(drop=True)


def keypresses(log):
    """Keypresses that can be responses: time and key."""
    key = log["msg"].str.extract(r"^Keypress:\s*(\S+)$")[0]
    out = log.assign(key=key).dropna(subset=["key"])
    return out.loc[~out["key"].isin(NON_RESPONSE_KEYS), ["time", "key"]].reset_index(drop=True)


def first_response(keys, onset, duration):
    """First keypress while a screen is shown -> (key, response_time), or (NaN, NaN)."""
    sel = keys[(keys["time"] >= onset) & (keys["time"] < onset + duration)]
    if sel.empty:
        return np.nan, np.nan
    return sel["key"].iloc[0], sel["time"].iloc[0] - onset


# ---------------------------------------------------------------------------
# fixation -> stimulus -> response screen tasks (beliefs, emoinf, social)
# ---------------------------------------------------------------------------

STIM_LABEL = re.compile(r"^(?P<kind>story|clip|question): (?P<item>\d+)_(?P<cond>\d+)$")


def story_task_events(log_path, stimulus_kind, conditions, response_item=False):
    """Events of a task shaped fixation -> stimulus -> response screen -> fixation ...

    ``stimulus_kind`` is the word in the stimulus screen's log line ("story",
    "clip"); ``conditions`` maps the condition code at the end of that line
    (e.g. "story: 7_1") to a name. The response screen ("question") takes the
    condition of the stimulus before it; its stimulus_id is the item number if
    ``response_item`` (the line carries it), else "resp_screen".
    """
    log = after_trigger(read_log(log_path), "first fixation")
    keys = keypresses(log)
    rows, last = [], None
    for s in screens(log).itertuples(index=False):
        if s.label in ("first fixation", "final fixation"):
            rows.append(dict(onset=s.onset, duration=s.duration, trial_type="fixation",
                             stimulus_id="cross"))
            continue
        m = STIM_LABEL.match(s.label)
        if s.label.startswith(f"{stimulus_kind}: "):
            if not m:
                raise ValueError(f"unexpected stimulus line 'DISPLAY {s.label}' (expected '{stimulus_kind}: <item>_<cond>')")
            if m["cond"] not in conditions:
                raise ValueError(f"unknown condition code {m['cond']!r} in 'DISPLAY {s.label}'")
            last = dict(condition=conditions[m["cond"]], item=m["item"])
            rows.append(dict(onset=s.onset, duration=s.duration, trial_type="stimulus",
                             condition=last["condition"], stimulus_id=last["item"]))
        elif s.label == "question" or s.label.startswith("question: "):
            if m:   # "question: <item>_<cond>"
                cond, item = conditions[m["cond"]], m["item"]
            elif last is not None:
                cond, item = last["condition"], last["item"]
            else:
                raise ValueError(f"response screen at {s.onset} s before any stimulus")
            key, rt = first_response(keys, s.onset, s.duration)
            rows.append(dict(onset=s.onset, duration=s.duration, trial_type="response",
                             condition=cond, response=key, response_time=rt,
                             stimulus_id=item if response_item else "resp_screen"))
    if not rows:
        raise ValueError(f"{log_path}: no events found")
    df = pd.DataFrame(rows, columns=COLUMNS)
    if df["duration"].isna().any():
        raise ValueError(f"{log_path}: the last event has no end: was the run aborted?")
    return df


# ---------------------------------------------------------------------------
# Runs without responses (rest, movie watching)
# ---------------------------------------------------------------------------

def passive_task_events(log_path, first_screen, screen_rows):
    """Events of a run without responses: one row per screen whose label is in
    ``screen_rows`` (label -> dict of column values, e.g. trial_type,
    condition, stimulus_id); other screens (e.g. the end screen) are not
    events. Durations follow the shared rule (until the next screen change);
    response, response_time and accuracy are n/a.
    """
    log = after_trigger(read_log(log_path), first_screen)
    rows = [dict(onset=s.onset, duration=s.duration, **screen_rows[s.label])
            for s in screens(log).itertuples(index=False) if s.label in screen_rows]
    df = pd.DataFrame(rows, columns=COLUMNS)
    if df["duration"].isna().any():
        raise ValueError(f"{log_path}: the last event has no end: was the run aborted?")
    return df


def check_counts(df, expected, source=""):
    """Warn when the number of rows of a trial_type differs from the expected count."""
    for trial_type, n in expected.items():
        found = int((df["trial_type"] == trial_type).sum())
        if found != n:
            warnings.warn(f"{source}: {found} '{trial_type}' event(s), expected {n}", stacklevel=2)


# ---------------------------------------------------------------------------
# Checks and output
# ---------------------------------------------------------------------------

def check_durations(df, expected, by="trial_type", source=""):
    """Warn about screens whose duration differs from the nominal one by > DURATION_TOLERANCE."""
    for value, nominal in expected.items():
        sel = df[df[by] == value]
        off = sel[(sel["duration"] - nominal).abs() > DURATION_TOLERANCE]
        if len(off):
            warnings.warn(
                f"{source}: {len(off)} of {len(sel)} '{value}' screens deviate from the nominal "
                f"{nominal} s (durations {off['duration'].round(2).tolist()}); demo or interrupted run?",
                stacklevel=2)


def write_events(df, path, extra_columns=()):
    """Write a BIDS events.tsv: COLUMNS first, numbers with 4 decimals, missing values n/a."""
    out = df.reindex(columns=COLUMNS + [c for c in extra_columns if c not in COLUMNS]).copy()
    for col in INTEGER_COLUMNS:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce").round().astype("Int64")
    out = out.sort_values("onset", kind="stable")
    out.to_csv(path, sep="\t", index=False, na_rep=NA, float_format="%.4f")
    return Path(path)


def parse_args(script, names, example):
    """Positional command-line arguments -> dict; usage message if the count is wrong."""
    if len(sys.argv) != len(names) + 1:
        sys.exit(f"usage: python {script} " + " ".join(f"<{n}>" for n in names)
                 + f"\n  e.g. python {script} {example}")
    return dict(zip(names, sys.argv[1:]))


def events_file(outpath, sub, ses, task, acq, run=None):
    """BIDS events file name; the run entity only when given."""
    run_part = f"_run-{run}" if run is not None else ""
    return Path(outpath) / f"sub-{sub}_ses-{ses}_task-{task}_acq-{acq}{run_part}_events.tsv"


def cli(task, usage_infile="/path/to/log.log"):
    """Positional arguments of the task scripts: infile outpath subject session run acq."""
    a = parse_args(f"{task}_log2tsv.py", ["infile", "outpath", "sub", "ses", "run", "acq"],
                   f"{usage_infile} /output/tsv/here 023 02 1 1p9mm")
    return a["infile"], events_file(a["outpath"], a["sub"], a["ses"], task, a["acq"], a["run"])
