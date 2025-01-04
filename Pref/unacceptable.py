#!/usr/bin/env python3

import argparse
import random
import string
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare acceptable vs. unacceptable')
    parser.add_argument('qrels', type=str, help='Qrels')
    args = parser.parse_args()

    bad = {}
    good = {}
    with open(args.qrels) as f:
        for line in f:
            line = line.rstrip()
            (topic, q0, docno, qrel) = line.split()
            if qrel == '0':
                if topic not in bad:
                    bad[topic] = []
                bad[topic].append(docno)
            else:
                if topic not in good:
                    good[topic] = []
                good[topic].append(docno)
    for topic in bad:
        random.shuffle(bad[topic])
    for topic in good:
        random.shuffle(good[topic])

    for topic in bad:
        if topic in good:
            m = max(len(bad[topic]), len((good[topic])))
            for n in range(m):
                i = n % len(bad[topic])
                j = n % len(good[topic])
                print(topic, bad[topic][i], good[topic][j])
