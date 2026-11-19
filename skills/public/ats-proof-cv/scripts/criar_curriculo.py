#!/usr/bin/env python3
"""Orquestra extração, recuperação por grupos e fatos, matching granular e rascunho; Word e PDF automáticos quando há experiências suficientes."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
import extrair_vaga
import avaliar_experiencias as matching
import redigir_curriculo as writing


def document_stem(job, config):
    def component(field):
        value = job.get(field)
        if field == 'nome_empresa' and (not isinstance(value, str) or not value.strip()):
            value = config['montagem_curriculo']['nome_arquivo'].get('empresa_ausente')
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'Campo ausente para o nome do currículo: {field}.')
        value = unicodedata.normalize('NFKD', value)
        value = ''.join(char for char in value if not unicodedata.combining(char))
        value = re.sub(r'[^\w]+', '_', value).strip('_')
        if not value:
            raise ValueError(f'Campo inválido para o nome do currículo: {field}.')
        return value
    pattern = config['montagem_curriculo']['nome_arquivo']['padrao']
    stem = pattern.format(company=component('nome_empresa'), role=component('nome_vaga'))
    if not stem or stem in {'.', '..'} or '/' in stem or '\\' in stem:
        raise ValueError('Padrão de nome do currículo inválido.')
    return stem


def main(argv=None, caller_override=None, editorial_policy=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--url')
    source.add_argument('--arquivo', type=Path)
    source.add_argument('--candidatura', type=Path)
    parser.add_argument('--aprovado', action='store_true', help='Registra aprovação humana já dada.')
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args(argv)
    try:
        model = os.environ.get('OPENAI_MODEL', 'gpt-6-luna')
        extraction_model = os.environ.get('OPENAI_EXTRACTION_MODEL', 'gpt-6.1-sol')
        matching_model = os.environ.get('OPENAI_MATCHING_MODEL', model)
        caller = caller_override if caller_override is not None else matching.model_json
        key = None
        folder = args.candidatura
        if folder is None:
            if args.aprovado:
                raise ValueError('Uma nova vaga precisa de rascunho e revisão antes da aprovação.')
            key = matching.get_key()
            text = extrair_vaga.read_source(url=args.url, arquivo=args.arquivo)
            job = extrair_vaga.extract_validated(text, key, extraction_model)
            folder = extrair_vaga.save_candidatura(job, parent=matching.ROOT/'candidaturas')
        folder = Path(folder).resolve()
        print(f'Candidatura atual: {folder}', flush=True)
        diagnostics = {}
        if not (folder/'experiencias-aprovadas.json').exists():
            if args.aprovado:
                raise ValueError('Matching ausente; execute primeiro sem --aprovado.')
            key = key or matching.get_key()
            effort = os.environ.get('OPENAI_MATCHING_REASONING_EFFORT',
                                    os.environ.get('OPENAI_REASONING_EFFORT', 'medium')) if matching_model.startswith('gpt-6') else None
            label = f' com {matching_model}' + (f' (reasoning.effort={effort})' if effort else '')
            retrieval_label = getattr(caller, 'retrieval_label', 'grupos, realizações, fontes principais e detalhes necessários')
            print('Matching' + label + ': ' + retrieval_label + '; avaliação dos textos originais.', flush=True)
            matching.run(folder, matching_model, key, caller=caller, diagnostics=diagnostics)
        if not (folder/'dados-reescritos.json').exists():
            if args.aprovado:
                raise ValueError('Rascunho ausente; execute primeiro sem --aprovado.')
            key = key or matching.get_key()
            writing.run(folder, model, key, caller=caller, lacunas=diagnostics.get('lacunas'),
                        editorial_policy=editorial_policy)
        data = matching.load(folder/'dados-reescritos.json')
        selection = matching.load(folder/'experiencias-aprovadas.json')
        rules = matching.load(matching.ROOT/'config/regras_matching.json')
        requires_human = len(selection['selecionadas']) < rules['matching']['selecao']['meta_minima_experiencias_no_rascunho'] or bool(data.get('propostas'))
        review_after = bool(editorial_policy and editorial_policy.get('revisao_factual_apos_documentos'))
        if review_after and (data.get('revisao_editorial', {}).get('modo') != 'embedding' or data.get('propostas')):
            raise ValueError('Rascunho anterior incompatível com revisão posterior; não sobrescrever nem aprovar automaticamente.')
        if review_after and editorial_policy.get('revisar_alinhamento_antes_documentos'):
            writing.validate_alignment_review(data, selection)
        if requires_human and not review_after and not args.aprovado and data.get('aprovado_por_usuario') is not True:
            print(f'Rascunho para revisão: {folder / "dados-reescritos.json"}')
            print('Aguardando aprovação humana. Nenhum documento foi montado.')
            return 0
        # Propostas ficam fora dos vínculos até o candidato decidir sua inclusão no JSON.
        base = matching.load(matching.ROOT/'base/curriculo_base.json')
        recorded = data['versao_base']
        if recorded and recorded != matching.version(base):
            raise ValueError('Base mudou após o rascunho; revisar antes de montar.')
        config = matching.load(matching.ROOT/'config/configuracao.json')
        job = matching.load(folder/'requisitos-vaga.json')
        if data['versao_requisitos'] != matching.version(job):
            raise ValueError('A vaga mudou após a redação; revisar antes de montar.')
        command = [sys.executable, str(matching.SOURCE_ROOT/'scripts/montar_curriculo.py'),
                   '--entrada', str(folder/'dados-reescritos.json'),
                   '--saida', str(folder/(document_stem(job, config) + '.docx'))]
        if args.aprovado:
            command.append('--aprovado')
        if review_after:
            command.append('--revisao-posterior')
            command.append('--retomar')
            print('Revisão factual pendente: Word/PDF serão gerados para conferência humana posterior.')
        command.append('--pdf')
        return subprocess.run(command, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')).returncode
    except (ValueError, KeyError, OSError, extrair_vaga.ExtractionError) as error:
        print(f'Fluxo não concluído: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
