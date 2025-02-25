import os
import json
from umbrela.gpt_judge import GPTJudge
from umbrela.gpt_judge_llama import GPTJudgeLLama
import argparse
def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

def get_judgements(dataset, model_name):
    # Define year for file paths
    for year in dataset:
        # Initialize GPTJudge
        if model_name=='gpt-4o':
            gpt_judge = GPTJudge(
                qrel=f'data/qrels_text.dl{year}',
                prompt_type='bing',
                engine='gpt-4o',
            )
        elif model_name=='llama3.2':
            gpt_judge = GPTJudgeLLama(
                qrel=f'data/qrels_text.dl{year}',
                prompt_type='bing',
                engine='llama3.2',
            )
            

        # Load queries into a dictionary
        query_dic = {}
        with open(f'data/topics.filtered.dl{year}.txt', 'r') as file:
            for line in file:
                qid, query = line.strip().split('\t')
                query_dic[qid] = query

        # Load documents into a dictionary
        doc_dic = {}
        with open(f'data/qrels_text.dl{year}', 'r') as file:
            for line in file:
                docid = line.split('\t')[0]  # Extract the document ID
                doctext = line.replace(docid, '').strip()  # Remove the first occurrence of docid
                doc_dic[docid] = doctext

        # Process and save judgments
        output_file_clean = f'raw qrels/{model_name}/umbrela/umbrella_dl{year}.clean.json'

        counter = 0
        try:
            with open(output_file_clean, 'a') as output:
                for line in open(f'data/qrels.dl{year}-passage.txt', 'r'):
                    print(f"{year} : Processing line {counter}")
                    counter += 1
                    try:
                        qid, _, pid, _ = line.strip().split()
                        input_dict = {
                            "query": {"text": query_dic[qid], "qid": qid},
                            "candidates": [
                                {
                                    "doc": {"segment": doc_dic[pid]},
                                    "docid": pid,
                                },
                            ]
                        }

                        # Generate judgments using GPTJudge
                        results = gpt_judge.judge(input_dict, max_new_tokens=100, prepocess=True)


                        # Write the clean format result
                        output.write(f"{qid} 0 {pid} {results[0]['judgment']}\n")

                    except KeyError as e:
                        print(f"KeyError for qid={qid}, pid={pid}: {e}")
                    except Exception as e:
                        print(f"Error processing qid={qid}, pid={pid}: {e}")

        except IOError as e:
            print(f"File handling error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main(dataset, model_name, api_key):
    if 'gpt-4o' == model_name:
        initialize_openai(api_key)
    get_judgements(dataset, model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate exam rubrics using OpenAI or Ollama models.")
    parser.add_argument('--dataset', nargs='+', default=['antique','19', '20', '21'], help='dataset to process')
    parser.add_argument('--model_name', type=str, default='llama3.2', help='Model name to use')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')

    args = parser.parse_args()
    main(args.dataset, args.model_name, args.api_key)
