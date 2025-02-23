# LLM Relevance Judgment Comparison

This repository contains code and data for comparing different **relevance judgment methods** across two Large Language Models (LLMs): **GPT-4o** and **LLaMA 3.2** interms of **alignment with Human Labels** and **Agreement with System Rankings**

## 📌 Included Judgment Methods
This repository includes five relevance judgment methods:

1. **Pointwise**:  
   - [Binary](https://arxiv.org/abs/2304.09161)  
   - Graded ([UMBRELLA](https://github.com/castorini/umbrela/tree/main))
   
2. **Nugget-Based**:  
   - Document-Dependent ([AutoNuggetizer](https://arxiv.org/abs/2411.09607))  
   - Document-Agnostic ([Exam](https://github.com/laura-dietz/flan-t5-exam-appendix))
   
3. **Pairwise**:  
   - [Preference-based comparisons](https://github.com/claclark/preferences) between document pairs.

---

## 📂 Repository Structure

- **`Compatibility/`** → Contains scripts and data for System Ranking Analysis using [compatibility](https://github.com/claclark/Compatibility) metrics.
- **`Methods/`** → Includes various relevance judgment methods** implemented in this study.
- **`Pref/`** → Stores pairwise preference data and related scripts.
- **`data/`** → Contains queries, qrels, and qrels raw text of collections used in the experiments.
- **`raw_qrels/`** → Stores raw relevance judgments collected from both models using the four different methods.
- **`runs/`** → Includes TREC 2019, 2020, and 2021 runs and evalaution files for system ranking experiments.

---
