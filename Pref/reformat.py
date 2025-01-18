#!/usr/bin/env python3
#reformat judge.* into qrels

import sys
from collections import Counter

data = sys.stdin.read().strip().split("\n")

counts = Counter()
for line in data:
    fields = line.split()
    if len(fields) >= 2:
        pair = (fields[0], fields[1])
        counts[pair] += 1

for (field1, field2), count in sorted(counts.items(), key=lambda x: (x[0][0], -x[1])):
    print(field1, 'Q0', field2, count)
