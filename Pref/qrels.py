#!/usr/bin/env python3

import string
import sys

def main():
    for line in sys.stdin:
        line = line.rstrip()
        (topic, q0, docno, rel) = line.split()
        if rel == '0':
          print(topic, q0, docno, 0)
        else:
          print(topic, q0, docno, 1)

if __name__ == "__main__":
    main()
