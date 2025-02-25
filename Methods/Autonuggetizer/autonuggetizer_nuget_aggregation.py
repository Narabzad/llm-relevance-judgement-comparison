import os
import json
import re
import openai
import ast
import traceback
import argparse
import numpy as np
from ollama import chat
from ollama import ChatResponse

def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

def process_nuggets(nugget_importance_file, nugget_assignment_file, dataset,model_name):
    qrels = {}
    new_qrels = {}
    new_qrels_vitals = {}
    levels = {}
    
    with open(f'data/qrels.dl{dataset}-passage.txt', 'r') as file:
        for line in file.readlines():
            qid, _, docid, rel = line.strip().split()
            if qid not in qrels:
                qrels[qid] = []
            qrels[qid].append(docid)
    
    nugget_imp = {}
    with open(nugget_importance_file, 'r') as file:
        for line in file.readlines():
            qid, query, imp = line.strip().split('\t')
            if qid not in nugget_imp:
                nugget_imp[qid] = imp
    
    with open(nugget_assignment_file, 'r') as file:
        for line in file.readlines():
            qid, docid, query, support = line.strip().split('\t')
            org_id = qid.split('_')[0]
            if (org_id, docid) not in new_qrels:
                new_qrels[org_id, docid] = []
            if qid in nugget_imp:
                if 'vital' in nugget_imp[qid]:
                    if (org_id, docid) not in new_qrels_vitals:
                        new_qrels_vitals[org_id, docid] = []
                    new_qrels_vitals[org_id, docid].append(support)
            new_qrels[org_id, docid].append(support)
    
    score = {'all': {}, 'all_strict': {}, 'vital': {}, 'vital_strict': {}, 'weighted': {}, 'weighted_strict': {}}
    output_files = {
        'all': open(f'raw qrels/{model_name}/nuggets//all/autonuggetizer.all.dl{dataset}.txt', 'w'),
        'all_strict': open(f'raw qrels/{model_name}/nuggets/all_strict/qrels.autonuggetizer.all_strict.dl{dataset}.txt', 'w'),
        'vital': open(f'raw qrels/{model_name}/nuggets/vital/autonuggetizer.vital.dl{dataset}.txt', 'w'),
        'vital_strict': open(f'raw qrels/{model_name}/nuggets/vital_strict/qrels.autonuggetizer.vital_strict.dl{dataset}.txt', 'w'),
        'weighted': open(f'raw qrels/{model_name}/nuggets/weighted/autonuggetizer.w.dl{dataset}.txt', 'w'),
        'weighted_strict': open(f'raw qrels/{model_name}/nuggets/weighted_strict/autonuggetizer.w_strict.dl{dataset}.txt', 'w')
    }
    
    for key in new_qrels:
        org_id, docid = key
        score['all'][key] = []
        score['all_strict'][key] = []
        score['weighted'][key] = []
        score['weighted_strict'][key] = []
        
        if key in new_qrels_vitals:
            score['vital'][key] = []
            score['vital_strict'][key] = []
            for val in new_qrels_vitals[key]:
                if 'partial' in val:
                    score['vital'][key].append(0.5)
                    score['vital_strict'][key].append(0)
                elif 'not' in val:
                    score['vital'][key].append(0)
                    score['vital_strict'][key].append(0)
                else:
                    score['vital'][key].append(1)
                    score['vital_strict'][key].append(1)
        
        for val in new_qrels[key]:
            if 'partial' in val:
                score['all'][key].append(0.5)
                score['all_strict'][key].append(0)
            elif 'not' in val:
                score['all'][key].append(0)
                score['all_strict'][key].append(0)
            else:
                score['all'][key].append(1)
                score['all_strict'][key].append(1)
        
        if key not in score['vital']:
            score['vital'][key] = [0]
        if key not in score['vital_strict']:
            score['vital_strict'][key] = [0]
        
        score['weighted'][key] = (sum(score['vital'][key]) + 0.5 * (sum(score['all'][key]) - sum(score['vital'][key]))) / (len(score['vital'][key]) + 0.5 * len(score['all'][key]) - len(score['vital'][key]))
        score['weighted_strict'][key] = (sum(score['vital_strict'][key]) + 0.5 * (sum(score['all_strict'][key]) - sum(score['vital_strict'][key]))) / (len(score['vital_strict'][key]) + 0.5 * len(score['all_strict'][key]) - len(score['vital_strict'][key]))
        
        output_files['all'].write(f'{org_id} 0 {docid} {np.mean(score["all"][key])}\n')
        output_files['all_strict'].write(f'{org_id} 0 {docid} {np.mean(score["all_strict"][key])}\n')
        output_files['weighted'].write(f'{org_id} 0 {docid} {score["weighted"][key]}\n')
        output_files['weighted_strict'].write(f'{org_id} 0 {docid} {score["weighted_strict"][key]}\n')
        try:
            output_files['vital'].write(f'{org_id} 0 {docid} {np.mean(score["vital"][key])}\n')
            output_files['vital_strict'].write(f'{org_id} 0 {docid} {np.mean(score["vital_strict"][key])}\n')
        except:
            print(org_id, docid)
    
    for file in output_files.values():
        file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process nuggets for qrels.")
    parser.add_argument('--nugget_importance_file', type=str, required=True, help='Path to the nugget importance file')
    parser.add_argument('--nugget_assignment_file', type=str, required=True, help='Path to the nugget assignment file')
    parser.add_argument('--dataset', type=str, required=True, help='Dataset identifier (e.g., 19, 20, 21, antique)')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')

    args = parser.parse_args()
    process_nuggets(args.nugget_importance_file, args.nugget_assignment_file, args.dataset,args.model_name)
