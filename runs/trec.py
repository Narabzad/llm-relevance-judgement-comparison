#!/usr/bin/env python3
  
import argparse
import re
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reorganize trec_eval output')
    parser.add_argument('eval', type=str, help='trec_eval output')
    parser.add_argument('--measure', type=str, default=None, help='Optional measure to process')
    args = parser.parse_args()

    measure = 'ndcg_cut_10'
    if args.measure:
        measure = args.measure
    print('runid,topic,', measure, sep='')

    runid = ""
    maps = {}
    with open(args.eval) as evalf:
        for line in evalf:
            line = line.rstrip()
            (key, topic, value) = re.split(r'\s+', line)
            if key == 'runid':
                runid = value
            elif key == measure:
                if topic == 'all':
                    for topic in maps:
                        print(runid, topic, maps[topic], sep=',')
                    print(runid, 'average', value, sep=',')
                    maps = {}
                else:
                    maps[topic] = value
