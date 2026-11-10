#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree as ET


SIMULATION_TOKENS = [
    "SIMULAÇÃO DE DESENVOLVIMENTO, NÃO ENVIAR",
    "◊",
    "contrafactual",
    "currículo aspiracional",
    "curriculo aspiracional",
]
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def required_text_file(package: Path, name: str) -> list[str]:
    target = package / name
    if not target.is_file():
        return [f"missing required file: {name}"]
    try:
        if not target.read_text(encoding="utf-8").strip():
            return [f"empty required file: {name}"]
    except OSError as exc:
        return [f"cannot read required file {name}: {exc}"]
    return []


def read_docx(path: Path) -> tuple[str, list[str], list[str]]:
    errors = []
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        return "", [], [f"invalid DOCX {path.name}: {exc}"]

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        return "", [], [f"invalid document XML in {path.name}: {exc}"]

    paragraphs = []
    list_paragraphs = []
    for paragraph in root.findall(".//w:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()
        if not text:
            continue
        paragraphs.append(text)
        style_node = paragraph.find("./w:pPr/w:pStyle", NS)
        style_value = style_node.get(f"{{{W_NS}}}val", "") if style_node is not None else ""
        if paragraph.find("./w:pPr/w:numPr", NS) is not None or style_value.casefold().startswith("list"):
            list_paragraphs.append(text)
    return "\n".join(paragraphs), list_paragraphs, errors


def validate_matrix(path: Path) -> list[str]:
    errors = required_text_file(path.parent, path.name)
    if errors:
        return errors

    text = path.read_text(encoding="utf-8")
    folded = text.casefold()
    required_terms = [
        "texto exato",
        "formulação normalizada",
        "categoria",
        "prioridade",
        "evidência",
        "fonte",
        "score",
        "ranking agregado",
    ]
    for term in required_terms:
        if term.casefold() not in folded:
            errors.append(f"requirements matrix is missing field or section: {term}")

    if not re.search(r"\bR\d{2,}\b", text):
        errors.append("requirements matrix has no requirement identifiers such as R01")
    has_explicit_score = re.search(r"\bscore\b[^\n]{0,20}\b[0-3]\b", text, re.IGNORECASE)
    has_score_table_value = re.search(r"\|\s*[0-3]\s*\|", text)
    if not has_explicit_score and not has_score_table_value:
        errors.append("requirements matrix has no explicit score from 0 to 3")
    invalid_scores = re.findall(r"\bscore\b[^\n]{0,20}\b([4-9]|\d{2,})\b", text, re.IGNORECASE)
    if invalid_scores:
        errors.append("requirements matrix contains a requirement score outside the 0 to 3 scale")
    return errors


def validate_confirmation(path: Path) -> list[str]:
    errors = required_text_file(path.parent, path.name)
    if errors:
        return errors

    text = path.read_text(encoding="utf-8")
    folded = text.casefold()
    no_zero_scores = "nenhum requisito material com score 0" in folded
    if no_zero_scores:
        return errors

    required_terms = [
        "hipótese",
        "exemplo hipotético, não confirmado e proibido no currículo até confirmação de alex",
        "pergunta",
        "resposta",
        "classificação",
        "score revisado",
    ]
    for term in required_terms:
        if term.casefold() not in folded:
            errors.append(f"confirmation record is missing field or section: {term}")
    return errors


def validate_ats_audit(path: Path) -> list[str]:
    errors = required_text_file(path.parent, path.name)
    if errors:
        return errors

    text = path.read_text(encoding="utf-8")
    folded = text.casefold()
    required_terms = [
        "veredito do ats antigo",
        "o que precisaria ser verdade",
        "frase ideal se confirmada",
        "alteração proposta",
        "estado factual",
        "ação autorizada",
        "segunda passagem",
    ]
    for term in required_terms:
        if term.casefold() not in folded:
            errors.append(f"literal ATS audit is missing field or section: {term}")

    if not re.search(r"\bATS-R\d{2,}\b", text, re.IGNORECASE):
        errors.append("literal ATS audit has no requirement identifiers such as ATS-R01")

    allowed_factual_states = [
        "confirmado e sustentado",
        "potencialmente verdadeiro, requer confirmação",
        "negado ou sem suporte confirmado",
    ]
    if not any(state in folded for state in allowed_factual_states):
        errors.append("literal ATS audit has no recognized factual state")

    allowed_actions = ["aplicar", "perguntar antes de alterar", "não inserir"]
    if not any(action in folded for action in allowed_actions):
        errors.append("literal ATS audit has no recognized authorized action")
    return errors


def validate_qa(path: Path, verified_rel: str) -> list[str]:
    if not path.is_file():
        return ["missing required file: qa-word.json"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid qa-word.json: {exc}"]

    errors = []
    if data.get("status") != "passed":
        errors.append("qa-word.json status must be passed")
    row = data.get("verified_resume")
    if not isinstance(row, dict):
        errors.append("qa-word.json is missing object: verified_resume")
        return errors
    if row.get("path") != verified_rel:
        errors.append("qa-word.json verified_resume.path does not match the required DOCX")
    if not isinstance(row.get("pages_rendered"), int) or row["pages_rendered"] < 1:
        errors.append("qa-word.json verified_resume.pages_rendered must be a positive integer")
    if row.get("all_pages_inspected") is not True:
        errors.append("qa-word.json verified_resume.all_pages_inspected must be true")
    if row.get("visual_issues") != []:
        errors.append("qa-word.json verified_resume.visual_issues must be an empty array")
    if "aspirational_resume" in data:
        errors.append("qa-word.json must not contain aspirational_resume")
    return errors


def find_forbidden_artifacts(package: Path) -> list[str]:
    errors = []
    forbidden_dir = package / "aspiracional_privado_nao_enviar"
    if forbidden_dir.exists():
        errors.append("forbidden aspirational directory exists")
    for target in package.rglob("*"):
        if target == forbidden_dir or forbidden_dir in target.parents:
            continue
        folded = target.name.casefold()
        if "aspiracional" in folded or "contrafactual" in folded:
            errors.append(f"forbidden aspirational or counterfactual artifact: {target.relative_to(package)}")
    return errors


def validate_draft_stage(package: Path, require_ats_audit: bool) -> list[str]:
    errors = []
    for name in [
        "diagnostico-da-vaga.md",
        "matriz-de-requisitos-e-evidencias.md",
        "confirmacao-de-requisitos.md",
        "rascunho-do-curriculo.md",
        "avaliacao-do-curriculo.md",
    ]:
        errors.extend(required_text_file(package, name))
    errors.extend(validate_matrix(package / "matriz-de-requisitos-e-evidencias.md"))
    errors.extend(validate_confirmation(package / "confirmacao-de-requisitos.md"))
    ats_audit = package / "auditoria-ats-literal.md"
    if require_ats_audit or ats_audit.exists():
        errors.extend(validate_ats_audit(ats_audit))

    premature = list(package.rglob("*.docx"))
    if premature:
        errors.append("draft stage must not contain DOCX files before human approval")
    for name in ["qa-word.json", "aprovacao-humana.md"]:
        if (package / name).exists():
            errors.append(f"draft stage must not contain {name} before human approval")
    return errors


def validate_final_stage(package: Path, language: str, require_ats_audit: bool) -> list[str]:
    errors = []
    for name in [
        "diagnostico-da-vaga.md",
        "matriz-de-requisitos-e-evidencias.md",
        "confirmacao-de-requisitos.md",
        "rascunho-do-curriculo.md",
        "avaliacao-do-curriculo.md",
        "aprovacao-humana.md",
    ]:
        errors.extend(required_text_file(package, name))
    errors.extend(validate_matrix(package / "matriz-de-requisitos-e-evidencias.md"))
    errors.extend(validate_confirmation(package / "confirmacao-de-requisitos.md"))
    ats_audit = package / "auditoria-ats-literal.md"
    if require_ats_audit or ats_audit.exists():
        errors.extend(validate_ats_audit(ats_audit))

    language_suffix = "PTBR" if language == "pt" else "EN"
    candidates = sorted(package.glob(f"Alex_Floriano_*_{language_suffix}.docx"))
    if len(candidates) != 1:
        errors.append(
            f"expected exactly one correctly named DOCX matching "
            f"Alex_Floriano_Cargo_Empresa_{language_suffix}.docx; found {len(candidates)}"
        )
        verified = None
        verified_name = ""
    else:
        verified = candidates[0]
        verified_name = verified.name

    if verified is not None and verified.stat().st_size == 0:
        errors.append(f"empty required DOCX: {verified_name}")
    elif verified is not None:
        verified_text, verified_bullets, docx_errors = read_docx(verified)
        errors.extend(docx_errors)
        if not verified_bullets:
            errors.append("verified DOCX has no real Word list paragraphs")
        for token in SIMULATION_TOKENS:
            if token.casefold() in verified_text.casefold():
                errors.append(f"verified resume contains forbidden simulation token: {token}")

    if verified is not None:
        errors.extend(validate_qa(package / "qa-word.json", verified_name))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an adaptar-vaga application package")
    parser.add_argument("--package", required=True)
    parser.add_argument("--language", required=True, choices=["pt", "en"])
    parser.add_argument("--stage", choices=["draft", "final"], default="final")
    parser.add_argument(
        "--require-ats-audit",
        action="store_true",
        help="Require and validate auditoria-ats-literal.md for the updated workflow",
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    package = Path(args.package).expanduser().resolve()
    errors = find_forbidden_artifacts(package)
    if args.stage == "draft":
        errors.extend(validate_draft_stage(package, args.require_ats_audit))
        scope_parts = ["draft structure", "requirements matrix"]
        if args.require_ats_audit or (package / "auditoria-ats-literal.md").exists():
            scope_parts.append("literal ATS audit")
        scope_parts.extend(["evaluator output", "pre-DOCX approval gate"])
    else:
        errors.extend(validate_final_stage(package, args.language, args.require_ats_audit))
        scope_parts = ["final package structure"]
        if args.require_ats_audit or (package / "auditoria-ats-literal.md").exists():
            scope_parts.append("literal ATS audit")
        scope_parts.extend(["DOCX structure", "human-approval record", "recorded visual QA"])
    scope = ", ".join(scope_parts)

    status = "passed" if not errors else "failed"
    result = {
        "validator_scope": scope,
        "package": str(package),
        "language": args.language,
        "stage": args.stage,
        "status": status,
        "errors": errors,
        "warning": "This validator does not verify factual truth, semantic honesty, human approval authenticity, predict actual ATS behavior, or independently repeat the visual inspection.",
    }

    if args.write:
        package.mkdir(parents=True, exist_ok=True)
        (package / "validacao-do-pacote.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
