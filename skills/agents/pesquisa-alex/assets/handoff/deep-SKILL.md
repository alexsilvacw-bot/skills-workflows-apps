---
name: pesquisa-alex-deep
description: Execute or resume Pesquisa Alex from outline.yaml and fields.yaml against an authorized versioned corpus. Use only after an explicit `pesquisa-alex` invocation has passed its mandatory intent audit, or when the user explicitly invokes `pesquisa-alex-deep`; otherwise suggest Pesquisa Alex and wait for authorization. Use when robust research must produce per-item JSON, atomic critical claims with literal evidence and locations, explicit absence states, deterministic quote matching, and review-aware delivery gates without inheriting early discovery gaps.
---

# Deep Pesquisa Alex

## Preparation

1. Locate the paired `outline.yaml` and `fields.yaml`.
2. Read applicable `AGENTS.md` files and relevant project context.
3. Resolve and read `contract.md` beside this phase instruction.
4. Read `outline.execution_handoff`. If it is absent or unconfirmed in a Pesquisa Alex outline, stop and ask whether execution will occur in the current environment or an external executor. If it selects an external executor but the current environment is not that confirmed destination, stop and provide or repair the handoff package instead of running deep research.
5. Resolve `authorized_corpus` and `output_dir` relative to `outline.yaml`.
6. If `authorized_corpus` is missing or `pending_discovery`, stop and route to `pesquisa-alex-discover`.
7. When `source_manifest` is present, require a passing discovery validation summary with `handoff_ready: true` and verify that the manifest paths resolve inside the authorized corpus.
8. Do not cite or use unregistered external sources. When additional web evidence is needed, read `discover-SKILL.md`, run a recorded discovery enrichment iteration, acquire it into the authorized corpus, update the manifest and revision, revalidate with `validate_discovery.py`, and resume.
9. Skip existing results only when they pass the experimental validator.

## Execution

Process sequentially unless the user explicitly requests delegation. Ask before each new batch unless the full run was authorized.

For every item:

1. Search the authorized corpus for the defined fields and decisive questions.
2. Before finalizing `not_found`, `inconclusive`, or an eligibility downgrade, decide whether the missing evidence could change a key answer, classification, material attribute, temporal validity, comparison, explanation, assessment, or implication. If yes, run a focused recorded enrichment iteration rather than treating the initial corpus gap as final.
3. If enrichment surfaces a new plausible candidate, register it immediately. Add `direct`, `adjacent`, and `inconclusive` candidates to the outline and process them before completion; retain confirmed exclusions in the discovery register.
4. Record sources in the result JSON with unique `source_id`, corpus-relative `path`, and a useful title.
5. Fill supported fields. For unsupported or inapplicable fields after any material enrichment, record `not_found`, `not_searched`, `not_applicable`, or `inconclusive`; never invent a plausible value.
6. Extract only decision-critical claims into `critical_claims`. Make each claim one independently verifiable proposition.
7. Link every critical claim to one or more decisive questions and use role `answer`, `premise`, `counterevidence`, or `context`.
8. Preserve emerging critical claims with `criticality_source: emerging` and a concise `criticality_reason`.
9. Preserve counterevidence even when it weakens the likely conclusion.
10. Copy literal evidence from one registered source and record a recoverable location.
11. Set `quote_match` to `unchecked`; never label truth as verified.
12. Set new semantic judgments to `unreviewed`, with `reviewed_by: null`.
13. Save as `{output_dir}/{item_name_slug}.json`.
14. Resolve the validator path relative to this skill directory and run it with an available Python 3 interpreter:

```bash
python3 validate_research.py \
  --outline /absolute/path/to/outline.yaml \
  --fields /absolute/path/to/fields.yaml \
  --results /absolute/path/to/results \
  --write
```

Fix structural and quote-match failures. Do not fabricate a semantic review. Model review, when explicitly requested, must use `reviewed_by.type: model` and cannot unlock `decision_ready`.

## Completion

Report completed, skipped, failed, and explicit-absence results. State whether the validator assigned `draft` or `decision_ready` and why. Preserve partial results for safe resume.
