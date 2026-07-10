# RAGLedger

Local-first control plane for RAG corpus versioning, eval data provenance, and retrieval reproducibility.

RAGLedger helps AI engineers and data platform teams snapshot, diff, validate, and reproduce the datasets used by retrieval-augmented generation and AI evaluation workflows.

## Why RAGLedger?

RAG quality is not only a model problem. It is also a data control-plane problem.

When a retrieval-augmented generation system changes behavior, teams need to know whether the change came from the corpus, chunking, metadata, policy violations, prompt changes, retriever settings, or evaluation data. RAGLedger makes the data side visible and reproducible.

## Current MVP

- Local project initialization
- Corpus registry
- Document fingerprinting
- Paragraph-based chunking
- Versioned corpus snapshots
- Snapshot diffing
- Policy validation for metadata, duplicate titles, stale documents, and sensitive patterns
- Reproducibility manifest generation
- Text and HTML reporting
- Example support knowledge base
- Example policy file
- CLI workflow
- Test suite and CI

## Install locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 60-second demo

```bash
ragledger init
ragledger register examples/support_kb --name support_kb
ragledger snapshot support_kb
ragledger list-snapshots support_kb
ragledger validate --corpus support_kb:v1 --policy policies/rag_data_policy.yml
ragledger manifest --corpus support_kb:v1 --output .ragledger/manifests/support_kb_v1.yml
ragledger report --html
```

## Diff workflow

Create a second snapshot after changing the corpus, then compare:

```bash
ragledger snapshot support_kb
ragledger diff support_kb:v1 support_kb:v2
```

The diff reports added, removed, and changed documents and chunks.

## CLI

```bash
ragledger init
ragledger register <path> --name <corpus_name>
ragledger snapshot <corpus_name>
ragledger list-corpora
ragledger list-snapshots <corpus_name>
ragledger diff <corpus:v1> <corpus:v2>
ragledger validate --corpus <corpus:v1> --policy policies/rag_data_policy.yml
ragledger manifest --corpus <corpus:v1> --output manifest.yml
ragledger report
ragledger report --html
```

## What RAGLedger tracks

For each document:

- relative path
- file hash
- byte size
- modified time
- detected title
- metadata block
- chunk count

For each chunk:

- stable chunk id
- chunk hash
- character count
- source document path

## What this does not solve

RAGLedger is not a vector database, embedding service, model evaluation platform, or hosted governance product. It is a local-first control plane for tracking and validating RAG/eval data changes before those changes reach retrieval indexes and evaluation pipelines.

## Design principles

- Local-first by default
- Plain files over hidden services
- Reproducibility over dashboards
- Clear diffs over vague quality scores
- Practical policy checks over inflated claims
- Built for engineers who need fast feedback

## License

MIT
