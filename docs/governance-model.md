# Governance Model

RAGLedger treats RAG data as a versioned, reviewable asset.

## Governance goals

- Know which corpus version backed an eval result.
- Detect document and chunk changes before indexing.
- Validate metadata before data enters retrieval workflows.
- Catch obvious sensitive patterns before corpus release.
- Produce reproducibility manifests for later review.

## Policy checks

The MVP supports:

- required metadata fields
- blocked patterns such as email, phone, SSN-like strings, and private keys
- duplicate document titles
- stale documents

## Limitations

Pattern checks are intentionally conservative and do not replace enterprise DLP, legal review, or domain-specific governance. They provide fast local feedback for engineering workflows.
