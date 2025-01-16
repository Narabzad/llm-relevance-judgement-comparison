#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <runs> <qrels>"
    exit 1
fi

RUNS=$1
QRELS=$2

EVAL="./compatibility.py -p 0.90"
# Process each file in the source directory
for file in "$RUNS"/*; do
    if [ -f "$file" ]; then
        $EVAL "$QRELS" "$file"
    fi
done
