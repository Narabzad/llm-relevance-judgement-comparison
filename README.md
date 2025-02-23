# LLM Relevance Judgment Comparison

This repository contains code and data for comparing different **relevance judgment methods** across two Large Language Models (LLMs): **GPT-4o** and **LLaMA 3.2** interms of **alignment with Human Labels** and **Agreement with System Rankings**

## 📌 Relevance Judgment Methods
This repository includes five relevance judgment methods. The final output of each method is stored in the following directories:

- ```raw_qrels/gpt-4o``` for judgments made by GPT-4o  
- ```raw_qrels/llama3.2``` for judgments made by LLaMA 3.2  

The available methods are:

1. **Pointwise**:  
   - Binary [[paper](https://arxiv.org/abs/2304.09161)]  
   - Graded (Umbrela) [[paper](https://github.com/castorini/umbrela/tree/main)]
   
2. **Nugget-Based**:  
   - Document-Dependent (AutoNuggetizer) [[paper](https://arxiv.org/abs/2411.09607)]
      - Autonuggetizer All
      - Autonuggetizer All Strict
      - Autonuggetizer Vital
      - Autonuggetizer Vital Strict
      - Autonuggetizer Weighted
      - Autonuggetizer Weighted Strict
   - Document-Agnostic [Exam] [[paper](https://github.com/laura-dietz/flan-t5-exam-appendix))]
      - Exam Binary
      - Exam Graded Max
      - Exam Graded Mean    
   
3. **Pairwise**:  
   - Preference-based comparisons [[paper](https://github.com/claclark/preferences)]

---

## 📂 Repository Structure

- **`Compatibility/`** → Contains scripts and data for System Ranking Analysis using [compatibility](https://github.com/claclark/Compatibility) metrics.
- **`Methods/`** → Includes various relevance judgment methods** implemented in this study.
- **`Pref/`** → Stores pairwise preference data and related scripts.
- **`data/`** → Contains queries, qrels, and qrels raw text of collections used in the experiments.
- **`raw_qrels/`** → Stores raw relevance judgments collected from both models using the four different methods.
- **`runs/`** → Includes TREC 2019, 2020, and 2021 runs and evalaution files for system ranking experiments.

---
##  Running Judgements
We note that while our repository is configured for llama3.2 and gpt-4o, it can be adapted easily to any model working witht llama or OpenAI.

### Binary
  
### Umbrela
  
### Exam:  
This method includes the following steps:  

#### 1️) Rubrics Generation  
This stage generates 10 rubrics per query.  
Run the following command:  
```python methods/exam/exam_generate_rubrics.py --dataset ['19', '20', '21', 'antique'] --model_name ['llama3.2' or 'gpt-4o'] --api_key [if using OpenAI]```

#### 2) Rubrics Assignment
Rubrics can be assigned using either of the following methods:
- Binary: Checks whether each rubric is satisfied by each document (Yes/No).
```python methods/exam/exam_binary.py --dataset ['19', '20', '21', 'antique'] --model_name ['llama3.2' or 'gpt-4o'] --api_key [if using OpenAI]```
- Graded: Rates how much (on a scale of 0-5) the rubric is satisfied in the document.
```python methods/exam/exam_graded.py --dataset ['19', '20', '21', 'antique'] --model_name ['llama3.2' or 'gpt-4o'] --api_key [if using OpenAI]```

#### 3) Aggregation
For binary, we calculate the average number of satisfied rubrics (out of 10).

```python exam_generate_qrels_binary.py --input_dir [output of binary rubric assignment stage] --output_dir raw_qrels/[model_name]/exam_binary/```

For graded, we compute:
- Max relevance: The highest relevance score assigned to any rubric for a query.
- Mean relevance: The average relevance score across all rubrics assigned to a query.
      
```python exam_generate_qrels_graded.py --input_dir [output of binary rubric assignment stage] --output_dir raw_qrels/[model_name]/exam_graded/```

### Autonuggetizer

### Pariwise
