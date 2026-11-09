---
name: pesquisa-alex-add-fields
description: Add or refine field definitions in a Pesquisa Alex fields.yaml without weakening its critical-claim evidence contract. Use only within an explicitly authorized Pesquisa Alex run or when the user explicitly invokes `pesquisa-alex-add-fields`; otherwise suggest Pesquisa Alex and wait for authorization.
---

# Add Pesquisa Alex fields

1. Locate the relevant `fields.yaml` under the current project. If more than one exists, ask which one to use.
2. Read applicable `AGENTS.md` files, the selected fields file, its paired `outline.yaml` when present, and `references/contract.md` relative to this `SKILL.md`.
3. Ask whether fields come from direct user input, web research, or both.
4. Present deduplicated fields with category, description, and `detail_level` (`brief`, `moderate`, or `detailed`).
5. Update `fields.yaml` only after user confirmation.
6. Preserve unrelated fields and formatting as closely as practical.
