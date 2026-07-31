"""
Evaluate the Medic RAG pipeline with RAGAS.

Splits evaluation into two concerns, run in the same pass so retrieval and
generation are measured against the *same* retrieved context per question:

Retrieval quality (is the vector store finding the right chunks?)
    - LLMContextPrecisionWithReference: are the top-k retrieved chunks
      actually relevant (low ranking noise)?
    - LLMContextRecall: does the retrieved context contain everything needed
      to produce the reference answer (nothing important missing)?

Response quality (given what was retrieved, is the LLM's answer good?)
    - Faithfulness: is every claim in the answer grounded in the retrieved
      context (no hallucination)?
    - ResponseRelevancy: does the answer actually address the question asked?
    - AnswerCorrectness: how close is the answer to the reference answer,
      combining factual overlap and semantic similarity?

Usage:
    cd Medic
    pip install -r eval/requirements-eval.txt
    python -m eval.run_ragas_eval
    python -m eval.run_ragas_eval --k 5 --limit 5   # quick smoke test
    python -m eval.run_ragas_eval --out eval/results/my_run.csv

Requires GOOGLE_API_KEY in the environment (or .env), same as the app.
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))  # allow `from rag.chatbot import ...`

load_dotenv(BASE_DIR / ".env")

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.run_config import RunConfig
from ragas.metrics import (
    AnswerCorrectness,
    Faithfulness,
    LLMContextPrecisionWithReference,
    LLMContextRecall,
    ResponseRelevancy,
)

from eval.golden_dataset import GOLDEN_SET

RETRIEVAL_METRIC_NAMES = {"llm_context_precision_with_reference", "context_recall"}
RESPONSE_METRIC_NAMES = {"faithfulness", "answer_relevancy", "answer_correctness"}


def build_samples(golden_set, k: int) -> list[SingleTurnSample]:
    """Run the real app pipeline (retrieval + generation) for every question."""
    # Imported lazily: importing rag.chatbot triggers vector store load/sync,
    # so we only pay that cost once we actually need it.
    from rag.chatbot import get_response, vector_store

    samples = []
    for i, item in enumerate(golden_set):
        question = item["question"]
        reference = item["reference"]

        print(f"[{i + 1}/{len(golden_set)}] Retrieving + generating for: {question!r}")

        retrieved_docs = vector_store.similarity_search(question, k=k)
        retrieved_contexts = [d.page_content for d in retrieved_docs]

        # Fresh thread per question so chat history from one eval question
        # doesn't leak into the next (each sample must be independently gradable).
        thread_id = f"eval-{uuid.uuid4()}"
        answer, _options = get_response(question, thread_id=thread_id)

        samples.append(
            SingleTurnSample(
                user_input=question,
                retrieved_contexts=retrieved_contexts,
                response=answer,
                reference=reference,
            )
        )
    return samples


def get_judge_models():
    """LLM + embeddings RAGAS uses to *grade* the pipeline.

    Deliberately configurable and separate from the app's generation model
    (RAGAS_EVAL_MODEL) so you can judge with a stronger model than the one
    being evaluated, avoiding the app grading its own homework with identical
    biases.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Add it to your environment or Medic/.env."
        )

    judge_model_name = os.getenv("RAGAS_EVAL_MODEL", "models/gemini-2.5-pro")
    judge_llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(model=judge_model_name, temperature=0, google_api_key=api_key)
    )
    judge_embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    )
    return judge_llm, judge_embeddings


def run(k: int, limit: int | None, out_path: Path, max_workers: int, max_retries: int, max_wait: int):
    golden_set = GOLDEN_SET[:limit] if limit else GOLDEN_SET
    if not golden_set:
        raise ValueError("Golden dataset is empty.")

    samples = build_samples(golden_set, k=k)
    dataset = EvaluationDataset(samples=samples)

    judge_llm, judge_embeddings = get_judge_models()

    metrics = [
        # retrieval
        LLMContextPrecisionWithReference(llm=judge_llm),
        LLMContextRecall(llm=judge_llm),
        # response
        Faithfulness(llm=judge_llm),
        ResponseRelevancy(llm=judge_llm, embeddings=judge_embeddings),
        AnswerCorrectness(llm=judge_llm, embeddings=judge_embeddings),
    ]

    # RAGAS defaults to 16 concurrent judge calls, which blows through Gemini's
    # RPM limits on free/lower tiers and surfaces as 429 errors (often shown as
    # silently NaN'd-out scores rather than a hard crash). Throttle concurrency
    # and let it retry-with-backoff instead.
    run_config = RunConfig(max_workers=max_workers, max_retries=max_retries, max_wait=max_wait)

    print(
        f"\nRunning RAGAS evaluation over {len(samples)} samples with {len(metrics)} metrics "
        f"(max_workers={max_workers}, max_retries={max_retries})...\n"
    )
    result = evaluate(dataset=dataset, metrics=metrics, run_config=run_config)

    df = result.to_pandas()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print_report(df)
    print(f"\nPer-sample results saved to: {out_path}")


def print_report(df: pd.DataFrame):
    score_cols = [c for c in df.columns if c not in {"user_input", "retrieved_contexts", "response", "reference"}]

    retrieval_cols = [c for c in score_cols if c in RETRIEVAL_METRIC_NAMES]
    response_cols = [c for c in score_cols if c in RESPONSE_METRIC_NAMES]

    print("\n" + "=" * 60)
    print("RETRIEVAL EVAL (is the vector store finding the right chunks?)")
    print("=" * 60)
    if retrieval_cols:
        print(df[retrieval_cols].mean(numeric_only=True).round(3).to_string())
    else:
        print("No retrieval metrics found in results.")

    print("\n" + "=" * 60)
    print("RESPONSE EVAL (is the generated answer good, given what was retrieved?)")
    print("=" * 60)
    if response_cols:
        print(df[response_cols].mean(numeric_only=True).round(3).to_string())
    else:
        print("No response metrics found in results.")

    print("\n" + "=" * 60)
    print("LOWEST-SCORING QUESTIONS (worth a manual look)")
    print("=" * 60)
    if score_cols:
        df["_overall"] = df[score_cols].mean(axis=1, numeric_only=True)
        worst = df.sort_values("_overall").head(5)
        for _, row in worst.iterrows():
            print(f"- ({row['_overall']:.2f}) {row['user_input']}")


def main():
    parser = argparse.ArgumentParser(description="RAGAS eval for the Medic RAG pipeline")
    parser.add_argument("--k", type=int, default=7, help="Top-k chunks to retrieve (matches rag/chatbot.py's chat())")
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N golden questions (smoke test)")
    parser.add_argument(
        "--out",
        type=Path,
        default=BASE_DIR / "eval" / "results" / "ragas_eval_results.csv",
        help="Where to write per-sample CSV results",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Concurrent judge-LLM calls (ragas default is 16, which hits rate limits fast). Lower = slower but safer.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=15,
        help="Retries per judge call on failure/429 before giving up on that sample.",
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=90,
        help="Max seconds to back off between retries.",
    )
    args = parser.parse_args()
    run(
        k=args.k,
        limit=args.limit,
        out_path=args.out,
        max_workers=args.max_workers,
        max_retries=args.max_retries,
        max_wait=args.max_wait,
    )


if __name__ == "__main__":
    main()