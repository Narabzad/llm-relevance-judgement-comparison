#!/usr/bin/env python3

import argparse
import string
import sys
import re
from openai import OpenAI

client = OpenAI()

smsg = """
You are a highly experienced and accurate assessor for TREC.
"""

def answer(question):
    completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "system", "content": smsg},
        {"role": "user", "content": question},
      ]
    )
    return completion.choices[0].message.content.replace("\n", " ")

def prompt(question, passage_a, passage_b):
    return """
Select the passage that answers the question better. Just answer 1 or 2, without any explanation or extra verbiage.  If both passages are similar, select the simplest and clearest.
Question:
{question}
Passage 1:
{passage_a}
Passage 2:
{passage_b}
""".format(question=question, passage_a=passage_a, passage_b=passage_b)

def judge(question, passage_a, passage_b):
    print(prompt(question, passage_a, passage_b))
    response = answer(prompt(question, passage_a, passage_b))
    print('Response:', response)
    if "Passage 1" in response:
        return 1
    if "Passage 2" in response:
        return -1 
    if "1" in response and "2" not in response:
        return 1
    if "1" not in response and "2" in response:
        return -1
    print("Bad GPT response:", response, file=sys.stderr)
    return 0

def pref(question, passage_a, passage_b):
    a = judge(question, passage_a, passage_b)
    b = judge(question, passage_b, passage_a)
    print(a, b, len(passage_a), len(passage_b))
    if a == 1 and b == -1:
      return 1
    if a == -1 and b == 1:
      return -1
    if a == 0:
      return -b
    if b == 0:
      return a
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GPT preference judgments')
    parser.add_argument('passages', type=str, help='passages by docno')
    parser.add_argument('questions', type=str, help='questions by topic')
    parser.add_argument('pairs', type=str, help='pairs to judge')
    args = parser.parse_args()

    questions = {}
    with open(args.questions) as f:
        for line in f:
            line = line.rstrip()
            (topic, question) = line.split('\t', 1)
            questions[topic] = question

    passages = {}
    with open(args.passages) as f:
        for line in f:
            line = line.rstrip()
            (docno, passage) = line.split('\t', 1)
            passages[docno] = passage

    with open(args.pairs) as f:
        for line in f:
            line = line.rstrip()
            (topic, a, b) = line.split(' ')
            print('---', topic, a, b)
            if a in passages.keys():
                if b in passages.keys():
                    better = pref(questions[topic], passages[a], passages[b])
                    if better == 1:
                        print('@', topic, a, b, '!')
                    elif better == -1:
                        print('@', topic, b, a, '!')
                    else:
                        if len(passages[a]) < len(passages[b]):
                            print('@', topic, a, b, '=')
                        else:
                            print('@', topic, b, a, '=')
                else:
                    print("No passage for:", b, file=sys.stderr)
                    print('@', topic, a, b, '?')
            elif b in passages.keys():
                print("No passage for:", a, file=sys.stderr)
                print('@', topic, b, a, '?')
            else:
                print("No passage for:", a, file=sys.stderr)
                print("No passage for:", b, file=sys.stderr)
                print('@', topic, a, b, '?')
            sys.stdout.flush()
