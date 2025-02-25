import ast
import argparse
from ollama import chat
from ollama import ChatResponse
import openai
import pandas as pd


def initialize_openai(api_key):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key



def main(model_name, nugget_file, dataset):
    if 'gpt-4o' == model_name:
        initialize_openai(api_key)
    query_col = {}
    with open(f'data/topics.filtered.dl{dataset}.txt', 'r') as file:
        for line in file.readlines():
            qid, query = line.strip().split('\t')
            query_col[qid] = query

    output_path = f'nuggets_importance.{nugget_file}.txt'
    with open(output_path, 'w') as output:
        nuggets = {}
        with open(nugget_file, 'r') as file:
            for line in file.readlines():
                qid, nugget_list = line.strip().split('\t')
                nuggets[qid] = ast.literal_eval(nugget_list)

        for qid in nuggets:
            q_counter = 1
            for i in range(0, len(nuggets[qid]), 10):
                current_nuggets = nuggets[qid][i:min(i + 10, len(nuggets[qid]))]
                messages = [
                    {
                        "role": "system",
                        "content": ("You are NuggetizeScoreLLM, an intelligent assistant that can label a list "
                                    "of atomic nuggets based on their importance for a given search query.")
                    },
                    {
                        "role": "user",
                        "content": (f'Based on the query, label each of the {len(current_nuggets)} nuggets '
                                    'either a vital or okay based on the following criteria. '
                                    'Vital nuggets represent concepts that must be present in a good answer; '
                                    'okay nuggets contribute worthwhile information but are not essential. '
                                    'Return the list of labels in a Pythonic list format (type: List[str]). '
                                    'The list should be in the same order as the input nuggets. '
                                    'Ensure a label for each nugget. '
                                    f'Search Query: {query_col[qid]} \n '
                                    f'Nugget List: {current_nuggets} \n '
                                    'Only return the list of labels (List[str]). Do not explain. '
                                    'Labels:')
                    }
                ]
                if model_name == 'gpt-4o':
                    response = openai.ChatCompletion.create(
                        model=model_name,
                        messages=messages,
                        temperature=0
                    )
                    response = response.choices[0].message.content
                elif model_name == 'llama3.2':

                    response: ChatResponse = chat(
                        model=model_name,
                        messages=messages,
                        options={"temperature": 0}
                    )
                    
                    response = response.message.content 
                
                try:
                    response = ast.literal_eval(response)
                except:
                    first_part, *middle, last_part = response.split('[')
                    last_part = last_part.split(']')[-1]
                    msg = '['.join(middle).split(']')[0] + ']'  # Extract valid list part
                    try:
                        response = ast.literal_eval(msg)
                    except:
                        continue
                if len(response) != len(current_nuggets):
                    continue
                for j in range(len(response)):
                    output.write(f'{qid}_{q_counter}\t{current_nuggets[j]}\t{response[j]}\n')
                    print(f'{dataset} {qid}_{q_counter}\t{response[j]}\n')
                    q_counter += 1

    input_file = f'{output_path}'
    output_file = f'nuggets_importance_sorted.{nugget_file}.txt'
    

    # Path to your data file
    file_path = input_file

    # Reading the data into a DataFrame
    df = pd.read_csv(file_path, sep="\t", names=['qid_index', 'subquery', 'priority'])

    # Extracting qid and index separately for easier manipulation
    df['qid'] = df['qid_index'].apply(lambda x: x.split('_')[0])
    df['index'] = df['qid_index'].apply(lambda x: x.split('_')[1]).astype(int)

    # Sorting by qid, priority (vital first), and then index
    df.sort_values(by=['qid', 'priority', 'index'], ascending=[True, False, True], inplace=True)

    # Reindexing within each group
    df['new_index'] = df.groupby('qid').cumcount() + 1

    # Creating a new qid_index column based on the new index
    df['new_qid_index'] = df['qid'] + "_" + df['new_index'].astype(str)

    df_filtered = df[df['new_index'] <= 20]

    # Saving only selected columns to a new file without headers
    df_filtered[['new_qid_index', 'subquery', 'priority']].to_csv(output_file, sep='\t', index=False, header=False)

    # Displaying the reordered DataFrame for verification (optional)
    print(df[['new_qid_index', 'subquery', 'priority']])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process nuggets file for importance labeling.")
    parser.add_argument("--model_name", type=str, required=True, help="Name of the model to use.")
    parser.add_argument("--nugget_file", type=str, required=True, help="Path to the nuggets file.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset identifier (e.g., 19, 20, 21, antique).")
    args = parser.parse_args()
    
    main(args.model_name, args.nugget_file, args.dataset)
