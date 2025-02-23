# LLM Relevance Judgment Comparison

This repository contains code and data for comparing different relevance judgments methods made by two Large Language Models (LLMs) gpt-4o and llama3.2.
The methods included in this repo:
 pointiwse: binary graded(UMBRELA)
 nuggetbased: document dependet (autonuggeizer), document agnostic (exam)
 pairwise

## Repository Structure

- **Compatibility/**: Contains scripts and data related to System Ranking Analysis with compatibility.
- **Methods/**: Includes various methods and approaches implemented for relevance judgment.
- **Pref/**: Pairwises preference data and related scripts.
- **data/**: queries, qrels and other data .
- **raw_qrels/**:  raw relevance judgments collected from both models and 4 different methods.
- **runs/**: TREC 19,20,21 runs for system ranking experiment.

