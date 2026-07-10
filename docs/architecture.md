# RAGLedger Architecture

RAGLedger is a local-first control plane for RAG corpus versioning and eval data provenance.

```text
local documents
  -> corpus registry
  -> document inspection
  -> chunking
  -> snapshot store
  -> diff / validate / manifest / report
```

## Components

### Corpus registry

The registry maps a stable corpus name to a local folder path. It is stored in `.ragledger/registry.yml`.

### Document inspection

Documents are fingerprinted by path, SHA-256 hash, byte size, modified time, title, metadata, and chunks.

### Chunking

The MVP uses deterministic paragraph-based chunking. This keeps diffs easy to understand and avoids introducing a dependency on a RAG framework.

### Snapshots

Snapshots are stored as JSON files in `.ragledger/snapshots/<corpus>/<version>.json`.

### Diffing

Diffing compares document and chunk hashes across two snapshots and reports added, removed, and changed documents and chunks.

### Policy validation

Validation checks required metadata, duplicate titles, stale documents, and blocked sensitive patterns.

### Reproducibility manifest

The manifest captures corpus version, corpus hash, chunking config, retriever config, prompt version, and eval set so an eval can be reproduced later.
