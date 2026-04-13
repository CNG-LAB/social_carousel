################################################################
## log to tsv conversion for task: emomatch
## 
## example usage:
"""
python emomatch_log2tsv.py \
    /path/to/csv.csv \
    /output/tsv/here \
    pilot06 \
    02 \
    02
"""
################################################################

# packages
import pandas as pd
import sys

## Read inputs
infile = sys.argv[1] 
outpath = sys.argv[2]
subj = sys.argv[3]
ses = sys.argv[4]
run = sys.argv[5]

# subject id
bids_id = 'sub-{subject}_ses-{session}'.format(subject=subj, session=ses)

# functions
def transform_csv_to_tsv(input_csv_path, output_tsv_path, column_mapping, column_order):
    """
    Loads a CSV, renames and reorders columns, and saves as TSV.
    :param input_csv_path: Path to input CSV file
    :param output_tsv_path: Path to output TSV file
    :param column_mapping: Dict of old_name -> new_name
    :param column_order: List of column names in desired order (after renaming)
    """

    # Load CSV
    df = pd.read_csv(input_csv_path)
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    df["duration"] = 2

    # Reorder columns
    df = df[column_order]
    
    # Save as TSV
    df.to_csv(output_tsv_path, sep="\t", index=False)


if __name__ == "__main__":
    
    # out name
    outfile = '{out_here}/{id_here}_task-emomatch_run-{run_here}_events.tsv'.format(out_here=outpath, id_here=bids_id, run_here=run)

    # Define how columns should be renamed
    column_mapping = {
        "trialOnsetTime": "onset",
        "condition(0=checker,1=gender,2=emo)": "trial_type",
        "condTrialNumber": "trial_number",
        "keyPress": "response",
        "accuracy": "accuracy",
        "probeFileName": "probe_id",
        "foilFileName": "foil_id",
        "targetFileName": "target_id"
    }
    
    # Define desired column order (after renaming)
    column_order = [
        "onset",
        "duration",
        "trial_type",
        "trial_number",
        "response",
        "accuracy",
        "probe_id",
        "foil_id",
        "target_id"
    ]

transform_csv_to_tsv(
    infile,
    outfile,
    column_mapping,
    column_order
)
