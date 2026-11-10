---
name: pesquisa-alex
description: Plan and route robust, structured research whose important conclusions must be traceable and reviewable. Run only when the user explicitly invokes `pesquisa-alex`; if the workflow merely appears useful, suggest it and wait for explicit authorization before loading or executing it. Use after invocation for consequential comparisons, landscapes, diagnostics, assessments, evidence syntheses, descriptive studies, or other investigations needing an intent audit, key questions, explicit evidence gaps, auditable discovery, atomic critical claims, audience-aware reporting, and a readiness gate. Do not use for simple fact lookup or lightweight research.
---

# Pesquisa Alex — planning and routing

Create a confirmed framework before deep investigation. Open-web work must first be captured in an authorized, versioned corpus; do not edit the production `research*` skills.

## Invocation policy

- Execute this workflow only after the user explicitly invokes `pesquisa-alex` by name.
- When the workflow appears appropriate but was not invoked, explain briefly why it may help and ask permission. Do not begin any phase until the user agrees.
- An explicit invocation authorizes the intent audit only. It does not waive the confirmation gate below.

## Mandatory intent audit

Perform this audit before planning, searching, creating artifacts, or routing to another phase. Read only the user's request and supplied or explicitly referenced material needed to interpret intent.

### Step 1 — State and confirm the interpretation

Present exactly four concise assertions written as what you understood, in the user's language. In Portuguese, use these forms:

1. **Objetivo:** “Seu objetivo parece ser X.”
2. **Público:** “Você parece estar fazendo isso para Y.”
3. **Resultado esperado:** “O resultado que você parece esperar é Z.”
4. **Prazo:** “Você parece esperar sucesso em W.”

Use the environment's structured-question tool, including `AskUserQuestion` when available. Turn each assertion into a question whose choices in Portuguese are exactly `correto`, `parcialmente correto`, and `errado`, allowing the user to supply a correction. In another language, use faithful equivalents. If the tool accepts fewer than four questions, ask them in consecutive batches without beginning other work. If no structured-question tool is available, present the four assertions as text and wait for the user's confirmation or corrections.

Do not infer confirmation from silence, prior approval of a different research run, or the invocation itself. Stop until the user responds.

### Step 2 — Diagnose misalignment

For every point the user marks `partially correct` or `wrong`, in this order:

1. Explain why the initial reading differed, citing the concrete phrase, slide, file element, ambiguity, or omission that caused it. Treat this as a likely communication risk for the real audience, not merely an assistant error.
2. End that point with the exact structure in the user's language. In Portuguese, use: “Se você tivesse dito/feito X, eu teria entendido corretamente.” Replace X with a concrete wording or change.

If all four points are correct, state in one line that there was no intent misalignment and continue.

Use the corrected interpretation as authoritative. Preserve both the initial reading and the confirmed corrections in `outline.yaml` so later phases do not silently reinterpret the request.

## Required shared contract

Resolve and read `references/contract.md` relative to this `SKILL.md` before creating or editing research artifacts. It is the single definition of key questions, critical claims, evidence, review states, absence states, and delivery gates.

## Workflow

1. Read applicable `AGENTS.md` files and nearby project context.
2. Confirm that the request warrants robust structured research. For a simple question, recommend ordinary research instead.
3. Propose:
   - research objects;
   - field categories and definitions;
   - key questions that determine whether the purpose has been answered;
   - reporting audience, primary use, mode, detail level, and dossier preference.
4. Ask only questions whose answers materially change scope, evidence, or output.
5. Ask the user to confirm the objects, fields, and decisive questions. This is separate from the mandatory intent-audit confirmation.
6. Create `outline.yaml` and `fields.yaml` after confirmation.
7. Determine the source mode:
   - for an existing corpus, confirm its authorized path;
   - for open-web research, set `authorized_corpus: pending_discovery` and route to `pesquisa-alex-discover`.
   Treat proposed objects and prior knowledge as candidate seeds, never as evidence. Do not discard a plausible seed merely because evidence has not yet been acquired.
8. Immediately before deep research, after initial discovery when required, ask where the deep phase will run. Use a structured-question tool when available; otherwise ask in text and wait. Offer:
   - `current_environment`: run deep research in the environment conducting strategy;
   - `external_executor`: hand deep research to another language-model environment, application, CLI, or API.
   In the user-facing question, name the detected current surface when helpful—for example, “aqui no ChatGPT” versus “outro ambiente ou LLM”—without hard-coding that provider into the stored workflow. Do not assume that strategy and deep execution use the same system. Record the answer under `execution_handoff` in `outline.yaml`.
9. If the confirmed destination is Codex CLI, explicitly ask the user which Codex model must execute the research. Do not infer a model, select a default, or continue from silence. Record the user's answer under `execution_handoff.model` in `outline.yaml` and stop until it is confirmed.
10. When the user selects `external_executor`, resolve and read `references/external-handoff.md` completely. Create and validate the required handoff package, give the user direct links to every required file plus a ready-to-paste execution instruction, and stop. Do not begin deep research in the current environment.
11. Confirm `batch_size` only when it matters operationally; default to `3`. Set `output_dir` to `./results` unless the user specifies otherwise.
12. Show the absolute paths and direct the user to the appropriate follow-up skill.

## Output schemas

`outline.yaml`:

```yaml
topic: Research topic
workflow: pesquisa-alex
research_purpose: What the reader needs to understand, assess, explain, or decide
decision_context: Optional decision this research informs
intent_audit:
  status: confirmed
  initial_interpretation:
    objective: Initial interpretation
    audience: Initial interpretation
    expected_outcome: Initial interpretation
    time_horizon: Initial interpretation
  confirmed_interpretation:
    objective: Confirmed objective
    audience: Confirmed audience
    expected_outcome: Confirmed outcome
    time_horizon: Confirmed time horizon
  misalignments:
    - point: objective
      initial_reading: What was initially understood
      correction: What the user corrected
      cause: Concrete material element that caused the initial reading
      counterfactual: What wording or change would have made the intent clear
execution_handoff:
  status: pending
  mode: null
  executor: null
  surface: null
  model: null
  package_path: null
decision_questions:
  - question_id: Q01
    question_text: Decisive question
items: []
authorized_corpus: ./corpus
source_manifest: null
corpus_revision: 0
reporting:
  audience: Intended reader
  primary_use: Intended use of the report
  report_mode: auto
  detail_level: standard
  item_dossier: auto
execution:
  batch_size: 3
  output_dir: ./results
```

`fields.yaml`:

```yaml
field_categories:
  - category: Basic Info
    description: Core identification fields
    fields:
      - name: name
        description: Item name
        detail_level: brief
        required: true
```

Use `brief`, `moderate`, or `detailed` for field `detail_level`. For reporting, use `executive`, `standard`, or `detailed`; use `report_mode: auto` unless the user confirms a specific mode. Use `required: true` only when absence must fail structural validation; never require plausible invented content.

## Follow-up skills

- `pesquisa-alex-discover`: discover candidates and maintain an authorized versioned corpus.
- `pesquisa-alex-add-items`: extend objects.
- `pesquisa-alex-add-fields`: refine fields.
- `pesquisa-alex-deep`: produce evidence-backed results.
- `pesquisa-alex-report`: publish answers, gaps, evidence, and delivery status.
