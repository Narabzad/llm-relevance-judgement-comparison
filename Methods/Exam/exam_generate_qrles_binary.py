import os
import numpy as np
import argparse

def compute_mean_relevance(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        input_file = os.path.join(input_dir, file)
        output_file = os.path.join(output_dir, f'exam_binary.qrels.mean.{file}')

        if os.path.isfile(input_file):
            rel_col = {}

            with open(input_file, 'r') as f:
                for line in f.readlines():
                    qid, _, pid, rel = line.strip().split()
                    qid, subjectid = qid.split('_')
                    rel_col.setdefault((qid, pid), []).append(int(rel))

            with open(output_file, 'w') as output:
                for (qid, pid), rels in rel_col.items():
                    output.write(f'{qid} 0 {pid} {np.mean(rels):.2f}\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute mean relevance scores from input files and store them in the output directory.")
    parser.add_argument('--input_dir', type=str, required=True, help='Path to input directory containing relevance files.')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to output directory for storing mean qrels.')

    args = parser.parse_args()

    compute_mean_relevance(args.input_dir, args.output_dir)
