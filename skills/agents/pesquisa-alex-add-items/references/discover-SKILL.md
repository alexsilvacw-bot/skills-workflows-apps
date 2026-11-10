---
name: pesquisa-alex-discover
description: Discover, classify, and acquire open-web sources for Pesquisa Alex while maintaining a reproducible versioned corpus. Use only after an explicit `pesquisa-alex` invocation has passed its mandatory intent audit, or when the user explicitly invokes `pesquisa-alex-discover`; otherwise suggest Pesquisa Alex and wait for authorization. Use for logged discovery or enrichment, normalized research objects, inclusion and exclusion rationale, source coverage, local snapshots, and a validated manifest.
---

# Discover sources for Pesquisa Alex

Create or enrich an auditable discovery package. Discovery identifies candidates and sources; it does not establish decision-critical claims or produce the final recommendation.

## Preparation

1. Locate the paired `outline.yaml` and `fields.yaml` when they exist.
2. Read applicable `AGENTS.md` files and project context.
3. Resolve and read `references/contract.md` relative to the containing skill's `SKILL.md`.
4. Confirm the topic, geography, current date, candidate eligibility, required capabilities, and time range. Infer them from confirmed artifacts when possible.
5. Record a reproducible navigation plan in `discovery/run-config.json`: initial query and page allocations, elapsed-time limit, `budget_mode`, any predeclared minimum retained-candidate count, and source restrictions.
   - Default `budget_mode` to `adaptive`. When an allocation is reached before saturation, append a timestamped, reasoned `budget_extensions` entry and continue.
   - Use `budget_mode: hard` only when the user explicitly requests a bounded benchmark or cost ceiling. Never silently exceed the effective recorded limits.
6. Create `discovery/corpus/`. Prior knowledge, user suggestions, and project context may seed candidate leads but never count as evidence. When experimental isolation forbids prior lists, record that restriction explicitly.
7. Set or increment `corpus_revision`. Give every search-log and newly acquired manifest entry the active revision or iteration ID.

## Search and classify

1. Divide discovery into four passes before spending the budget:
   - broad category and local-language synonym queries;
   - capability-pair and alternative-category queries;
   - candidate expansion from directories, comparisons, and related-result terminology;
   - verification queries for identity, scope, key attributes, outcomes, limitations, recency, and independent evidence relevant to the confirmed fields.
2. Reserve at least 20% of the query budget for candidate expansion. Do not spend the entire budget verifying the first names found.
3. Append every issued query to `discovery/search-log.jsonl`, including `query_id`, revision or iteration ID, query family, exact query, timestamp, result URLs considered, URLs opened, and newly surfaced candidate IDs.
   Register each newly surfaced candidate ID in `candidates.json` immediately. Never leave a logged candidate ID without a candidate record.
4. At 50% and 80% of the query budget, run a recall checkpoint. Record cumulative candidate count, newly surfaced plausible direct candidates by query family, unused page budget, and the next expansion strategy.
5. Continue candidate expansion until two consecutive distinct expansion query families surface no new plausible direct or materially adjacent candidate.
   - In `adaptive` mode, reaching a query or page allocation triggers a recorded extension, not a stop.
   - Stop unsaturated only at the elapsed-time limit, an external interruption, or an explicit hard ceiling. Record `saturation_reached: false`, label the run `recall_limited`, and do not hand off normally.
6. Normalize aliases, versions, labels, and entity names into one candidate object when they refer to the same unit of analysis. Assign stable IDs.
7. Classify every surfaced candidate as:
   - `direct`: plausibly satisfies the recorded eligibility and object scope;
   - `adjacent`: overlaps materially but misses one or more essential scope criteria;
   - `inconclusive`: plausibly relevant, but acquired evidence is insufficient for direct, adjacent, or excluded;
   - `excluded`: affirmative evidence shows duplicate, irrelevant, discontinued, unavailable in scope, or otherwise outside the recorded rules.
8. Record concise rationale and supporting source IDs when acquired. A snippet or prior knowledge may create an `inconclusive` lead but cannot establish eligibility. Acquisition failure alone must remain `inconclusive`, not `excluded`.
9. Keep every discovered candidate, including exclusions and unresolved leads; this makes omissions, false positives, and aliases measurable.
10. Do not cap any retained class to a convenient report size. Retain every `direct`, `adjacent`, and `inconclusive` candidate for deep verification; control presentation later with synthesis, a dossier, and an appendix.
11. For a capability-count threshold, store the supporting source IDs for every counted capability. Treat an unsupported cell as `inconclusive`, not as evidence toward eligibility.
12. Flag apparent launch-stage, placeholder, illustrative, simulated, or coming-soon evidence. These candidates may remain direct, but must carry a maturity limitation rather than being silently promoted or discarded.

## Acquire and version sources

1. Prefer original or primary sources appropriate to each field. Seek independent, scholarly, institutional, or regulatory sources when corroboration, interpretation, outcomes, reputation, or external context matters.
2. Open each retained source and save a UTF-8 Markdown or text snapshot under `discovery/corpus/`. Preserve literal source text used later as evidence; add provenance metadata without paraphrasing the quoted body. During enrichment, add new snapshots without overwriting older revisions.
3. Register every snapshot in `discovery/source-manifest.json` with:
   - `source_id`, title, publisher, original URL, final URL when redirected;
   - `source_type`: `official`, `independent`, `regulatory`, or `other`;
   - candidate IDs and field or capability coverage;
   - access timestamp and publication or update date when visible;
   - corpus-relative `local_path`, SHA-256 hash, and acquisition status;
   - corpus revision or iteration ID;
   - limitation notes for dynamic, blocked, partial, translated, or stale content.
4. Never register a snippet-only result as an acquired source. Mark inaccessible or failed pages in the manifest with no local path and a clear status.
5. Do not treat a local snapshot as proof that the publisher's assertion is true. It only freezes what was accessible during the run.

## Discovery outputs

Create all of these under `discovery/`:

- `run-config.json`: frozen scope, navigation plan, extensions, corpus revision, and handoff conditions;
- `search-log.jsonl`: complete query and navigation log;
- `candidates.json`: normalized candidates, aliases, classification, rationale, source IDs, eligibility evidence, and maturity limitations;
- `coverage.json`: candidate-by-capability and field coverage using `supported`, `not_found`, `not_searched`, or `inconclusive`;
- `source-manifest.json`: source metadata and corpus paths;
- `corpus/`: acquired snapshots;
- `discovery-summary.md`: readable direct, adjacent, inconclusive, and excluded lists plus coverage gaps and navigation use.

The summary must state whether saturation was reached, whether discovery is recall-limited, every budget extension, actual usage, corpus revision, retained and excluded counts, and which candidates were found only during expansion passes.

Use explicit absence states. `not_found` means the planned search was performed within this run's budget; it does not prove global absence from the internet.

## Validate and hand off

Resolve the validator relative to this skill directory and run it with an available Python 3 interpreter:

```bash
python3 scripts/validate_discovery.py \
  --discovery /absolute/path/to/discovery \
  --write
```

Fix structural, reference, path, and hash failures. The validator does not judge candidate relevance or source truth.

Before deep research:

1. Present all normalized candidates, including inconclusive leads and exclusions, plus coverage gaps, saturation state, corpus revision, and navigation use.
2. Require `validation-summary.json` to report `handoff_ready: true`. A structurally valid `recall_limited` run is not ready unless the user explicitly accepts the limitation in `run-config.json`. In a comparison with a predeclared minimum retained-candidate count, also require that minimum.
3. After confirmation, update `outline.yaml` with every `direct`, `adjacent`, and `inconclusive` item, `authorized_corpus: ./discovery/corpus`, `source_manifest: ./discovery/source-manifest.json`, and `corpus_revision`.
4. Preserve the validated revision. Add candidates or sources through a new recorded discovery iteration, then revalidate; never silently edit the corpus.
5. Before continuing to `pesquisa-alex-deep`, return to the mandatory execution-destination gate in `pesquisa-alex`: ask whether deep research will run in the current environment or an external executor. If external, create the handoff package and stop locally.
