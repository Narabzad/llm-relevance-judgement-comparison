#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <runs> <qrels>"
    exit 1
fi

RUNS=$1
QRELS=$2

TREC_EVAL="$HOME/trec_eval/trec_eval -q -m all_trec $QRELS"
# Process each file in the source directory
for file in "$RUNS"/*; do
    if [ -f "$file" ]; then
        $TREC_EVAL $file
    fi
done
