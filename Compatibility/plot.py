#!/usr/bin/env python3
  
import argparse
import csv
import math
import sys
import matplotlib.pyplot as plt
import matplotlib.pyplot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Metric scatterplot')
    parser.add_argument('title', type=str, help='plot title')
    parser.add_argument('xmetric', type=str, help='x-axis metric')
    parser.add_argument('ymetric', type=str, help='y-axis metric')
    parser.add_argument('file', nargs='+', type=str)
    args = parser.parse_args()

    xdict = {}
    ydict = {}

    for name in args.file:
        first = True
        ignore = ""
        xpos = ypos = 0
        with open(name) as f:
            for line in f:
                if line != ignore:
                    field = line.rstrip().split(',')
                    if first:
                        ignore = line
                        first = False
                        for i in range(2,len(field)):
                            if field[i] == args.xmetric:
                                xpos = i
                            if field[i] == args.ymetric:
                                ypos = i
                    elif field[1] == 'average':
                        if xpos > 0:
                            xdict[field[0]] = float(field[xpos])
                        if ypos > 0:
                            ydict[field[0]] = float(field[ypos])
    x = []
    y = []
    for docno in xdict:
        if docno in ydict:
            x.append(xdict[docno])
            y.append(ydict[docno])

    plt.scatter(x, y, color='black')
    left, right = plt.xlim()
    right = math.ceil(max(x) * 10) / 10
    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.02f'))
    plt.xlim((0.0, right))
    if args.xmetric == 'ndcg_cut_10':
        xmetric = 'NDCG@10'
    else:
        xmetric = args.xmetric
    plt.xlabel(xmetric)
    left, right = plt.ylim()
    right = math.ceil(max(y) * 10) / 10
    plt.ylim((0.0, right))
    if args.ymetric == 'compatibility':
        ymetric = 'Compatibility'
    else:
        ymetric = args.ymetric
    plt.ylabel(ymetric)

    plt.title(args.title)

    plt.savefig('plot.png')
