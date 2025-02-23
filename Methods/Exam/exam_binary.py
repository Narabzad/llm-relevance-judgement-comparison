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
        output_path = f'outputs/{model_name}/exam_binary/exam_binary_{model_name}_dl{year}.txt'

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
                                " You are an expert assessor making TREC relevance judgments. \
                                You will be given a TREC topic and a portion of a document. \
                                If any part of the document is relevant to the topic, answer “Yes”. \
                                If not, answer “No”. Remember that the TREC relevance condition states that a document is relevant to a topic \
                                if it contains information that is helpful in satisfying the user’s information need described by the topic. \
                                A document is judged relevant if it contains information that is on-topic and of potential value to the user. "
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f" Indicate if the passage is relevant for the question. \
                                Question: {nugget}\n \
                                Passage: {text_col[docid]} \n \
                                Relevant?"
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
                    if 'yes' in rate.lower():
                        rate = 1
                    else:
                        rate = 0
                    output.write(f"{subtopic_id} 0 {docid} {rate}\n")
                    print(f"Year {year} | QID {subtopic_id} | DocID {docid} | Rating {rate}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate document relevance using OpenAI models.")
    parser.add_argument('--years', nargs='+', default=[ '20','21','antique','19'], help='Years to process (e.g., 19 20)')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model to use for evaluation')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')
    args = parser.parse_args()

    main(args.years, args.model_name, args.api_key)

        
