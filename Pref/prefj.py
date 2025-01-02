#!/usr/bin/env python3
  
import argparse
import pickle
import random
import sys

def load_qrels(filename):
  qrels = {}
  with open(filename) as qf:
      for line in qf:
          fields = line.rstrip().split()
          if len(fields) == 4:
              (topic, q0, docno, rel) = fields
          else:
              (topic, docno, rel) = fields
          if rel[0] == 'L':
              rel = rel[1:]
          rel = float(rel)
          if topic not in qrels:
              qrels[topic] = {}
          qrels[topic][docno] = rel;
  return qrels


def load_judgments(filename):
    judgments = {}
    with open(filename) as jf:
        for line in jf:
            fields = line.rstrip().split()
            if len(fields) == 3:
                (topic, a, b) = fields
                best = a
            else:
                (topic, a, b, best) = fields
            if a == b or (a != best and b != best):
                print('Bad judgment: ', line, file=sys.stderr)
            else:
                if topic not in judgments:
                    judgments[topic] = set()
                if a < b:
                    judgment = ' '.join((a, b, best))
                else:
                    judgment = ' '.join((b, a, best))
                judgments[topic].add(judgment)
    return judgments


def candidates(qrels, k):
    candidates = []
    for docno in qrels:
        if qrels[docno] > 0.0:
            candidates.append(docno)
    candidates.sort(key=lambda docno: qrels[docno], reverse=True)
    bottom = k
    while bottom < len(candidates) and qrels[
          candidates[bottom]] == qrels[candidates[k - 1]]:
        bottom += 1
    return candidates[:bottom]


def stage1(docnos, requested):
    work = set()
    n = min(requested, len(docnos) - 1)
    if n < 1:
        return work
    counts = {}
    for docno in docnos:
        counts[docno] = 0
    done = False
    while not done:
        random.shuffle(docnos)
        docnos.sort(key = lambda docno : counts[docno])
        found = False
        a = b = ""
        i = 0
        while not found and i < len(docnos) - 1:
            j = i + 1
            while not found and j < len(docnos):
                a = docnos[i]
                b = docnos[j]
                if a < b:
                    task = a + ' ' + b
                else:
                    task = b + ' ' + a
                found = task not in work
                j += 1
            i += 1
        work.add(task)
        counts[a] += 1
        counts[b] += 1
        done = True
        for docno in counts:
            if counts[docno] < n:
                done = False
    return work


def stage2(docnos):
    work = set()
    for a in docnos:
        for b in docnos:
            if a < b:
                task = a + ' ' + b
                work.add(task)
    return work


class prefj(object):
    K = 5
    F = 9
    P = 7
   
    def __init__(self, topic, qrels, k = None, f = None, p = None):
        self.topic = topic
        if k == None:
            self.k = prefj.K
        elif k <= 0:
            self.k = 1
        else:
            self.k = k
        if p == None:
            self.p = prefj.P
        elif p <= self.k:
            self.p = self.k + 1
        else:
            self.p = p
        if f == None:
            self.f = prefj.F
        elif f <= self.p:
            self.f = self.p + 1
        else:
            self.f = f
        self.qrels = qrels
        self.candidates = candidates(qrels, self.k)
        self.outstanding = set()
        self.log = []
        self.topk = {}
        if len(self.candidates) == 1:
            self.topk[self.candidates[0]] = 1.0
            self.pool = []
        else:
            self.pool = self.candidates

    def requests(self):
        if len(self.outstanding) > 0 or len(self.topk) > 0:
            return self.outstanding
        if len(self.pool) > self.f:
            self.outstanding = stage1(self.pool, self.p)
        else:
            self.outstanding = stage2(self.pool)
        return self.outstanding

    def add(self, judgments):
        winner = {}
        for judgment in judgments:
            (a, b, best) = judgment.split(' ')
            pair = a + ' ' + b
            if pair in self.outstanding:
                self.outstanding.remove(pair)
                winner[pair] = best
                self.log.append(judgment)
            else:
              print('judgment not requested:', self.topic, pair,
                    file=sys.stderr)
        if len(self.outstanding) > 0:
            return
        score = {}
        for docno in self.pool:
            score[docno] = 0.0
        for pair in winner:
            score[winner[pair]] += 1
        if len(self.pool) > self.f:
            threshold = int(self.p/2)
            self.pool = []
            for docno in score:
                if score[docno] > threshold:
                    self.pool.append(docno)
            self.requests()
            return
        else:
            self.pool.sort(key=lambda docno: score[docno], reverse=True)
            if self.k >= len(self.pool):
                bottom = len(self.pool)
            else:
                bottom = self.k
                while bottom < len(self.pool) and score[
                      self.pool[bottom]] == score[self.pool[self.k - 1]]:
                    bottom += 1
            for i in range(0,bottom):
                if score[self.pool[i]] > 0.0:
                    self.topk[self.pool[i]] = score[self.pool[i]]
            self.pool = []

    def prefs(self):
        prefs = {}
        if len(self.pool) > 0:
            return
        max = 0.0
        for docno in self.qrels:
            if self.qrels[docno] > max:
                max = self.qrels[docno]
        for docno in self.topk:
            prefs[docno] = self.topk[docno] + max + 100.0
        for docno in self.qrels:
            if docno not in self.topk:
                prefs[docno] = self.qrels[docno]
        return prefs

    def dump_prefs(self):
        if len(self.pool) > 0:
            return
        prefs = self.prefs()
        for docno in prefs:
            print (self.topic, 'Q0', docno, prefs[docno])

    def dump_qrels(self):
        for docno in self.qrels:
            print(self.topic, 'Q0', docno, self.qrels[docno])

    def dump_candidates(self):
        for docno in self.candidates:
            print(self.topic, 'Q0', docno, self.qrels[docno])

    def dump_pool(self):
        for docno in self.pool:
            print(self.topic, 'Q0', docno, self.qrels[docno])

    def dump_log(self):
        for triple in self.log:
            print(self.topic, triple)


class command(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
          description='Manage preference judging',
          usage='''prefj state <subcommand> [<args>]
Available subcommands are:
    initialize     Load an initial qrels file
    add            Add judgments
    requests       Request judgments
    prefs          Produce preferences in qrel format
    qrels          Dump original qrels
    candidates     Dump inital candidate pool as qrels
    pool           Dump current candidate pool as qrels
    log            Dump log of judgment pairs 
''')
        parser.add_argument('state', help='Judging state')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:3])
        if not hasattr(self, args.command):
            print('prefj: Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)(args.state)

    def initialize(self, state):
        parser = argparse.ArgumentParser(
          description='Initialize preference judgments')
        parser.add_argument('qrels', type=str,
          help='TREC-style qrels')
        parser.add_argument('--k', type=int, default=prefj.K,
          help='Depth of top documents required')
        parser.add_argument('--f', type=int, default=prefj.F,
          help='First stage pooling threshold')
        parser.add_argument('--p', type=int, default=prefj.P,
          help='First stage pairings')
        args = parser.parse_args(sys.argv[3:])
        if args.p <= args.k:
            print('p={p} must be greater than k={k}'.format(
                p=args.p, k=args.k), file=sys.stderr)
        if args.f <= args.p:
            print('f={f} must be greater than p={p}'.format(
                f=args.f, p=args.p), file=sys.stderr)
        qrels = load_qrels(args.qrels)
        prefjs = {}
        for topic in qrels:
            prefjs[topic] = prefj(
              topic, qrels[topic], k = args.k, f = args.f, p = args.p)
        pickle.dump(prefjs, open(state, "wb"))

    def add(self, state):
        parser = argparse.ArgumentParser(
          description='Initialize preference judgments')
        parser.add_argument('judgments', type=str,
          help='Perference judgments')
        args = parser.parse_args(sys.argv[3:])
        judgments = load_judgments(args.judgments)
        prefjs = pickle.load(open(state, "rb"))
        for topic in judgments:
            if topic not in prefjs:
                print('unknown topic: ', topic, file=sys.stderr)
            else:
                prefjs[topic].add(judgments[topic])
        pickle.dump(prefjs, open(state, "wb"))

    def requests(self, state):
        prefjs = pickle.load(open(state, "rb"))
        for topic in prefjs:
            outstanding = prefjs[topic].requests()
            for request in outstanding:
                (a, b) = request.split(' ')
                if random.randint(0,1) == 0:
                    print(topic, a, b)
                else:
                    print(topic, b, a)
        pickle.dump(prefjs, open(state, "wb"))

    def prefs(self, state):
        prefjs = pickle.load(open(state, "rb"))
        for topic in prefjs:
            prefjs[topic].dump_prefs()

    def qrels(self, state):
        prefjs = pickle.load(open(state, "rb"))
        for topic in prefjs:
            prefjs[topic].dump_qrels()

    def candidates(self, state):
        prefjs = pickle.load(open(state, "rb"))
        for topic in prefjs:
            prefjs[topic].dump_candidates()

    def pool(self, state):
        prefjs = pickle.load(open(state, "rb"))
        for topic in prefjs:
            prefjs[topic].dump_pool()

    def log(self, state):
        prefjs = pickle.load(open(state, "rb"))
        for topic in prefjs:
            prefjs[topic].dump_log()


if __name__ == "__main__":
    command()
