---
name: ats-proof-cv
description: Tailor a résumé to a job using embedding retrieval, requirement-level evidence selection, and an alignment review before PDF export. Use with an existing career file or to prepare one from the user's résumé or experience notes.
license: MIT
---

# ATS-Proof CV

Use the [English guide](README.en.md) or the [Portuguese guide](README.md) for installation, career data, and commands. Run `scripts/cv.py` from the skill folder or invoke the script by absolute path from the user's project. Keep the same `--workspace` throughout an application.

1. Obtain a UTF-8 JSON file with the user's experience. When needed, structure the résumé or notes they provide using the [career file instructions](README.en.md#add-and-index-your-experience). Preserve job titles, companies, dates, metrics, and units. Assign stable IDs to roles and individual accounts of work. If the user only asks to prepare their career file, return the JSON for review.
2. Before preparing or updating the file, explain that the experience descriptions go to OpenAI to group versions of the same work and generate vectors. Run `index --base` when the user has authorized that step. Use `OPENAI_API_KEY` from the environment. Reuse a prepared index when it matches the current file. When the user supplies or edits their data, compare it with the prepared copy at `base/curriculo_base.json` inside the workspace.
3. Run `create --url` with the public job URL or `create --vaga` with the ad in a UTF-8 text file. If the page is inaccessible, use the text supplied by the user. After an interruption, run `resume --candidatura` with the folder returned by the script. If the script stops because retrieval covered the entire career file, explain that scoring this set can send all retrieved descriptions to the API. Use `--permitir-base-integral` when the user's authorization covers that transfer.
4. Use the engine's built-in sequence. Retrieval finds candidate sources. Scoring evaluates the original text, selection resolves duplicate accounts and requirement coverage, and the selection review distinguishes direct, partial, transferable, and missing evidence. Drafting uses the coverage and positioning, preserves metrics, and runs a separate alignment review before assembly. If a step fails, retain the application folder for the resume command.
5. Inspect the PDF visually. Use `experiencias-aprovadas.json` and `dados-reescritos.json` to explain gaps and flag additions for factual review. Deliver the PDF and point to the application folder. Keep factual review pending until the user completes it.
