QRELS_DIR = ../data
TREC_SCRIPT = trec.py
EVAL_SCRIPT = trec_eval.sh
DATASETS = dl19 dl20 dl21
NDCG_TARGETS = $(addsuffix .ndcg_cut10, $(DATASETS))

all: $(NDCG_TARGETS)

%.ndcg_cut10: $(TREC_SCRIPT) %.trec_eval
	./$(TREC_SCRIPT) $*.trec_eval > $@

%.trec_eval: $(EVAL_SCRIPT)
	./$(EVAL_SCRIPT) $* $(QRELS_DIR)/qrels.$*-passage.txt > $@
