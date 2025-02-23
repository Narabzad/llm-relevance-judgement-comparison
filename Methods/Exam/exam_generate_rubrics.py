import os
import json
import openai
import argparse
from ollama import chat
from ollama import ChatResponse

def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

def generate_rubrics(year, model_name):
    query_dic = {}
    output_file = f'data/exam_rubrics_{model_name}_dl{year}.json'
    if not os.path.exists(output_file):
        with open(f'data/topics.filtered.dl{year}.txt', 'r') as input_file, open(output_file, 'a') as output:
            for line in input_file:
                qid, query_text = line.strip().split('\t')
                query_dic[qid] = query_text
                print(f"Processing QID: {qid}")

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are an intelligent assistant that can generate a comprehensive list of subtopics "
                            "that thoroughly cover the information need behind the query."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Break the query <query_title> into concise questions that must be answered. "
                            f"Generate 10 concise, insightful questions that reveal whether information relevant for <query_title> was provided, showcasing a deep understanding of the subject matter. "
                            f"Avoid basic or introductory-level inquiries. Keep the questions short and in a Python list format.\n\n"
                            f"query_title: {query_text}"
                        )
                    }
                ]

                try:
                    if model_name == 'gpt-4o':
                        response = openai.ChatCompletion.create(
                            model=model_name,
                            messages=messages,
                            temperature=0
                        )
                    elif model_name == 'llama3.2':
                        response: ChatResponse = chat(
                            model='llama3.2',
                            messages=messages,
                            options={"temperature": 0}
                        )
                except Exception as e:
                    print(f"Error processing QID {qid}: {e}")
                    continue

                current_query = {
                    "qid": qid,
                    "original_query": query_text,
                    "examtopics": response.choices[0].message.content if model_name == 'gpt-4o' else response.message.content
                }
                
                output.write(json.dumps(current_query) + "\n")
                print("exam rubric generation",year,model_name,current_query)

def main(dataset, model_name, api_key):
    if 'gpt-4o' == model_name:
        initialize_openai(api_key)
    for ds in dataset:
        generate_rubrics(year, model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate exam rubrics using OpenAI or Ollama models.")
    parser.add_argument('--dataset', nargs='+', default=['19', '20', '21', 'antique'], help='dataset to process')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')

    args = parser.parse_args()
    main(args.dataset, args.model_name, args.api_key)
