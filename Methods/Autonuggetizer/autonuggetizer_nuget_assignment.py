import os
import json
import re
import openai
import ast
import traceback
import argparse
from ollama import chat
from ollama import ChatResponse

def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

def generate_rubrics(dataset, model_name, sorted_nugget_file):
    nugget_col = {}
    with open(sorted_nugget_file, 'r') as file:
        for line in file.readlines():
            qid, query, imp = line.strip().split('\t')
            qid = qid.split('_')[0]
            if qid not in nugget_col:
                nugget_col[qid] = []
            nugget_col[qid].append(query)

    query_col = {}
    with open(f'data/topics.filtered.dl{dataset}.txt', 'r') as file:
        for line in file.readlines():
            qid, query = line.strip().split('\t')
            query_col[qid] = query

    doctext = {}
    with open(f'data/qrels_text.dl{dataset}', 'r') as file:
        for line in file.readlines():
            docid = line.split('\t')[0]
            doctext[docid] = line.replace(f'{docid}\t', '').strip()

    output_path = f'nuggets_assignments_{model_name}.{dataset}.txt'
    with open(output_path, 'w') as output:
        qrel_col = {}
        with open(f'data/qrels.dl{dataset}-passage.txt', 'r') as file:
            for line in file.readlines():
                qid, _, docid, rel = line.split()
                if qid not in qrel_col:
                    qrel_col[qid] = []
                qrel_col[qid].append(docid)

        for qid in qrel_col:
            print(dataset, qid)
            for docid in qrel_col[qid]:
                if qid not in nugget_col:
                    print(qid, 'not available')
                    continue
                for i in range(0, len(nugget_col[qid]), 10):
                    nuggets = nugget_col[qid][i:min(i + 10, len(nugget_col[qid]))]
                    messages = [
                        {
                            "role": "system",
                            "content": ("You are NuggetizeAssignerLLM, an intelligent assistant that can label a list of atomic nuggets based on if they are captured by a given passage.")
                        },
                        {
                            "role": "user",
                            "content": (f'Based on the query and passage, label each of the {len(nuggets)} nuggets either as '
                                        'support, partial_support, or not_support using the following criteria. '
                                        'A nugget that is fully captured in the passage should be labeled as support. '
                                        'A nugget that is partially captured in the passage should be labeled as partial_support. '
                                        'If the nugget is not captured at all, label it as not_support. '
                                        'Return the list of labels in a Pythonic list format (type: List[str]). '
                                        'The list should be in the same order as the input nuggets. '
                                        'Ensure a label for each nugget. \n' 
                                        f'Search Query: {query_col[qid]}\n'
                                        f'Passage: {doctext[docid]}\n'
                                        f'Nugget List: {nuggets} \n'
                                        'Only return the list of labels (List[str]). Do not explain.\n'
                                        'Labels:')
                        }
                    ]
                    try:
                        if model_name == 'gpt-4o':
                            response = openai.chat.completions.create(
                                model="gpt-4o",
                                messages=messages,
                                temperature=0
                            )
                            response = ast.literal_eval(response.choices[0].message.content)
                        elif model_name == 'llama3.2':
                            response: ChatResponse = chat(
                                model='llama3.2',
                                messages=messages,
                                options={"temperature": 0}
                            )
                            response = ast.literal_eval(response.message.content)

                        if len(nuggets) != len(response):
                            print(f'Error: {qid} {docid} {len(nuggets)} {len(response)}')
                            break

                        for j in range(len(response)):
                            q_counter = i + j
                            output.write(f'{qid}_{q_counter}\t{docid}\t{nuggets[j]}\t{response[j]}\n')
                            print(f'nugget_assignment {dataset} {qid}_{q_counter} {docid} {response[j]}\n')
                    except Exception as e:
                        print(f'Error: {qid} {docid}')
                        traceback.print_exc()

def main(datasets, model_name, api_key, sorted_nugget_file):
    if model_name == 'gpt-4o':
        initialize_openai(api_key)
    for dataset in datasets:
        generate_rubrics(dataset, model_name, sorted_nugget_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate exam rubrics using OpenAI or Ollama models.")
    parser.add_argument('--datasets', nargs='+', default=['19', '20', '21', 'antique'], help='Datasets to process')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')
    parser.add_argument('--sorted_nugget_file', type=str, required=True, help='Path to the sorted nuggets file')
    
    args = parser.parse_args()
    main(args.datasets, args.model_name, args.api_key, args.sorted_nugget_file)