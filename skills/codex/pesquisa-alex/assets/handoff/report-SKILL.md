---
name: pesquisa-alex-report
description: Consolidate Pesquisa Alex results into an audience-appropriate, question-driven report, an optional object dossier, and an auditable evidence appendix. Use only after an explicit `pesquisa-alex` invocation has passed its mandatory intent audit, or when the user explicitly invokes `pesquisa-alex-report`; otherwise suggest Pesquisa Alex and wait for authorization. Use across comparisons, landscapes, diagnostics, evidence syntheses, assessments, and descriptive investigations without forcing a domain-specific template.
---

# Pesquisa Alex report

## Preparation

1. Locate `outline.yaml`, `fields.yaml`, the configured results directory, and `validation-summary.json`.
2. Read applicable project instructions.
3. Resolve and read `contract.md` beside this phase instruction.
4. Read `report-routing.md` completely before selecting the report structure.
5. Read `outline.reporting`. When absent or set to `auto`, infer the audience, primary use, report mode, detail level, and dossier need from the research purpose and key questions. State material assumptions in the method note.
6. Resolve `validate_research.py` beside this phase instruction. Run it with an available Python 3 interpreter and treat its delivery status as authoritative for process gates.
7. Reconcile the item set with discovery. Every retained item must have a result or appear in a visible incomplete-research register with the reason.

## Output package

Always generate:

- `report.md`: answer-first narrative for the intended reader;
- `audit-appendix.md`: exhaustive evidence and process traceability.

Generate `research-dossier.md` when multiple items contain decision-relevant detail that would otherwise be lost or force the reader to inspect JSON files. In `auto` mode, create it whenever compact treatment in `report.md` would omit material item-level evidence, counterevidence, or uncertainty. Do not create an empty or token dossier.

## Report routing

Choose structure from the purpose and key questions, never from the topic label alone. Support mixed modes when different questions require different forms.

Use this core order, merging or omitting inapplicable sections without omitting any key question:

1. Primary answer or synthesis. Recommend an action only when the research purpose calls for a decision.
2. Answers to each key question, using natural-language headings.
3. Adaptive synthesis appropriate to the selected mode.
4. Material evidence, counterevidence, trade-offs, or exceptions needed to interpret the answers.
5. Important gaps, conflicts, sensitivity, and conditions that could change the conclusion.
6. Implications or next steps when useful.
7. Brief method and delivery status.

Organize the narrative by key questions. Use field categories as evidence inputs, not as a mandatory table of contents.

## Presentation rules

- Lead with the answer, synthesis, or state of knowledge. Do not force a recommendation, ranking, shortlist, or winner.
- Translate identifiers, enums, field names, and gate names into natural language in reader-facing artifacts.
- Include only sections supported by the research purpose and evidence. Do not force prices, organizations, products, regulations, integrations, or any other domain field.
- Use tables only for genuinely comparable values. Put nuance below the table and never truncate prose with ellipses.
- Distinguish source assertions from independently corroborated evidence using context-neutral language such as “the source states” or “the authors report.”
- Rank or group items only against explicit criteria. State the decisive trade-off and uncertainty for each ranking.
- Preserve direct external links in `report.md` or `research-dossier.md`; the reader must not need the manifest merely to reach a source.
- Keep `report.md` useful on its own while avoiding repetition across artifacts.
- Separate established classifications or findings from items still under investigation. Keep inconclusive items visible.
- Match depth to `reporting.detail_level`: `executive`, `standard`, or `detailed`. Control length by moving item detail to the dossier, not by deleting evidence or candidates.

## Dossier rules

When generated, give every retained item a stable section containing:

1. identity and relevance to the research purpose;
2. decision-relevant or question-relevant findings;
3. material evidence and counterevidence;
4. limitations, conflicts, and missing information;
5. direct source links.

Use natural labels derived from `fields.yaml`. Do not dump raw JSON or expose internal identifiers. Keep confirmed exclusions in the audit appendix unless they materially affect the main conclusion.

## Synthesis and uncertainty rules

- Present only `full` support as established by the registered evidence.
- Qualify `partial` and `inconclusive` support.
- Never synthesize `irrelevant` or `contradicted` claims as established facts.
- Keep the report in `draft` when claims are unreviewed, but explain this once in plain language.
- Do not equate `unreviewed` with unsupported. Distinguish located evidence from semantic review.
- Keep automated or model-assisted review distinguishable from human review without naming or assuming a particular system.
- Do not hide nulls, empty values, legacy uncertainty markers, or explicit absence states. Summarize material gaps and preserve the exhaustive register in the appendix.
- Do not claim that quote matching proves truth, completeness, or semantic support.
- Put limitations that could change the answer in `report.md`, not only in supporting artifacts.

## Audit appendix order

1. Delivery status and validation gates.
2. Key questions and their dispositions.
3. Complete retained-item and incomplete-research reconciliation.
4. Explicit absence, conflict, and uncertainty states by item or theme.
5. Complete critical-claim register with review state, source, literal evidence, and recoverable location.
6. Discovery and corpus revisions relevant to the report.
7. Technical limitations.

## Completion checks

Before finishing, verify that:

- every key question has an answer or explicit open state;
- every retained item appears in the report, dossier, or incomplete-research register;
- every recommendation or major implication traces to critical claims;
- material counterevidence is visible to the intended reader;
- no section exists solely because of a domain-specific template;
- source links and audit paths resolve;
- the three artifacts do not contradict one another.
