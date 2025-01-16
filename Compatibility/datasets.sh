#!/bin/sh -v

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <category>"
    exit 1
fi

category=$1

echo "Category: $category"
./all.sh dl19 "$category"
./all.sh dl20 "$category"
./all.sh dl21 "$category"
