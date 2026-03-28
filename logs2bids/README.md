# Reformating task logs to tsv

Each task has its associated script to convert the log to a BIDS-compatible tsv file.

Using the false beliefs task as an example:

```
# Set parameters
log=/path/to/log.log
subjID=001
sesID=01
runID=01
out=/bids/rawdata/sub-${subjID}/ses-${sesID}/func/

python beliefs_log2tsv.py \
    ${log} \
    ${out} \
    ${subjID} \
    ${sesID} \
    ${runID}
```

Note that the output path should lead to the participant's `/rawdata/func` diretory
