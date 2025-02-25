import os
import json
import re
import openai
import ast
import argparse
from ollama import chat
from ollama import ChatResponse 

def main(dataset, model_name, api_key=None):
    if model_name == 'gpt-4o' and openai_api_key is None:
        raise ValueError("OPENAI_API_KEY must be provided for model 'gpt-4o'")
    if model_name not in  ['gpt-4o','llama3.2']:
        raise ValueError("Model not available")
    if model_name == 'gpt-4o':
        os.environ['OPENAI_API_KEY'] = openai_api_key

    for year in dataset:
        queries = {}
        for line in open(f'data/topics.filtered.dl{year}.txt', 'r').readlines():
            qid, query = line.split('\t')
            queries[qid] = query

        text_col = {}
        for line in open(f'data/qrels_text.dl{year}', 'r').readlines():
            docid = line.split('\t')[0]
            doctext = line.replace(docid, '').replace('\t', '')
            text_col[docid] = doctext
        

        output = open(f'binary_{model_name}_dl{year}.txt', 'a')

        for line in open(f'data/qrels.dl{year}-passage.txt', 'r').readlines():
            qid, _, docid, _ = line.split()

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
                        Question: {queries[qid]}\n \
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
            print('binary',model_name,year, qid, docid, rate)
            output.write(f"{qid} 0 {docid} {rate}\n")
    output.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--dataset', type=list, default=['20','21','antique','19'], help='name the collections')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')
    parser.add_argument('--api_key', type=str, default=key,help='OpenAI API key for model gpt-4o')

    args = parser.parse_args()

    main(dataset=args.dataset, model_name=args.model_name, api_key=args.api_key)