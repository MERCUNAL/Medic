# RAGAS evaluation for the Medic RAG pipeline

Evaluates the chatbot in `rag/chatbot.py` on two levels, using [RAGAS](https://docs.ragas.io/):

1. **Retrieval eval** — is `vector_store.similarity_search(...)` pulling back the right chunks?
   - `LLMContextPrecisionWithReference` — are the top-k chunks actually relevant (low noise/ranking quality)?
   - `LLMContextRecall` — does the retrieved context contain everything needed to answer correctly (nothing important missing)?
2. **Response eval** — given what was retrieved, is the generated answer good?
   - `Faithfulness` — is every claim grounded in the retrieved context (no hallucination)?
   - `ResponseRelevancy` — does the answer address the question asked?
   - `AnswerCorrectness` — how close is the answer to a known-good reference answer?

Each question is run through the **real** pipeline end-to-end (real Chroma retrieval + real Gemini generation via `get_response`), so scores reflect production behavior, not a mocked-out sandbox.

## Files

- `golden_dataset.py` — curated question / reference-answer pairs pulled from the three sources the app actually embeds (`Medical_list_with_specs.csv`, `FAQ.docx`, `Log and sign.docx`), plus one out-of-scope question that should trigger the "I do not have that information" fallback. Add more entries here as the product's documents/catalogue grow.
- `run_ragas_eval.py` — runs the pipeline over the golden set, scores it with RAGAS, prints a retrieval/response summary, and writes per-question scores to CSV.

## Setup

RAGAS's latest release currently breaks on import against the latest `langchain-community` (it references a `vertexai` submodule that was removed upstream), so this uses a pinned, verified-working combination in a **separate** requirements file:

```bash
cd Medic
pip install -r requirements.txt -r eval/requirements-eval.txt
```

Make sure `GOOGLE_API_KEY` is set (same variable the app already uses — via `.env` or your shell), and that `chroma_db_new/` is already populated (i.e., `rag/chatbot.py` has been run at least once so the CSV catalogue is embedded).

## Running

```bash
python -m eval.run_ragas_eval
```

Useful flags:

```bash
# Quick smoke test on the first 5 questions only
python -m eval.run_ragas_eval --limit 5

# Match a different retrieval k (rag/chatbot.py currently uses k=7)
python -m eval.run_ragas_eval --k 5

# Custom output path
python -m eval.run_ragas_eval --out eval/results/run_2026_07_31.csv
```

## Judge model

By default RAGAS grades with `models/gemini-2.5-pro` (deliberately a stronger/different model than the app's own `gemini-3.1-flash-lite`, so the pipeline isn't grading its own homework). Override with:

```bash
export RAGAS_EVAL_MODEL=models/gemini-2.5-pro
```

## Output

The script prints two grouped summaries (retrieval metrics, response metrics) plus the 5 lowest-scoring questions worth a manual look, and saves full per-question scores to `eval/results/ragas_eval_results.csv` (gitignored — see below).

## Notes

- Each golden question runs in its own fresh conversation thread, so scores reflect single-turn quality and aren't polluted by chat history from earlier eval questions.
- Add `eval/results/` to `.gitignore` if you don't want to commit raw run output.
- If you change `rag/chatbot.py`'s retrieval `k` or the system prompt, re-run this eval — that's the point.
