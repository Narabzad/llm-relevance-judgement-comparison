import os
import json
import openai
import argparse
from ollama import chat
from ollama import ChatResponse
import ast
def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

def generate_rubrics(ds, model_name):
    query_col={}
    for line in open(f'data/topics.filtered.dl{ds}.txt','r').readlines():
        qid,query = line.split('\t')
        query_col[qid]=query
        
    doctext={}
    for line in open(f'data/qrels_text.dl{ds}','r').readlines():
        docid = line.split('\t')[0]
        text = line.replace(docid,'').replace('\t','')  
        doctext[docid]=text
        
    output=open(f'nuggets.{model_name}.dl{ds}.txt','w')

    for q in query_col:
        docs=[]
        for line in open(f'data/qrels.dl{ds}-passage.txt','r').readlines():
            qid,_,docid,rel = line.split()
            if q in qid and int(rel)>0:
                docs.append(docid)

        previous_list =[]
        query = query_col[q]

        for i in range(0,len(docs),10):
            docids = docs[i:i+10]    
            messages = [
                        {
                            "role": "system",
                            "content": (
                                "You are NuggetizeLLM, an intelligent assistant that can update a list of atomic nuggets \
                                    to best provide all the information required for the query."
                            )
                        },
                        {
                            "role": "user",
                            "content": ( f'Update the list of atomic nuggets of information (1-12 words), if needed, '
                            'so they best provide the information required for the query. '
                            'Leverage only the initial list of nuggets (if exists) and the provided context (this is an iterative process).'
                            'Return only the final list of all nuggets in a Pythonic list format (even if no updates). '
                            'Make sure there is no redundant information. '
                            'Ensure the updated nugget list has at most 30 nuggets (can be less), keeping only the most vital ones. '
                            'Order them in decreasing order of importance. '
                            'Prefer nuggets that provide more interesting information. \n '
                            f'Search Query: {query} '
                            'Context: ' + ' '.join([f'[{i+1}] {doctext[docid]} ' for i, docid in enumerate(docids)]) +
                            f'Search Query: {query} \n '
                            f'Initial Nugget List: {previous_list} \n '
                            f'Initial Nugget List Length: {len(previous_list)} \n '
                            'Only update the list of atomic nuggets (if needed, else return as is). Do not explain. '
                            'Always answer in short nuggets (not questions). List in the form ["a", "b", ...] and a and b are strings with no mention of ". '
                            'Updated Nugget List:')
                        }
                        ]
            try:
                if model_name == 'gpt-4o':
                    response = openai.ChatCompletion.create(
                        model=model_name,
                        messages=messages,
                        temperature=0
                    )
                    previous_list = ast.literal_eval(response.choices[0].message.content)
                elif model_name == 'llama3.2':
                    response: ChatResponse = chat(
                        model='llama3.2',
                        messages=messages,
                        options={"temperature": 0}
                    )
                    previous_list = ast.literal_eval(response.message.content)
            except Exception as e:
                print(f"Error processing QID {qid}: {e}")
                continue
            
            print(ds,q,i,len(previous_list))
        output.write(f'{q}\t{previous_list}\n')
        print(ds,q, previous_list,len(previous_list))
    output.close()

def main(dataset, model_name, api_key):
    if 'gpt-4o' == model_name:
        initialize_openai(api_key)
    for ds in dataset:
        generate_rubrics(ds, model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate exam rubrics using OpenAI or Ollama models.")
    parser.add_argument('--dataset', nargs='+', default=['19', '20', '21', 'antique'], help='dataset to process')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')

    args = parser.parse_args()
    main(args.dataset, args.model_name, args.api_key)
