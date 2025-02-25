import os
import json
import re
import  openai 
import ast
import traceback
import argparse
from ollama import chat
from ollama import ChatResponse

def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

def generate_rubrics(year, model_name):
    nugget_col={}
    for line in open(f'outputs/{model_name}/nuggets/nuggets_importance_sorted.{model_name}_dl{year}.txt','r').readlines():
        qid,query,imp = line.split('\t')
        qid = qid.split('_')[0]
        if qid not in nugget_col:
            nugget_col[qid]=[]   
        nugget_col[qid].append(query)

    query_col={}
    for line in open(f'data/topics.filtered.dl{year}.txt','r').readlines():
        qid,query = line.split('\t')
        query_col[qid]=query
        
    doctext={}
    for line in open(f'data/qrels_text.dl{year}','r').readlines():
        docid = line.split('\t')[0]
        doctext[docid]=line.replace(f'{docid}\t','').strip()
        
    docs=[]
    error=False

    output=open(f'outputs/{model_name}/nuggets/nuggets_assignments_{model_name}.dl{year}-passage.txt','w')
    #check what has been written in the output file so far and store the qid docid in a "done" array
    qrel_col={}
    for line in open(f'data/qrels.dl{year}-passage.txt','r').readlines():
        qid,_,docid,rel = line.split()
        if qid not in qrel_col:
            qrel_col[qid]=[]
        qrel_col[qid].append(docid)

    for qid in qrel_col:
        print(year,qid)
        for docid in qrel_col[qid]:
            if qid not in nugget_col:
                print(qid,'not availavle')
                continue
            for i in range(0,len(nugget_col[qid]),10):
                nuggets = nugget_col[qid][i:min(i+10,len(nugget_col[qid]))]     
                messages = [
                            {
                                "role": "system",
                                "content": (
                                    "You are NuggetizeAssignerLLM, an intelligent assistant that can label a list of atomic nuggets based on if they are captured by a given passage."
                                )
                            },
                            {
                                "role": "user",
                            "content": ( f'Based on the query and passage, label each of the {len(nuggets )} nuggets either as'
                                        'support, partial_support, or not_support using the following criteria.'
                                        'A nugget that is fully captured in the passage should be labeled as support.'
                                        'A nugget that is partially captured in the passage should be labeled as partial_support.'
                                        'If the nugget is not captured at all, label it as not_support.'
                                        'Return the list of labels in a Pythonic list format (type: List[str]).'
                                        'The list should be in the same order as the input nuggets.'
                                        'Make sure to provide a label for each nugget. \n' 
                                        f'Search Query: {query_col[qid]}\n'
                                        f'Passage: {doctext[docid]}\n'
                                        f'Nugget List: {nuggets} \n'
                                        'Only return the list of labels (List[str]). Do not explain.\n'
                                        'Labels:')
                            }
                            ]
                try:
                    if model_name=='gpt-4o':
                        response = openai.chat.completions.create(
                            model="gpt-4o",
                            messages=messages,
                            temperature=0
                            )
                        response = ast.literal_eval(response.choices[0].message.content)

                    elif model_name=='llama3.2':
                        response: ChatResponse = chat(
                        model='llama3.2',
                        messages=messages,
                        options={"temperature": 0}
                    )
                        try:
                            response = ast.literal_eval(response.message.content)
                        except:
                            firstpart=response.message.content.split('[')[0]
                            lastpart=response.message.content.split(']')[-1]
                            msg=response.message.content.replace(firstpart,'').replace(lastpart,'')
                            try:
                                response = ast.literal_eval(msg)       
                            except:
                                continue       

                    if len(nuggets) != len(response):
                        print(f'Error: {qid} {docid} {len(nuggets)} {len(response)}')
                        error=True
                        break
                    
                    for j in range(len(response)):
                        q_counter = i + j 
                        output.write(f'{qid}_{q_counter}\t{docid}\t{nuggets[j]}\t{response[j]}\n')
                        print(f'nugget_assignment {year} {qid}_{q_counter} {docid} {response[j]}\n')
                except:
                    pass
                    #print what caused the error
                    print(f'Error: {qid} {docid}')
                    traceback.print_exc()
            if error:
                break
    output.close()
def main(years, model_name, api_key):
    if 'gpt-4o' == model_name:
        initialize_openai(api_key)
    for year in years:
        generate_rubrics(year, model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate exam rubrics using OpenAI or Ollama models.")
    parser.add_argument('--years', nargs='+', default=['19', '20', '21', 'antique'], help='Years to process')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')

    args = parser.parse_args()
    main(args.years, args.model_name, args.api_key)
