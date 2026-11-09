# External execution handoff

Use this procedure when strategy and initial discovery are completed in one environment and deep research will run in another. Keep the package provider-neutral. Include reporting only when the user also delegates it.

## Confirm the destination

Ask only for details that affect delivery: the destination environment or surface, whether it can access the same filesystem, and whether it supports files, code execution, web access, and resumable work. Do not require a particular provider or interface. When the confirmed surface is Claude CLI, explicitly ask the user which Claude model must be used. Do not infer or default the model, and do not build the ready package until the answer is recorded in `outline.execution_handoff.model`.

## Build the package

Create `handoff/` beside the confirmed `outline.yaml`. Snapshot the exact approved state; do not substitute regenerated content.

Include the following bundled files from `assets/handoff/`:

- `outline.yaml` and `fields.yaml`;
- `contract.md`;
- `deep-SKILL.md` plus `discover-SKILL.md` so the deep executor can perform logged evidence enrichment;
- `report-SKILL.md` and `report-routing.md` only when reporting is also delegated;
- `validate_research.py` and `validate_discovery.py` as the validators required by those phases;
- `EXECUTE.md` containing the phase order, inputs, working-directory rules, validation commands, stop conditions, expected outputs, and a ready-to-paste instruction for the external executor;
- `handoff-manifest.json` listing every packaged file, its SHA-256 hash, its role, the confirmed executor, surface and model when applicable, creation time, and `deep` as the first pending phase.

When discovery is already complete, also provide the source manifest, discovery validation summary, candidate register, and corpus access instructions. Include the corpus itself or an unambiguous accessible path. Never mark a handoff ready if the external executor cannot access the authorized evidence.

Do not create a deep handoff while initial discovery is still pending. Complete the discovery handoff gate first. The deep executor may run later discovery enrichment, but must not start against `pending_discovery` or an unvalidated corpus.

## Write the execution instruction

Make the instruction self-contained and provider-neutral. It must tell the recipient to:

1. read `EXECUTE.md`, `outline.yaml`, `fields.yaml`, `contract.md`, and the first pending phase instructions completely;
2. preserve the confirmed intent audit and scope;
3. use only the authorized corpus for deep claims, enriching it through the recorded discovery process when material evidence is missing;
4. retain direct, adjacent, and inconclusive objects without a convenience cap;
5. run the supplied validators and preserve partial results for resume;
6. return the required artifacts and validation summaries without silently changing the framework.

Do not rely on slash commands, tool names, model names, or paths that exist only in the planning environment. Add surface-specific operational guidance only as a clearly labeled adapter section in `EXECUTE.md`. A Claude CLI adapter must state the user-confirmed model and instruct the executor to use it; never replace that choice with a default model.

## Deliver and stop

Verify that every manifest path exists and every hash matches. For Claude CLI, also verify that the confirmed model appears consistently in the outline, manifest, and surface-specific adapter. Update `outline.execution_handoff` with `status: ready`, destination details, model when applicable, package path, manifest path, and `first_pending_phase: deep`. Give the user direct file links and the ready-to-paste instruction. Stop the current workflow until the external executor's outputs are returned or the user explicitly changes the execution choice.
