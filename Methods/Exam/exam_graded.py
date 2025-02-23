import os
import json
import re
import openai
import ast
import argparse
from ollama import chat
from ollama import ChatResponse 

def load_text_collection(year):
    text_col = {}
    with open(f'data/qrels_text.dl{year}', 'r') as file:
        for line in file.readlines():
            docid=line.split('\t')[0]
            text_col[docid] = line.replace(docid+'\t', '').strip()
    return text_col

def load_qrels(year):
    qrels_col = {}
    with open(f'data/qrels.dl{year}-passage.txt', 'r') as file:
        for line in file.readlines():
            qid, _, docid, _ = line.strip().split()
            qrels_col.setdefault(qid, []).append(docid)
    return qrels_col

    

def main(years, model_name, api_key):
    for year in years:
        openai.api_key = api_key
        text_col = load_text_collection(year)
        qrels_col = load_qrels(year)


                
        done=[]
        output_path = f'outputs/{model_name}/exam_graded/exam_graded_{model_name}_dl{year}.txt'

        try:
            for line in  open(output_path, 'r').readlines():
                subtopic_id,_,docid,_=line.split()
                done.append((subtopic_id, docid))
        except:
            pass
        
        with open(output_path, 'w') as output:
            for line in open(f'data/exam_rubrics_{model_name}_dl{year}.tsv','r').readlines():
                subtopic_id,nugget= line.split('\t')
                print(nugget)
                qid= subtopic_id.split('_')[0]
                for docid in qrels_col[qid]:
                    if (subtopic_id,docid) in done:
                        continue
                    messages = [
                        {
                            "role": "system",
                            "content": (
                                "You are an intelligent assistant."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Can the question be answered based on the available context? choose one option and do not add additional explanation: \
                                - 5: The answer is highly relevant, complete, and accurate.\
                                - 4: The answer is mostly relevant and complete but may have minor gaps or inaccuracies. \
                                - 3: The answer is partially relevant and complete, with noticeable gaps or inaccuracies. \
                                - 2: The answer has limited relevance and completeness, with significant gaps or inaccuracies. \
                                - 1: The answer is minimally relevant or complete, with substantial shortcomings. \
                                - 0: The answer is not relevant or complete at all. \
                                Question: {nugget}\
                                Context: {text_col[docid]}"
                            )

                        }
                        ]

                    try:
                        if model_name =='gpt-4o':
                            response = openai.chat.completions.create(
                                model=model_name,
                                messages=messages,
                                temperature=0)
                        elif model_name =='llama3.2':
                            response: ChatResponse = chat(model='llama3.2', 
                            messages = messages,options={ "temperature": 0})

                    except:
                        continue
                    if model_name =='gpt-4o':
                        rate = response.choices[0].message.content
                    elif model_name =='llama3.2':
                        rate = response.message.content
                    output.write(f"{subtopic_id} 0 {docid} {rate}\n")
                    print(f"Year {year} | QID {subtopic_id} | DocID {docid} | Rating {rate}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate document relevance using OpenAI models.")
    parser.add_argument('--years', nargs='+', default=[ '20','21','antique','19'], help='Years to process (e.g., 19 20)')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model to use for evaluation')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')
    args = parser.parse_args()

    main(args.years, args.model_name, args.api_key)

        
