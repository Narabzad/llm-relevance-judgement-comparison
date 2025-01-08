#!/usr/bin/env python3

import argparse
import json
import math
import os
import string
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute agreement statistics')
    parser.add_argument('human', type=str, help='Human judgments')
    parser.add_argument('log', type=str, help='Judgment log')
    args = parser.parse_args()

    human = {}
    with open(args.human) as f:
        for line in f:
            (topic, a, b, best) = line.rstrip().split()
            if topic not in human:
                human[topic] = {}
            if a > b:
                (a, b) = (b, a)
            pair = a + ':' + b
            if pair not in human[topic]:
                human[topic][pair] = 0
            if best == a:
                human[topic][pair] += 1
            elif best == b:
                human[topic][pair] -= 1


    llm = {}
    with open(args.log) as f:
        for line in f:
            if len(line) > 2 and line[0] == '@' and line[1] == ' ':
                line = line.rstrip()
                (at, topic, a, b, pjudge) = line.split()
                if topic not in llm:
                    llm[topic] = {}
                if pjudge == '!':
                    best = a
                    if a > b:
                        (a, b) = (b, a)
                    pair = a + ':' + b
                    if pair not in llm[topic]:
                        llm[topic][pair] = 0
                    if best == a:
                        llm[topic][pair] += 1
                    else:
                        llm[topic][pair] -= 1
                elif pjudge == '=':
                    if pair not in llm[topic]:
                        llm[topic][pair] = 0

    agree = tie = disagree = 0
    for topic in llm:
        for pair in llm[topic]:
            if pair in human[topic]:
                if llm[topic][pair] == 0:
                    tie += 1
                elif llm[topic][pair] > 0:
                    if human[topic][pair] > 0:
                        agree += 1
                    elif human[topic][pair] < 0:
                        disagree += 1
                else:
                    if human[topic][pair] < 0:
                        agree += 1
                    elif human[topic][pair] > 0:
                        disagree += 1

    total = agree + tie + disagree
    percent = 100.0*agree/total
    print('Agree', agree, f"{percent:.1f}%")
    percent = 100.0*tie/total
    print('Tie', tie, f"{percent:.1f}%")
    percent = 100.0*disagree/total
    print('Disagree', disagree, f"{percent:.1f}%")
