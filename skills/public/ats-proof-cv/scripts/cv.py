#!/usr/bin/env python3
"""Executa a variante original de embeddings em uma área de trabalho privada."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parents[1]
MODELS = {
    'OPENAI_EXTRACTION_MODEL': 'gpt-6.1-sol',
    'OPENAI_MATCHING_MODEL': 'gpt-6-luna',
    'OPENAI_MODEL': 'gpt-6-luna',
    'OPENAI_EXTRACTION_REASONING_EFFORT': 'low',
    'OPENAI_MATCHING_REASONING_EFFORT': 'high',
    'OPENAI_REASONING_EFFORT': 'high',
}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, encoding='utf-8', delete=False) as tmp:
            temporary = Path(tmp.name)
            json.dump(value, tmp, ensure_ascii=False, indent=2)
            tmp.write('\n')
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_career(path, catalog):
    base = load_json(path)
    if not isinstance(base, dict) or not isinstance(base.get('nome'), str) or not base['nome'].strip():
        raise ValueError('A base precisa de um nome.')
    if not isinstance(base.get('contato', ''), str):
        raise ValueError('contato deve ser um texto.')
    links = base.get('experiencias')
    if not isinstance(links, list) or not links:
        raise ValueError('experiencias deve conter pelo menos um vínculo profissional.')
    for link in links:
        if not isinstance(link, dict) or not all(
                isinstance(link.get(field), str) and link[field].strip()
                for field in ('empresa', 'cargo')):
            raise ValueError('Preencha empresa e cargo em cada vínculo.')
        facts = link.get('experiencia')
        if not isinstance(facts, list) or not facts or any(not isinstance(row, dict) for row in facts):
            raise ValueError('Informe os relatos de cada vínculo na lista experiencia.')
        if any(isinstance(row.get('texto'), str) and len(row['texto'].encode('utf-8')) > 8191 for row in facts):
            raise ValueError('Divida textos acima de 8191 bytes em relatos completos antes de indexar.')
        period = link.get('periodo')
        if not isinstance(period, dict) or type(period.get('atual')) is not bool:
            raise ValueError('periodo deve ter entrada, saida e atual. Use null para mês desconhecido.')
        for field in ('entrada', 'saida'):
            date = period.get(field)
            if date is not None and (not isinstance(date, str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', date)):
                raise ValueError('Datas usam YYYY-MM ou null.')
        if period['atual'] and period.get('saida') is not None:
            raise ValueError('Vínculo atual deve ter saida null.')
        if period.get('entrada') and period.get('saida') and period['entrada'] > period['saida']:
            raise ValueError('A data de saída antecede a entrada em um vínculo.')
    catalog(base)
    return base


def template(path):
    from docx import Document

    document = Document()
    document.core_properties.author = ''
    for marker, style in (
        ('NOME', 'Title'), ('CARGO_ALVO', 'Subtitle'),
        ('LOCALIZACAO_E_DISPONIBILIDADE', 'Normal'), ('CONTATOS', 'Normal'),
        ('TITULO_RESUMO', 'Heading 1'), ('RESUMO_PROFISSIONAL', 'Normal'),
        ('TITULO_EXPERIENCIAS', 'Heading 1'), ('TITULO_HISTORICO_RESUMIDO', 'Heading 1'),
        ('EMPRESA', 'Heading 2'), ('CARGO}} | {{PERIODO', 'Normal'),
        ('DESCRICAO_EMPRESA', 'Normal'), ('EXPERIENCIA', 'List Bullet'),
        ('TITULO_COMPETENCIAS', 'Heading 1'), ('COMPETENCIAS', 'Normal'),
        ('TITULO_FERRAMENTAS', 'Heading 1'), ('FERRAMENTAS', 'Normal'),
    ):
        document.add_paragraph('{{' + marker + '}}', style=style)
    with tempfile.TemporaryDirectory(dir=path.parent) as folder:
        prepared = Path(folder) / path.name
        document.save(prepared)
        prepared.replace(path)


def index_base(source, workspace, matching, embedding):
    base = load_career(source, matching.catalog)
    config = load_json(PACKAGE / 'config/configuracao.json')
    rules = load_json(PACKAGE / 'config/regras_matching.json')
    settings = embedding.settings(PACKAGE / 'config/recuperacao_embedding.json')
    rules_path = workspace / 'config/regras_matching.json'
    rules_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    template(workspace / config['layout']['template'])
    saved = load_json(rules_path) if rules_path.is_file() else {}
    index = saved.get('indice_matching', {})
    if index.get('versao_base') == matching.version(base) and saved.get('matching') == rules['matching']:
        matching.validate_realizations(index, base)
    else:
        key = matching.get_key()
        model = MODELS['OPENAI_MATCHING_MODEL']
        groups = matching.build_index(base, model, key, config=rules)
        index = matching.build_realizations(base, groups, rules, model, key)

    def check_source():
        if load_json(source) != base:
            raise ValueError('A base de entrada mudou durante a preparação. Execute index novamente.')

    result = embedding.prepare(index, base, settings, os.environ.get('OPENAI_API_KEY'),
                               source_check=check_source)
    check_source()
    header = {'localizacao': '', 'contatos': base.get('contato', '')}
    config['dados_fixos'] = {'nome': base['nome'], 'pt': header, 'en': header}
    save_json(workspace / 'base/curriculo_base.json', base)
    save_json(workspace / 'config/configuracao.json', config)
    save_json(workspace / 'config/recuperacao_embedding.json', settings)
    save_json(rules_path, dict(rules, indice_matching=index))
    print(f"Base preparada em {workspace} | {result['novos_ou_alterados']} vetores novos ou alterados "
          f"| {result['reutilizados']} reutilizados.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    index = commands.add_parser('index', help='Prepara a base e os embeddings.')
    index.add_argument('--base', type=Path, required=True)
    create = commands.add_parser('create', help='Cria uma candidatura.')
    vacancy = create.add_mutually_exclusive_group(required=True)
    vacancy.add_argument('--vaga', type=Path, help='Anúncio em TXT UTF-8.')
    vacancy.add_argument('--url', help='URL pública do anúncio.')
    resume = commands.add_parser('resume', help='Continua uma candidatura interrompida.')
    resume.add_argument('--candidatura', type=Path, required=True)
    for sub in (index, create, resume):
        sub.add_argument('--workspace', type=Path, default=Path('.ats-proof-cv'),
                         help='Pasta privada da base, dos índices e das candidaturas.')
    for sub in (create, resume):
        sub.add_argument('--permitir-base-integral', action='store_true',
                         help='Autoriza avaliar toda a base se o recorte da busca já cobrir todos os textos.')
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    try:
        workspace.mkdir(mode=0o700, exist_ok=True, parents=True)
        lock = os.open(workspace / '.execucao.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Já existe uma execução nesta área de trabalho.') from None
            os.environ.update(MODELS, CV_EMBEDDING_WORKSPACE=str(workspace))
            import avaliar_experiencias as matching
            import recuperar_embeddings as embedding
            import criar_curriculo_embedding as workflow
            if args.command == 'index':
                index_base(args.base, workspace, matching, embedding)
                return 0
            if not (workspace / 'config/regras_matching.json').is_file():
                raise ValueError('Base ainda não indexada. Execute index antes de criar o currículo.')
            if args.command == 'resume':
                folder = args.candidatura.resolve()
                if folder.parent != workspace / 'candidaturas' or not (folder / 'requisitos-vaga.json').is_file():
                    raise ValueError('Informe a pasta de candidatura retornada pela execução neste workspace.')
                source = ['--candidatura', str(folder)]
            elif args.url:
                source = ['--url', args.url]
            else:
                source = ['--arquivo', str(args.vaga.resolve())]
            return workflow.main(source, allow_full_base=args.permitir_base_integral)
        finally:
            os.close(lock)
    except (ImportError, KeyError, OSError, ValueError, sqlite3.Error) as error:
        print(f'Fluxo interrompido: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
