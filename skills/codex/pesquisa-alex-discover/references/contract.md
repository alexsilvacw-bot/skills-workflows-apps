# Pesquisa Alex — shared research contract

This file is the single source of truth for all experimental entry points.

The contract is implementation-neutral and domain-neutral. A human, software workflow, or language model may execute it. Do not assume or name a particular model, provider, industry, object type, or decision pattern in research artifacts unless the confirmed project context requires it.

## Open-web discovery and corpus acquisition

When no authorized corpus exists, run discovery before deep research. Discovery must produce a reproducible navigation plan, exact query log, normalized candidate register, source-coverage matrix, source manifest, and local corpus snapshots.

Discovery must separate broad search, capability expansion, candidate expansion, and verification. Reserve search capacity for expansion and record recall checkpoints. Treat query and page allocations as auditable planning increments, not production stopping rules. In normal open-web research, extend them explicitly and continue until two consecutive distinct expansion query families add no plausible direct or materially adjacent candidate. Use a hard ceiling only when the user explicitly requests a bounded benchmark or cost limit.

If a hard ceiling or external interruption prevents saturation, mark the run `recall_limited`. A `recall_limited` package is structurally valid but is not ready for ordinary deep-research handoff unless the user explicitly accepts the limitation. If a comparison condition has a predeclared minimum candidate count, record it before discovery and do not hand off below it. Never cap eligible candidates merely to shorten the report.

Register every surfaced candidate ID immediately, including weak leads. Classify evaluated candidates as `direct`, `adjacent`, `inconclusive`, or `excluded`, with rationale. Use `inconclusive` when a plausible candidate lacks enough acquired evidence; acquisition failure alone is not exclusion. Reserve `excluded` for affirmative evidence of duplication, irrelevance, unavailability in scope, or another recorded exclusion rule. Preserve aliases, inconclusive candidates, and exclusions so omissions, duplicates, and false positives remain measurable. A snippet may create an inconclusive lead but cannot by itself establish eligibility.

For eligibility based on a capability threshold, associate every counted capability with supporting source IDs. Record maturity limitations for placeholder, illustrative, simulated, launch-stage, or coming-soon evidence.

Every acquired source must retain its original URL, access time, source type, corpus-relative local path, SHA-256 hash, and acquisition limitations. A snapshot freezes accessible source content; it does not verify publisher claims or source truth. Failed or inaccessible sources remain in the manifest with an explicit acquisition status and no fabricated snapshot.

Discovery absence states use `not_found`, `not_searched`, and `inconclusive`. Here, `not_found` means not found within the recorded queries and budget, never absent from the entire internet.

Deep research normally includes every `direct`, `adjacent`, and `inconclusive` candidate; only confirmed exclusions stay outside the item list. It may begin only after the candidate set is confirmed and discovery validation reports `handoff_ready: true`.

The corpus is versioned, not permanently closed. Deep research may request a recorded enrichment iteration when missing evidence could change eligibility, a decisive answer, or a material field. Append exact queries to the search log, register every new candidate, acquire new snapshots, update the manifest and hashes, increment the corpus revision, revalidate, and then resume. Never cite or use a newly found source before it is registered. This preserves auditability without turning early acquisition gaps into permanent information loss.

## Decisive questions

Define key questions that determine whether the research purpose has been answered. They may support a decision, explanation, assessment, synthesis, or descriptive account. Each critical claim must reference at least one valid `question_id` and declare one role:

- `answer`: directly answers the question;
- `premise`: is required to support an answer;
- `counterevidence`: limits or contradicts an answer;
- `context`: helps interpretation but does not decide alone.

## Critical claim

A critical claim contains one verifiable proposition. Split a sentence when parts could have different truth values or require different evidence.

```json
{
  "claim_id": "C01",
  "claim_text": "One atomic proposition",
  "decision_question_ids": ["Q01"],
  "claim_role": "answer",
  "critical": true,
  "criticality_source": "brief",
  "source_id": "S03",
  "evidence_quote": "Literal excerpt from the source",
  "evidence_location": {"section": "Results", "paragraph": 4},
  "quote_match": "unchecked",
  "semantic_support": "unreviewed",
  "reviewed_by": null,
  "limitations": []
}
```

Use `criticality_source: brief` for planned critical claims. Use `emerging` only with a non-empty `criticality_reason`.

## Two verification layers

### Deterministic provenance

The validator checks source IDs, corpus paths, literal normalized quote presence, recoverable locations, internal references, and non-empty critical fields. It writes `quote_match: passed|failed`. Call this quote matching or structural validation, never truth verification.

Normalization may collapse whitespace and apply Unicode normalization. It must not paraphrase, remove words, or use semantic similarity.

### Semantic support

Allowed values:

- `full`
- `partial`
- `irrelevant`
- `contradicted`
- `inconclusive`
- `unreviewed`

Every reviewed claim must include:

```json
{
  "type": "human",
  "id": "alex",
  "protocol": "single_human_source_masked",
  "reviewed_at": "2026-07-17"
}
```

`type` is `human` or `model`. A model judgment remains model-reviewed; model agreement is not human review.

## Explicit absence

Use one of:

- `not_found`: searched in the authorized corpus; no support found;
- `not_searched`: required search was not run;
- `not_applicable`: question or field does not apply;
- `inconclusive`: relevant material exists but does not permit a conclusion.

Represent decisive-question disposition in each result:

```json
{
  "question_id": "Q01",
  "status": "not_found",
  "notes": "Corpus paths searched and relevant limitation"
}
```

Do not silently omit these states from reports.

## Result envelope

```json
{
  "item_id": "I01",
  "item_name": "Example",
  "fields": {},
  "sources": [
    {"source_id": "S01", "title": "Source title", "path": "documents/source.txt"}
  ],
  "question_dispositions": [],
  "critical_claims": []
}
```

## Delivery gates

Assign `draft` if any critical claim:

- lacks source, literal quote, or recoverable location;
- has `quote_match` other than `passed`;
- is `unreviewed`;
- lacks human semantic review;
- is `irrelevant` or `contradicted` but presented as established;

or if a decisive question has neither a supported answer nor an explicit absence disposition.

Assign `decision_ready` only when all critical claims have `quote_match: passed` and human semantic review; partial, inconclusive, and conflicting claims are qualified; every decisive question is answered or explicitly closed; and critical limitations are visible.

The gate verifies recorded process and support, not source truth.
