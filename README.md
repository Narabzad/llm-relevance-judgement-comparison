# LLM Relevance Judgment Comparison

This repository contains code and data for comparing different **relevance judgment methods** across two Large Language Models (LLMs): **GPT-4o** and **LLaMA 3.2**.

## 📌 Included Judgment Methods
This repository includes four relevance judgment methods:

1. **Pointwise**:  
   - **Binary** (0/1 relevance)  
   - **Graded** (*UMBRELLA*, multi-level relevance)
   
2. **Nugget-Based**:  
   - **Document-Dependent** (*AutoNuggetizer*)  
   - **Document-Agnostic** (*Exam*)
   
3. **Pairwise**:  
   - Preference-based comparisons between document pairs.

---

## 📂 Repository Structure

- **`Compatibility/`** → Contains scripts and data for **System Ranking Analysis** using compatibility metrics.
- **`Methods/`** → Includes various **relevance judgment methods** implemented in this study.
- **`Pref/`** → Stores **pairwise preference** data and related scripts.
- **`data/`** → Contains **queries, qrels, and other datasets** used in the experiments.
- **`raw_qrels/`** → Stores **raw relevance judgments** collected from both models using the four different methods.
- **`runs/`** → Includes TREC 2019, 2020, and 2021 runs and evalaution files for system ranking experiments.

---

Let me know if you need any further refinements! 🚀
