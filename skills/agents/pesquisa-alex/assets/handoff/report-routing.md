# Report routing

Choose a mode from the research purpose and key-question verbs. Do not infer mode from the subject area alone. Combine modes when necessary.

| Mode | Use when key questions ask | Organizing unit | Typical synthesis |
|---|---|---|---|
| `choice` | which option, whether to proceed, what to prioritize | explicit criteria and options | trade-offs, conditions, recommendation when warranted |
| `landscape` | what exists, how the space is structured, what is missing | categories, relationships, coverage | map of the space, clusters, gaps, exceptions |
| `diagnostic` | why something happened, what explains an outcome | hypotheses and observations | support, counterevidence, alternative explanations |
| `evidence_synthesis` | what the evidence collectively shows | themes, findings, source quality | agreement, disagreement, strength, unresolved questions |
| `assessment` | how an item or situation performs against requirements | criteria, thresholds, risks | conformance, maturity, strengths, limitations |
| `descriptive` | what is known about a subject without an immediate decision | key questions and themes | factual account, patterns, boundaries, unknowns |
| `custom` | the confirmed purpose does not fit the modes above | user-defined | structure explicitly tied to confirmed questions |

## Routing rules

1. Use `choice` only when the purpose requires a selection, prioritization, or action decision.
2. Use `landscape` for coverage and structure; do not force ranking.
3. Use `diagnostic` only when causal or explanatory questions exist; distinguish association from causation.
4. Use `evidence_synthesis` when source agreement, disagreement, or quality is itself central.
5. Use `assessment` when explicit criteria or thresholds exist; do not invent a scoring model.
6. Use `descriptive` when a clear answer is needed without recommendation.
7. Use `custom` rather than distorting the research to fit another mode.

## Dossier routing

Set `item_dossier: true` when item-level detail is itself a deliverable. Set it to `false` when the research is thematic and item profiles would add repetition. In `auto`, generate the dossier when any of these are true:

- four or more retained items have moderate or detailed fields;
- item-level evidence or uncertainty would be materially lost in a compact table;
- the reader is likely to revisit individual items independently;
- the main report would otherwise require repetitive profiles.

The dossier is a depth layer, not a second executive report.
