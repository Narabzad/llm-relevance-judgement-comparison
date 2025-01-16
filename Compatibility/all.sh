#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <dataset> <category>"
    exit 1
fi

dataset=$1
category=$2

case "$category" in
    "binary")
        qrels="../raw qrels/binary/binary_${dataset}.txt"
        ;;
    "exam binary")
        qrels="../raw qrels/exam binary/qrels.mean.exam_selfrate_binary_${dataset}.txt"
        ;;
    "exam graded max")
        qrels="../raw qrels/exam graded max/qrels.max.exam_selfrate_${dataset}.txt"
        ;;
    "exam graded mean")
        qrels="../raw qrels/exam graded mean/qrels.mean.exam_selfrate_${dataset}.txt"
        ;;
    "nuggets all")
        qrels="../raw qrels/nuggets/all/qrels.autonuggetizer.all.${dataset}.txt"
        ;;
    "nuggets all strict")
        qrels="../raw qrels/nuggets/all_strict/qrels.autonuggetizer.all_strict.${dataset}.txt"
        ;;
    "nuggets vital")
        qrels="../raw qrels/nuggets/vital/qrels.autonuggetizer.vital.${dataset}.txt"
        ;;
    "nuggets vital strict")
        qrels="../raw qrels/nuggets/vital_strict/qrels.autonuggetizer.vital_strict.${dataset}.txt"
        ;;
    "nuggets weighted")
        qrels="../raw qrels/nuggets/weighted/qrels.autonuggetizer.w.${dataset}.txt"
        ;;
    "nuggets weighted strict")
        qrels="../raw qrels/nuggets/weighted_strict/qrels.autonuggetizer.w_strict.${dataset}.txt"
        ;;
    "umbrela zeroshot")
        qrels="../raw qrels/umbrela/zeroshot/umbrela_zeroshot_${dataset}.clean.json"
        ;;
    *)
        echo "Error: Unknown category '$category'"
        exit 1
        ;;
esac

label=$(echo "$dataset" | tr '[:lower:]' '[:upper:]')

tag="${category// /_}"

./compatibility.sh ../runs/"$dataset" "$qrels" > Output/"$dataset"."$tag".compatibility

./plot.py "$label $category" "$qrels" ndcg_cut_10 compatibility ../runs/"$dataset".ndcg_cut10 Output/"$dataset"."$tag".compatibility
mv plot.png Plots/"$dataset"."$tag".compatibility.png
