#!/usr/bin/env python3

import argparse
import json
import math
import os
import string
import sys

def load_qrels(filename):
    qrels = {}
    with open(filename) as f:
        for line in f:
            line = line.rstrip()
            (topic, q0, docno, qrel) = line.split()
            if topic not in qrels:
                qrels[topic] = {}
            qrels[topic][docno] = float(qrel)
    return qrels

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute agreement statistics')
    parser.add_argument('qrels', type=str, help='Qrels')
    parser.add_argument('log', type=str, help='Judgment log')
    parser.add_argument('--antique', action='store_true', help='Adjust for ANTIQUE qrels')
    args = parser.parse_args()

    if args.antique:
        unacceptable = 1
    else:
        unacceptable = 0

    qrels = load_qrels(args.qrels)
    qmax = {}
    for topic in qrels:
        if topic not in qmax:
            qmax[topic] = unacceptable 
        for docid in qrels[topic]:
            if qmax[topic] < qrels[topic][docid]:
                qmax[topic] = qrels[topic][docid]

    agreement = {
      "BvA": {"agree": 0, "tie": 0, "disagree": 0},
      "BvU": {"agree": 0, "tie": 0, "disagree": 0},
      "AvU": {"agree": 0, "tie": 0, "disagree": 0},
    }

    with open(args.log) as f:
        for line in f:
            if len(line) > 2 and line[0] == '@' and line[1] == ' ':
                line = line.rstrip()
                (at, topic, a, b, pjudge) = line.split()
                if qrels[topic][a] == qmax[topic]:
                    if qrels[topic][b] ==  unacceptable:
                        # Best(a) vs. Unacceptable(b)
                        if pjudge == '=':
                            agreement["BvU"]["tie"] += 1
                        else:
                            agreement["BvU"]["agree"] += 1
                    elif qrels[topic][b] < qmax[topic]:
                        # Best(a) vs. Acceptable(b)
                        if pjudge == '=':
                            agreement["BvA"]["tie"] += 1
                        else:
                            agreement["BvA"]["agree"] += 1
                elif qrels[topic][a] == unacceptable:
                    if qrels[topic][b] == qmax[topic]:
                        # Best(b) vs. Unacceptable(a)
                        if pjudge == '=':
                            agreement["BvU"]["tie"] += 1
                        else:
                            agreement["BvU"]["disagree"] += 1
                    elif qrels[topic][b] != unacceptable:
                        # Acceptable(b) vs. Unacceptable(a)
                        if pjudge == '=':
                            agreement["AvU"]["tie"] += 1
                        else:
                            agreement["AvU"]["disagree"] += 1
                else: 
                    if qrels[topic][b] == qmax[topic]:
                        # Best(b) vs. Acceptable(a)
                        if pjudge == '=':
                            agreement["BvA"]["tie"] += 1
                        else:
                            agreement["BvA"]["disagree"] += 1
                    elif qrels[topic][b] == unacceptable:
                        # Acceptable(a) vs. Unacceptable(b)
                        if pjudge == '=':
                            agreement["AvU"]["tie"] += 1
                        else:
                            agreement["AvU"]["agree"] += 1

    for kind in agreement:
        total = sum(agreement[kind].values())
        if total > 0:
            if kind == 'BvA':
                print ('Best vs. Acceptable:')
            elif kind == 'BvU':
                print ('Best vs. Unacceptable:')
            else:
                print ('Acceptable vs. Unacceptable:')
            for type in agreement[kind]:
                percent = 100*agreement[kind][type]/total
                print ('    ', type, agreement[kind][type], f"{percent:.1f}%")
