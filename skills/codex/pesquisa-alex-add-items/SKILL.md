---
name: pesquisa-alex-add-items
description: Add, correct, or refresh research objects in a Pesquisa Alex outline.yaml without weakening its evidence contract. Use only within an explicitly authorized Pesquisa Alex run or when the user explicitly invokes `pesquisa-alex-add-items`; otherwise suggest Pesquisa Alex and wait for authorization.
---

# Add Pesquisa Alex items

1. Locate the relevant `outline.yaml` under the current project. If more than one exists, ask which one to use.
2. Read applicable `AGENTS.md` files, the selected outline, and `references/contract.md` relative to this `SKILL.md`.
3. Ask which items the user already wants to add and whether current web research should supplement them.
4. If requested, search current authoritative sources and cite the evidence supporting additions.
5. Present a deduplicated proposed list.
6. When the outline uses a discovery corpus, resolve and read `references/discover-SKILL.md`, register additions through a new discovery iteration, acquire available evidence, update the manifest and corpus revision, and revalidate with `scripts/validate_discovery.py` before changing the outline.
7. Add direct, adjacent, and inconclusive candidates after user confirmation; do not require complete evidence merely to retain a plausible object for deep verification.
8. Preserve unrelated fields and formatting as closely as practical.
