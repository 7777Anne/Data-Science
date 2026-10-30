# Industrial Knowledge Assistant — a citation-backed RAG learning project

A small, inspectable Applied AI demo for a fictional production environment. It retrieves relevant passages from maintenance, line-changeover and quality-control SOPs, answers questions, and returns citations.

**Status:** working baseline with offline TF-IDF retrieval and *extractive* answers. Optional neural embedding retrieval (Sentence Transformers + FAISS) and optional local LLM generation (Ollama). This is not a validated industrial production system, and no proprietary Mercedes-Benz data is used.

## Architecture

    Fictional Markdown SOPs
              |
       Paragraph chunking
              |
       TF-IDF index [default] OR SentenceTransformer + FAISS [optional]
              |
       Ranked passages + relevance cutoff
              |
       Extractive answer [default] OR local Ollama prompt [optional]
              |
       Answer + source filenames + excerpts + scores
              |
           FastAPI

## Run the baseline

Requires Python 3.11 or newer. From this folder:

    python -m venv .venv
    source .venv/bin/activate             # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app:app --reload

Open http://127.0.0.1:8000/docs and POST to /ask, or use:

    curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question":"What should we do if conveyor bearings exceed 75 C?"}'

Sample output contains the answer, grounded flag, retrieval backend, generator, and cited source excerpts. /health is available for a health check.

## Try neural vector search (optional)

    pip install -r requirements-semantic.txt
    RETRIEVAL_BACKEND=faiss uvicorn app:app --reload

The default embedding model is sentence-transformers/all-MiniLM-L6-v2. Its weights are downloaded on first use; this mode requires internet for initial installation/download. The default TF-IDF mode does not require downloaded models.

## Try actual LLM generation (optional)

Install Ollama separately and pull a suitable model:

    ollama pull llama3.2:3b
    ollama serve

In POST /ask, set generator to "ollama" rather than "extractive". This sends retrieved context to a **locally running** Ollama instance at http://localhost:11434/api/generate. The assistant abstains when retrieval finds no sufficiently relevant passages. Generation can still hallucinate; citations indicate *retrieved passages*, not a formal proof of each generated claim.

## Tests and lightweight evaluation

    pytest -q tests
    python evaluate.py

Tests cover document loading, retrieval, out-of-scope abstention and the API. The evaluation script contains a tiny hand-authored smoke-test set only: it is **not** evidence of real-world accuracy or model superiority.

## Real engineering limitations and future experiments

- TF-IDF lexical retrieval misses synonyms. Compare it to FAISS embeddings on a larger annotated corpus.
- Relevance cutoffs are heuristics and need tuning against known unanswered questions.
- Corpus is synthetic, small and English-only. No OCR, document updates or access controls.
- Local model responses are not automatically fact-checked. Add faithfulness and citation-precision evaluation before deployment.
- For enterprise use, add authentication, document-level authorization, observability, PII redaction, prompt-injection testing, cost/latency measurement and CI deployment.
- Build a reproducible test set with recall@k, MRR, groundedness, p95 latency and abstention accuracy; avoid tuning on the final test set.
- No company-confidential records, copyrighted OEM manuals or actual safety-critical operating instructions belong in this demo.

## Portfolio context

This is an independently reproducible learning project exploring document QA, local RAG components and industrial workflows. It does **not** imply this system was used at Mercedes-Benz or deployed at Subex.

### Index lifetime
The retriever is cached per backend so repeated FastAPI requests do not rebuild the same TF-IDF index. Restart the service to load new documents. For a real deployment use versioned corpus snapshots and explicit cache invalidation.
