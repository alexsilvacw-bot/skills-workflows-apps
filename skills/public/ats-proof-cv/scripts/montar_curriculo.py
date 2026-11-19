#!/usr/bin/env python3
"""Montagem local de conteúdo aprovado. Não traduz, pontua ou reescreve."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from copy import deepcopy
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
import re
import sys
import tempfile
import zipfile
from lxml import etree as ET

from avaliar_experiencias import ROOT
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ET.register_namespace('w', W)
def tag(name): return '{' + W + '}' + name

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def language(value):
    value = str(value).strip().casefold()
    if value in ('en', 'en-us', 'en-gb', 'ingles', 'inglês', 'english'): return 'en'
    if value in ('pt', 'pt-br', 'portugues', 'português', 'portuguese'): return 'pt'
    raise ValueError('Idioma sem blocos fixos cadastrados. Cadastre o idioma na configuração antes da montagem.')

def clean(text, preserve_ratios=False):
    if not isinstance(text, str): raise ValueError('Texto deve ser uma string.')
    text = text.replace(r'\(', '').replace(r'\)', '').replace(r'\%', '%')
    text = re.sub(r'\s*\|\s*', ' | ', text)
    text = text.replace('—', ', ').replace('–', '-')
    text = re.sub(r'(?<!\d):|:(?!\d)', '.', text) if preserve_ratios else text.replace(':', '.')
    return re.sub(r'\s+', ' ', text).strip()

def period_text(period, lang):
    if not period: return ''
    months = {'pt': 'jan fev mar abr mai jun jul ago set out nov dez'.split(),
              'en': 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()}
    def month(value):
        if not value: return ''
        if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', value):
            raise ValueError('Data inválida, esperado YYYY-MM.')
        year, number = value.split('-')
        return f'{months[lang][int(number)-1]} {year}'
    start = month(period.get('entrada'))
    end = ('atual' if lang == 'pt' else 'Present') if period.get('atual') else month(period.get('saida'))
    return f'{start} - {end}' if start and end else start or end

def prepare(data, config, base, approved=False, review_after=False):
    count = sum(len(e.get('ids', [e.get('id')])) for l in data.get('vinculos', []) for e in l.get('experiencias', []))
    requires_human = bool(data.get('propostas')) or count < config['matching']['selecao']['meta_minima_experiencias_no_rascunho']
    if review_after and (data.get('revisao_editorial', {}).get('modo') != 'embedding' or data.get('propostas')):
        raise ValueError('Revisão posterior exige redação embedding sem propostas separadas.')
    if requires_human and not review_after and data.get('aprovado_por_usuario') is not True and not approved:
        raise ValueError('Experiências insuficientes; complementação exige validação humana.')
    lang = language(data.get('idioma_cv'))
    for field in ('cargo_alvo', 'resumo_profissional'):
        if not clean(data.get(field, '')): raise ValueError(f'Campo obrigatório vazio: {field}')
    for field in ('competencias', 'ferramentas'):
        if not isinstance(data.get(field), list) or any(not isinstance(x, str) or not x.strip() for x in data[field]):
            raise ValueError(f'{field} deve ser uma lista de textos não vazios.')
    if not isinstance(data.get('vinculos'), list): raise ValueError('vinculos deve ser uma lista.')
    catalog = {x['id']: x for x in base['experiencias']}
    records, seen, ids, warnings = [], set(), set(), []
    for original in data['vinculos']:
        item = deepcopy(original)
        key = item.get('empresa_id')
        if key not in catalog: raise ValueError(f'empresa_id não encontrado na base: {key}')
        if key in seen: raise ValueError(f'Vínculo duplicado: {key}; reúna as experiências no mesmo objeto.')
        seen.add(key)
        source = catalog[key]
        item['empresa'] = source['empresa']
        if not clean(item.get('cargo', '')): raise ValueError(f'Cargo final obrigatório: {key}')
        if source.get('periodo'):
            if item.get('periodo') and item['periodo'] != source['periodo']:
                warnings.append(f'{source["empresa"]}: datas da base confirmada prevaleceram sobre a entrada.')
            item['periodo'] = source['periodo']
        if not item.get('periodo') or not item['periodo'].get('entrada') or (not item['periodo'].get('atual') and not item['periodo'].get('saida')):
            warnings.append(f'{source["empresa"]}: período incompleto; nenhuma data foi inventada.')
        item['periodo_texto'] = period_text(item.get('periodo'), lang)
        period = item.get('periodo') or {}
        if period.get('entrada') and period.get('saida') and period['entrada'] > period['saida']:
            warnings.append(f'{source["empresa"]}: entrada posterior à saída; confira as datas aprovadas.')
        catalog_ids = {x['id'] for x in source['experiencia']}
        if not isinstance(item.get('experiencias'), list): raise ValueError('experiencias deve ser uma lista, inclusive quando vazia.')
        for exp in item['experiencias']:
            if not isinstance(exp, dict) or not clean(exp.get('texto', '')): raise ValueError('Experiência exige texto final aprovado.')
            refs = exp.get('ids', [exp.get('id')])
            if not refs or len(refs) != len(set(refs)) or not set(refs) <= catalog_ids:
                raise ValueError('Referências de experiência não pertencem ao vínculo.')
            if set(refs) & ids: raise ValueError('Experiência duplicada entre textos finais.')
            ids.update(refs)
        records.append(item)
    if review_after:
        warnings.append('Revisão factual humana pendente; os acréscimos estão em dados-reescritos.json, revisao_editorial.')
    rules = config['montagem_curriculo']
    optional = set(config['matching']['selecao']['empresas_opcionais'])
    missing = [x['empresa'] for x in catalog.values() if x['empresa'] not in optional and x['id'] not in seen]
    if missing: raise ValueError('Inclua os vínculos obrigatórios, com experiências=[] quando resumidos: ' + ', '.join(missing))
    if len(ids) > config['matching']['selecao']['limite_experiencias']:
        warnings.append(f'{len(ids)} experiências aprovadas excedem o limite 25; conteúdo preservado para revisão, sem corte automático.')
    def sort_key(item):
        p = item.get('periodo') or {}
        first = item['empresa'] == rules['ordem_vinculos']['primeiro']
        current = p.get('atual', False)
        date = p.get('entrada') if current else p.get('saida')
        numeric = lambda value: int((value or '0000-00').replace('-', ''))
        return (not first, not current, not bool(date), -numeric(date), -numeric(p.get('entrada')), item['empresa'], item['cargo'])
    records.sort(key=sort_key)
    display = rules['apresentacao_vinculos']
    today = datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m')
    for item in records:
        period = item.get('periodo') or {}
        for date in ('entrada', 'saida'):
            if period.get(date) and period[date] > today:
                warnings.append(f'{item["empresa"]}: {date} futura; data preservada para conferência.')
        if period.get('atual'):
            label = display['rotulos_atuais'][lang]['principal' if item['empresa'] == rules['ordem_vinculos']['primeiro'] else 'simultaneo']
            item['periodo_texto'] = period_text(dict(period, atual=False, saida=None), lang) + ' - ' + label
        parts = [x.strip() for x in item['empresa'].split('|')]
        item['empresa_exibicao'] = parts[0] + (' (' + '; '.join(parts[1:]) + ')' if len(parts) > 1 else '')
    for field in ('competencias', 'ferramentas'):
        n = len(data[field])
        if field == 'competencias' and n != 10 or field == 'ferramentas' and not 5 <= n <= 10:
            warnings.append(f'{field}: quantidade {n} fora da configuração de extração; conteúdo aprovado preservado.')
    return lang, records, warnings

def build(data, config, base, output, template, approved=False, review_after=False):
    output, template = Path(output), Path(template)
    if output.resolve() == template.resolve(): raise ValueError('Saída não pode sobrescrever o template.')
    lang, records, warnings = prepare(data, config, base, approved, review_after)
    with zipfile.ZipFile(template) as archive:
        parts = {x.filename: (x, archive.read(x.filename)) for x in archive.infolist()}
    expected = config['layout'].get('template_sha256')
    if expected and hashlib.sha256(template.read_bytes()).hexdigest() != expected:
        warnings.append('Hash do template difere da configuração; confira a revisão visual antes de usar o arquivo.')
    root = ET.fromstring(parts['word/document.xml'][1])
    body = root.find(tag('body'))
    prototypes = {}
    for p in body.findall(tag('p')):
        text = ''.join(x.text or '' for x in p.iter(tag('t')))
        prototypes[text] = deepcopy(p)
    sections = [deepcopy(x) for x in body if x.tag == tag('sectPr')]
    for x in list(body): body.remove(x)
    def paragraph(marker, text, keep_next=False, label=None):
        if not text: return
        if marker not in prototypes: raise ValueError(f'Campo ausente no template: {marker}')
        p = deepcopy(prototypes[marker])
        props = p.find(tag('pPr'))
        if props is None: props = ET.Element(tag('pPr')); p.insert(0, props)
        for child in list(p):
            if child.tag != tag('pPr'): p.remove(child)
        for element in list(props):
            if element.tag in (tag('keepNext'), tag('pageBreakBefore')): props.remove(element)
        ET.SubElement(props, tag('keepNext'), {tag('val'): '1' if keep_next else '0'})
        def run(value, bold=False):
            r = ET.SubElement(p, tag('r'))
            if bold: ET.SubElement(ET.SubElement(r, tag('rPr')), tag('b'))
            t = ET.SubElement(r, tag('t')); t.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); t.text = (' ' if value.startswith(' ') else '') + clean(value, preserve_ratios=data.get('revisao_editorial', {}).get('modo') == 'embedding')
        if label: run(label + '.', True); run(' ' + text)
        else: run(text)
        body.append(p)
    fixed = config['dados_fixos'][lang]
    titles = config['ats']['universais']['formatacao']['titulos_secoes'][lang]
    def heading(key): paragraph('{{TITULO_' + key.upper() + '}}', titles[key], True)
    detailed = [x for x in records if x['experiencias'] or x['empresa'] == config['montagem_curriculo']['ordem_vinculos']['primeiro']]
    earlier = [x for x in records if x not in detailed]
    def rules_join(*values):
        return config['montagem_curriculo']['apresentacao_vinculos']['separador_cargo_datas'].join(x for x in values if x)
    def section(key):
        if key == 'identificacao_contatos_e_cargo_alvo':
            paragraph('{{NOME}}', config['dados_fixos']['nome'], True)
            paragraph('{{CARGO_ALVO}}', data['cargo_alvo'], True)
            paragraph('{{LOCALIZACAO_E_DISPONIBILIDADE}}', fixed['localizacao'], True)
            for contact in fixed['contatos'].split('|'):
                paragraph('{{CONTATOS}}', contact.strip())
        elif key == 'resumo_profissional': heading('resumo'); paragraph('{{RESUMO_PROFISSIONAL}}', data['resumo_profissional'])
        elif key == 'ia':
            paragraph('{{TITULO_IA}}', fixed['titulo_ia'], True)
            for index, (label, text) in enumerate(fixed['ia'], 1): paragraph('{{IA_ITEM_' + str(index) + '}}', text, label=label)
        elif key == 'experiencias_profissionais':
            if detailed: heading('experiencias')
            descriptions = config['montagem_curriculo']['descricoes_empresas']
            for item in detailed:
                paragraph('{{EMPRESA}}', item['empresa_exibicao'], True)
                paragraph('{{CARGO}} | {{PERIODO}}', rules_join(item['cargo'], item['periodo_texto']), bool(item['experiencias']))
                if item['experiencias']:
                    description = descriptions['textos'].get(item['empresa'], {}).get(lang, '')
                    paragraph('{{DESCRICAO_EMPRESA}}', description, True)
                for exp in item['experiencias']: paragraph('{{EXPERIENCIA}}', exp['texto'])
        elif key == 'historico_resumido':
            if earlier: heading('historico_resumido')
            for item in earlier:
                paragraph('{{EMPRESA}}', item['empresa_exibicao'], True)
                paragraph('{{CARGO}} | {{PERIODO}}', rules_join(item['cargo'], item['periodo_texto']))
        elif key in ('competencias', 'ferramentas'):
            if data[key]: heading(key); paragraph('{{' + key.upper() + '}}', config['montagem_curriculo']['apresentacao_vinculos']['separador_listas'].join(data[key]))
        elif key in ('formacao', 'idiomas'):
            heading(key)
            for i, text in enumerate(fixed[key], 1): paragraph('{{' + ('FORMACAO' if key == 'formacao' else 'IDIOMA') + '_' + str(i) + '}}', text)
        else: raise ValueError(f'Seção desconhecida na configuração: {key}')
    for key in config['montagem_curriculo']['ordem_secoes']: section(key)
    for s in sections: body.append(s)
    visible = ''.join(x.text or '' for x in root.iter(tag('t')))
    if '{{' in visible or '}}' in visible: raise ValueError('Marcador não preenchido na saída.')
    punctuation_text = (re.sub(r'(?<=\d):(?=\d)', '', visible)
                        if data.get('revisao_editorial', {}).get('modo') == 'embedding' else visible)
    if any(x in punctuation_text for x in ('—','–',':')): raise ValueError('Pontuação proibida na saída.')
    if root.findall('.//' + tag('tbl')) or root.findall('.//' + tag('txbxContent')): raise ValueError('Estrutura incompatível com layout ATS.')
    parts['word/document.xml'] = (parts['word/document.xml'][0], ET.tostring(root, encoding='utf-8', xml_declaration=True))
    core_path = 'docProps/core.xml'
    if core_path in parts:
        core = ET.fromstring(parts[core_path][1])
        title = core.find('{http://purl.org/dc/elements/1.1/}title')
        if title is not None:
            title.text = f"{config['dados_fixos']['nome']} | {data['cargo_alvo']}"
            parts[core_path] = (parts[core_path][0], ET.tostring(core, encoding='utf-8', xml_declaration=True))
    # Um espaço após o rótulo de IA é preservado sem alterar o texto aprovado.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp: temp = Path(tmp.name)
    try:
        with zipfile.ZipFile(temp,'w') as archive:
            for info, value in parts.values(): archive.writestr(info, value)
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)
    return warnings

def build_or_resume(data, config, base, output, template, approved=False, review_after=False,
                    resume=False, overwrite=False):
    """Reuse a complete, identical DOCX when only PDF conversion was interrupted."""
    output = Path(output)
    if not output.exists() or overwrite:
        return build(data, config, base, output, template, approved, review_after), False
    if not resume:
        raise ValueError('Saída já existe. Use outro nome ou --sobrescrever.')
    with tempfile.TemporaryDirectory(prefix='cv-verificar-docx-') as temp:
        expected = Path(temp)/'esperado.docx'
        warnings = build(data, config, base, expected, template, approved, review_after)
        with zipfile.ZipFile(expected) as new, zipfile.ZipFile(output) as old:
            if (new.namelist() != old.namelist()
                    or any(new.read(name) != old.read(name) for name in new.namelist())):
                raise ValueError('DOCX existente difere do conteúdo validado; retomada não sobrescreve documentos.')
    return warnings, True

def resolve_converter():
    """Usa o LibreOffice do mesmo runtime do Python, sem depender da skill."""
    python_root = Path(sys.executable).parent.parent
    if python_root.name == 'python' and python_root.parent.name == 'dependencies':
        candidate = python_root.parent / 'bin/override/soffice'
        if candidate.is_file(): return str(candidate)
        raise FileNotFoundError(f'Conversor do runtime não encontrado: {candidate}')
    candidate = shutil.which('soffice') or shutil.which('libreoffice')
    if not candidate: raise FileNotFoundError('Instale LibreOffice e disponibilize soffice ou libreoffice no PATH.')
    return candidate

def convert_pdf(docx, output, overwrite=False):
    from pypdf import PdfReader
    docx, output = Path(docx).resolve(), Path(output).resolve()
    if output.suffix.lower() != '.pdf': raise ValueError('Saída PDF deve ter extensão .pdf.')
    if output == docx: raise ValueError('O PDF não pode sobrescrever o DOCX.')
    if output.exists() and not overwrite: raise ValueError('PDF já existe. Use --sobrescrever ou outro nome.')
    converter = resolve_converter()
    before = hashlib.sha256(docx.read_bytes()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='adaptar-pdf-') as temp:
        folder = Path(temp)
        profile = folder/'profile'
        env = os.environ.copy()
        if sys.platform == 'darwin':
            env.update(TMPDIR='/private/tmp', TEMP='/private/tmp', TMP='/private/tmp')
        result = subprocess.run([
            converter, '-env:UserInstallation=' + profile.as_uri(), '--headless',
            '--invisible', '--norestore', '--convert-to', 'pdf:writer_pdf_Export',
            '--outdir', str(folder), str(docx)
        ], capture_output=True, text=True, timeout=45, env=env)
        generated = folder/(docx.stem + '.pdf')
        if not generated.is_file() or not generated.stat().st_size:
            detail = (result.stderr or result.stdout or f'exit {result.returncode}').strip()
            raise ValueError('Conversor não gerou PDF: ' + detail[:600])
        try:
            reader = PdfReader(generated)
        except Exception as error:
            raise ValueError('PDF gerado não pôde ser lido; DOCX mantido.') from error
        if not reader.pages or any(not (page.extract_text() or '').strip() for page in reader.pages):
            raise ValueError('PDF sem texto extraível em uma ou mais páginas; DOCX mantido.')
        if hashlib.sha256(docx.read_bytes()).hexdigest() != before:
            raise ValueError('O conversor alterou o DOCX; confira o arquivo antes de usar.')
        page_count = len(reader.pages)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            staged = Path(temp_pdf.name)
        try:
            shutil.copyfile(generated, staged)
            staged.replace(output)
        finally:
            staged.unlink(missing_ok=True)
    return page_count

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, required=True)
    parser.add_argument('--saida', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT/'config/configuracao.json')
    parser.add_argument('--base', type=Path, default=ROOT/'base/curriculo_base.json')
    parser.add_argument('--template', type=Path)
    parser.add_argument('--aprovado', action='store_true', help='Confirma que o candidato já revisou o conteúdo.')
    parser.add_argument('--revisao-posterior', action='store_true', help='Gera documentos embedding para revisão humana posterior, sem registrar aprovação.')
    parser.add_argument('--sobrescrever', action='store_true')
    parser.add_argument('--retomar', action='store_true', help='Reutiliza DOCX idêntico para concluir PDF interrompido.')
    parser.add_argument('--pdf', action='store_true', help='Gera também PDF com mesmo nome e pasta do DOCX, sem API.')
    args = parser.parse_args()
    try:
        if args.saida.suffix.lower() != '.docx': raise ValueError('A saída desta etapa deve ser .docx.')
        if args.saida.exists() and not (args.sobrescrever or args.retomar):
            raise ValueError('Saída já existe. Use outro nome ou --sobrescrever.')
        if args.saida.resolve() in {args.entrada.resolve(), args.config.resolve(), args.base.resolve()}:
            raise ValueError('A saída não pode sobrescrever um arquivo de entrada.')
        if args.pdf and args.saida.with_suffix('.pdf').exists() and not args.sobrescrever:
            raise ValueError('PDF já existe. Use outro nome ou --sobrescrever.')
        if not (args.entrada.parent/'experiencias-aprovadas.json').is_file():
            raise ValueError('Matching ausente; configuração de currículo exige experiencias-aprovadas.json.')
        config = load(args.config)
        config.update(load(ROOT/'config/regras_matching.json'))
        template = args.template or ROOT/config['layout']['template']
        data = load(args.entrada); base = load(args.base); job = load(args.entrada.parent/'requisitos-vaga.json')
        import avaliar_experiencias as matching
        import redigir_curriculo as writing
        if data['versao_base'] != matching.version(base) or data['versao_requisitos'] != matching.version(job):
            raise ValueError('Base ou vaga mudou após a redação; documento não gerado.')
        if data.get('revisao_editorial', {}).get('modo') == 'embedding':
            policy = load(ROOT/'config/recuperacao_embedding.json')['redacao']
            if policy.get('revisar_alinhamento_antes_documentos'):
                writing.validate_alignment_review(data, load(args.entrada.parent/'experiencias-aprovadas.json'))
            _, evidence = matching.catalog(base)
            experiences = [x for link in data['vinculos'] for x in link['experiencias']]
            selected = [eid for x in experiences for eid in x['ids']]
            writing.validate_metric_preservation(experiences, evidence, selected)
        for link in data['vinculos']:
            writing.validate_redundancy(link['experiencias'], config)
        data.update(idioma_cv=job['idioma_cv'], cargo_alvo=clean(job['nome_vaga']),
                    competencias=job['competencias'], ferramentas=job['ferramentas'])
        warnings, reused = build_or_resume(data, config, base, args.saida, template,
            args.aprovado, args.revisao_posterior, resume=args.retomar, overwrite=args.sobrescrever)
        print(f'DOCX {"reutilizado" if reused else "gerado"}: {args.saida.resolve()}')
        for warning in warnings: print('Pendência: ' + warning, file=sys.stderr)
        if args.pdf:
            try:
                pdf_path = args.saida.with_suffix('.pdf')
                pages = convert_pdf(args.saida, pdf_path, args.sobrescrever)
                print(f'PDF gerado: {pdf_path.resolve()} | {pages} páginas | texto extraível conferido')
            except (OSError, ValueError, ImportError, subprocess.TimeoutExpired) as error:
                print(f'DOCX mantido. Falha na conversão para PDF: {error}', file=sys.stderr)
                return 2
        print('Estrutura conferida. Paginação deve ser revisada visualmente; isso não comprova leitura em ATS real.')
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, ET.ParseError) as error:
        print(f'Não foi possível montar: {error}', file=sys.stderr); return 1
    return 0

if __name__ == '__main__': sys.exit(main())
