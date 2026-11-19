#!/usr/bin/env python3
"""Recuperação large local e avaliação concorrente da variante embedding."""
import array
import functools
from collections import Counter, deque
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import avaliar_experiencias as matching
import matching_embedding as structured

API_URL = 'https://api.openai.com/v1/embeddings'
CONFIG_PATH = matching.ROOT / 'config/recuperacao_embedding.json'
STOPWORDS = set('a ao aos as o os de da das do dos e em na nas no nos para por com um uma '
                'the a an of and or in on to for with from at is be as by their that this '
                'experiencia experience profissional professional responsabilidade responsible '
                'capacidade ability conhecimento knowledge manage management lead leadership '
                'build own coordinate open develop development implement execute use including '
                'translate rebuild operar assumir vender gerenciar gestao liderar desenvolver '
                'implementar executar usar incluindo'.split())


def settings(path=CONFIG_PATH):
    config = matching.load(path)
    if config.get('modelo') != 'text-embedding-3-large' or config.get('dimensoes') != 3072:
        raise ValueError('Esta variante exige text-embedding-3-large com 3072 dimensões.')
    if (type(config.get('lotes_avaliacao_simultaneos')) is not int
            or config['lotes_avaliacao_simultaneos'] not in (1, 2)):
        raise ValueError('Avaliação embedding aceita um ou dois lotes simultâneos.')
    for field in ('lote_api', 'timeout_segundos', 'realizacoes_semanticas_por_requisito',
                  'realizacoes_lexicais_por_requisito', 'realizacoes_componentes_por_requisito',
                  'versoes_semanticas_por_realizacao',
                  ):
        if type(config.get(field)) is not int or config[field] < 1:
            raise ValueError('Configuração embedding inválida: ' + field)
    if config['lote_api'] > 32:
        raise ValueError('Lote embedding excede o limite conservador de 32 textos.')
    if (type(config.get('lote_fundamentacao')) is not int
            or not 1 <= config['lote_fundamentacao'] <= matching.BATCH_SIZE):
        raise ValueError('Lote de fundamentação inválido.')
    if type(config.get('correcoes_maximas_fundamento')) is not int or config['correcoes_maximas_fundamento'] not in (1, 2):
        raise ValueError('Limite de correções de fundamento inválido.')
    for field in ('peso_relevancia_mmr', 'pontuacao_minima_mmr', 'similaridade_maxima_complementar_mmr',
                  'peso_cobertura_fatos_mmr', 'peso_detalhes_mmr'):
        if type(config.get(field)) not in (int, float) or not 0 < config[field] < 1:
            raise ValueError('Parâmetro MMR inválido: ' + field)
    if type(config.get('evidencias_por_requisito_mmr')) is not int or config['evidencias_por_requisito_mmr'] not in (1, 2):
        raise ValueError('Cobertura MMR inválida.')
    for field in ('peso_fonte_principal', 'margem_minima_versao_semantica',
                  'fracao_similaridade_minima_componente'):
        if type(config.get(field)) not in (int, float) or not 0 <= config[field] <= 1:
            raise ValueError('Configuração embedding inválida: ' + field)
    focal_limit = config.get('redacao', {}).get('correcoes_focais_maximas', 1)
    if type(focal_limit) is not int or focal_limit != 1:
        raise ValueError('Limite de correções focais inválido.')
    technical_limit = config.get('redacao', {}).get('correcoes_tecnicas_maximas', 2)
    if type(technical_limit) is not int or not 0 <= technical_limit <= 2:
        raise ValueError('Limite de correções técnicas inválido.')
    target = Path(config.get('arquivo_indice', ''))
    if not str(target) or target.is_absolute() or '..' in target.parts or target.suffix != '.sqlite3':
        raise ValueError('Caminho relativo do índice embedding inválido.')
    return config


def normalize(vector, dimensions):
    if not isinstance(vector, (list, tuple, array.array)) or len(vector) != dimensions:
        raise ValueError('Dimensão do vetor embedding inválida.')
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in vector):
        raise ValueError('Vetor embedding não numérico ou não finito.')
    norm = math.sqrt(sum(x * x for x in vector))
    if not math.isfinite(norm) or norm == 0:
        raise ValueError('Vetor embedding sem norma válida.')
    return [x / norm for x in vector]


def embed(texts, key, config, telemetry=None):
    """API sem truncamento/retry silencioso; índices da resposta são validados."""
    if not texts:
        return []
    if not key:
        raise ValueError('Configure a chave no aplicativo existente.')
    # Cada byte UTF-8 é um limite superior conservador de tokens byte-level.
    # 32 * 8191 também fica abaixo do limite agregado de 300 mil tokens.
    if any(not isinstance(t, str) or not t.strip() or len(t.encode('utf-8')) > 8191 for t in texts):
        raise ValueError('Texto embedding vazio ou acima do limite conservador de 8191 bytes; nenhum corte realizado.')
    if len(texts) > config['lote_api']:
        raise ValueError('Lote embedding maior que o configurado.')
    request = Request(API_URL, data=json.dumps({'model': config['modelo'],
        'dimensions': config['dimensoes'], 'encoding_format': 'float', 'input': texts}).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=config['timeout_segundos']) as response:
            # Vetores em float JSON ultrapassam o limite do leitor de respostas textuais.
            raw = response.read(16_000_001)
            if len(raw) > 16_000_000:
                raise ValueError('Resposta embedding acima do limite de bytes.')
            result = json.loads(raw)
    except HTTPError as error:
        raise ValueError(f'Embeddings: HTTP {error.code}; lote não salvo.') from None
    except (URLError, TimeoutError, ConnectionError) as error:
        raise ValueError(f'Embeddings: falha de conexão ({type(getattr(error, "reason", error)).__name__}); lote não salvo.') from None
    if result.get('model') != config['modelo']:
        raise ValueError('Modelo retornado não corresponde ao embedding solicitado.')
    records = result.get('data', [])
    if (not isinstance(records, list) or len(records) != len(texts)
            or any(not isinstance(r, dict) or type(r.get('index')) is not int for r in records)
            or {r['index'] for r in records} != set(range(len(texts)))):
        raise ValueError('Resposta embedding omitiu, duplicou ou substituiu índices.')
    vectors = [normalize(record['embedding'], config['dimensoes'])
               for record in sorted(records, key=lambda r: r['index'])]
    if telemetry is not None:
        telemetry({'etapa': 'embedding', 'segundos': time.perf_counter() - started,
                   'textos': len(texts), 'usage': result.get('usage', {})})
    return vectors


def fingerprint(index, base, config):
    return matching.version({'base': matching.version(base), 'indice': matching.version(index),
                             'modelo': config['modelo'], 'dimensoes': config['dimensoes']})


def text_key(item, config):
    return matching.version({'id': item['id'], 'texto': item['texto'],
                             'modelo': config['modelo'], 'dimensoes': config['dimensoes']})


def connect(path, create=False):
    path = Path(path)
    if create:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            if os.fstat(fd).st_uid != os.getuid():
                raise ValueError('Índice embedding não pertence ao usuário.')
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)
    if not path.is_file() or path.is_symlink() or path.stat().st_uid != os.getuid():
        raise ValueError('Índice embedding ausente ou inseguro; prepare o índice explicitamente.')
    db = sqlite3.connect(path.as_uri() + ('?mode=rw' if create else '?mode=ro'), uri=True)
    if create:
        db.execute('CREATE TABLE IF NOT EXISTS vetores (id TEXT PRIMARY KEY, chave TEXT NOT NULL, vetor BLOB NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS metadados (id TEXT PRIMARY KEY, valor TEXT NOT NULL)')
        db.commit()
    return db


def prepare(index, base, config, key, path=None, embedder=embed, telemetry=None, source_check=None):
    matching.validate_realizations(index, base)
    _, items = matching.catalog(base)
    path = Path(path or matching.ROOT / config['arquivo_indice']).absolute()
    # Validar todos antes de enviar o primeiro lote; não cortar evidências.
    if any(len(item['texto'].encode('utf-8')) > 8191 for item in items.values()):
        raise ValueError('Base contém texto acima de 8191 bytes; indexação não iniciada.')
    db = connect(path, create=True)
    try:
        existing = dict(db.execute('SELECT id, chave FROM vetores'))
        invalid = set()
        for eid, blob in db.execute('SELECT id, vetor FROM vetores'):
            try:
                vector = array.array('f')
                vector.frombytes(blob)
                normalize(vector, config['dimensoes'])
            except (ValueError, TypeError):
                invalid.add(eid)
        pending = [item for item in items.values()
                   if item['id'] in invalid or existing.get(item['id']) != text_key(item, config)]
        # Uma preparação interrompida nunca fica marcada como pronta.
        db.execute('DELETE FROM metadados WHERE id="pronto"')
        db.commit()
        for start in range(0, len(pending), config['lote_api']):
            batch = pending[start:start + config['lote_api']]
            vectors = embedder([x['texto'] for x in batch], key, config, telemetry)
            if len(vectors) != len(batch):
                raise ValueError('Quantidade de vetores incompatível com o lote.')
            rows = [(item['id'], text_key(item, config),
                     array.array('f', normalize(vector, config['dimensoes'])).tobytes())
                    for item, vector in zip(batch, vectors)]
            db.executemany('INSERT OR REPLACE INTO vetores VALUES (?, ?, ?)', rows)
            db.commit()
            print(f'Índice embedding: {min(start + len(batch), len(pending))}/{len(pending)} textos novos/alterados.',
                  file=sys.stderr, flush=True)
        if source_check is not None:
            source_check()
        db.executemany('DELETE FROM vetores WHERE id=?', [(eid,) for eid in existing if eid not in items])
        db.execute('INSERT OR REPLACE INTO metadados VALUES ("pronto", ?)',
                   (fingerprint(index, base, config),))
        db.commit()
        return {'total': len(items), 'novos_ou_alterados': len(pending), 'reutilizados': len(items) - len(pending)}
    finally:
        db.close()


def read_vectors(index, base, config, path):
    db = connect(Path(path).absolute())
    try:
        row = db.execute('SELECT valor FROM metadados WHERE id="pronto"').fetchone()
        if row is None or row[0] != fingerprint(index, base, config):
            raise ValueError('Índice embedding incompleto ou desatualizado; prepare explicitamente.')
        _, items = matching.catalog(base)
        vectors = {}
        for eid, key, blob in db.execute('SELECT id, chave, vetor FROM vetores'):
            if eid not in items or key != text_key(items[eid], config):
                raise ValueError('IDs/textos incompatíveis no índice embedding.')
            vector = array.array('f')
            vector.frombytes(blob)
            vectors[eid] = normalize(vector, config['dimensoes'])
        if set(vectors) != set(items):
            raise ValueError('Índice embedding não cobre todos os IDs da base.')
        return vectors
    except sqlite3.Error:
        raise ValueError('Índice embedding inválido; prepare explicitamente.') from None
    finally:
        db.close()


def tokens(text):
    return set(re.findall(r'[a-z0-9]+', matching.normalized(text))) - STOPWORDS


def identifiers(text):
    """Pistas literais: siglas, nomes próprios e números; nunca confirmam aderência."""
    words = re.findall(r'\b[\w&.-]+\b', text)
    selected = [word for word in words if any(c.isdigit() for c in word)
                or (len(word) > 1 and word.isupper())
                or word[0].isupper()
                or any(c.isupper() for c in word[1:])]
    return tokens(' '.join(selected))


def similarities(vectors, queries):
    """Produto escalar exato de vetores normalizados; NumPy opcional, sem instalação."""
    ids = list(vectors)
    try:
        import numpy as np
    except ImportError:
        return [{eid: sum(a * b for a, b in zip(query, vectors[eid])) for eid in ids} for query in queries]
    matrix = np.asarray([vectors[eid] for eid in ids], dtype=np.float32)
    scores = np.asarray(queries, dtype=np.float32) @ matrix.T
    return [dict(zip(ids, map(float, row))) for row in scores]


class EmbeddingCaller:
    """Recuperação local e avaliação concorrente optativas; demais etapas delegadas."""
    def __init__(self, config=None, path=None, embedder=embed, telemetry=None, delegate=matching.model_json,
                 *, allow_full_base=False):
        self.config = config if config is not None else settings()
        self.path = Path(path or matching.ROOT / self.config['arquivo_indice']).absolute()
        self.embedder, self.telemetry, self.delegate = embedder, telemetry, delegate
        self.backend = 'api-embedding:' + matching.version({'config': self.config, 'indice': str(self.path)})
        self.retrieval_label = 'text-embedding-3-large, busca local por requisito, fontes principais e detalhes'
        self.query_cache = {}
        self.origens_recuperacao = {}
        self.allow_full_base = allow_full_base

    def __call__(self, *args, **kwargs):
        return self.delegate(*args, **kwargs)

    def assess(self, items, reqs, config, model, key, caller=matching.model_json):
        return self._assess(items, reqs, config, model, key, caller,
                            matching.assessment_request, matching.assessment_records)

    def deduplicate(self, items, config, model, key, caller=matching.model_json):
        return structured.deduplicate(items, config, model, key, caller)

    def select(self, base, job, config, assessments, families, universo_ids=None):
        vectors = read_vectors(config['indice_matching'], base, self.config, self.path)
        self.selection_allowed = structured.eligible_sources(base, job, config, assessments, families, universo_ids)
        return structured.select(base, job, config, assessments, families, universo_ids,
                                 vectors=vectors, settings=self.config,
                                 query_vector=self.query_cache.get(structured.role_query(matching.requirements(job, config))))

    def registrar_recuperacao(self, folder, selection):
        """Observação local após seleção; não participa de prompts ou critérios."""
        started = time.perf_counter()
        selected = set(selection['selecionadas'])
        def summarize(ids):
            counts = {'somente_semantica': 0, 'somente_lexical': 0,
                      'somente_componentes': 0, 'multiplas_buscas': 0,
                      'fora_topk_semantico': 0, 'sem_origem': 0}
            for eid in ids:
                paths = {name for origin in self.origens_recuperacao.get(eid, [])
                         for name in origin['buscas']}
                if not paths:
                    counts['sem_origem'] += 1
                    continue
                if 'semantica' not in paths:
                    counts['fora_topk_semantico'] += 1
                category = ('somente_' + next(iter(paths))) if len(paths) == 1 else 'multiplas_buscas'
                counts[category] += 1
            return dict(total=len(ids), **counts)
        report = {
            'versao_registro': 1,
            'versao_base': selection['versao_base'],
            'versao_requisitos': selection['versao_requisitos'],
            'configuracao_recuperacao': self.config,
            'recuperadas': summarize(set(self.origens_recuperacao)),
            'selecionadas': summarize(selected),
            'experiencias': {eid: {'selecionada': eid in selected, 'origens': origins}
                             for eid, origins in sorted(self.origens_recuperacao.items())},
            'interpretacao': 'As buscas indicam a origem da realização que trouxe a fonte. '
                'Fora do top K significa ausência na busca semântica de todos os requisitos. '
                'Não equivale a executar seleção sem buscas extras nem mede economia de API.',
        }
        report['segundos_montagem_registro'] = time.perf_counter() - started
        target = Path(folder) / 'origens-recuperacao.json'
        if target.exists():
            previous = matching.load(target)
            comparable = lambda value: {k: v for k, v in value.items() if k != 'segundos_montagem_registro'}
            if comparable(previous) != comparable(report):
                raise ValueError('Registro de origens existente incompatível; não sobrescrever.')
        else:
            matching.save(target, report)
        summary = report['selecionadas']
        print(f"Origens da seleção: {summary}; registro em origens-recuperacao.json.", file=sys.stderr)

    def fundamentar(self, items, reqs, config, assessments, selection, model, key, caller):
        if self.config.get('redacao', {}).get('revisar_alinhamento_antes_documentos'):
            if not hasattr(self, 'selection_allowed'):
                raise ValueError('Universo elegível da seleção embedding ausente para revisão.')
            structured.review_selection(items, reqs,
                dict(config, correcoes_maximas_fundamento=self.config['correcoes_maximas_fundamento']),
                assessments, selection, self.selection_allowed, model, key, caller)
            print('Fundamentação integrada à cobertura da seleção; sem segunda avaliação das mesmas fontes.',
                  file=sys.stderr, flush=True)
            return selection['cobertura_componentes']
        selected = {eid: items[eid] for eid in selection['selecionadas']}
        if not selected:
            return {}
        # Campos obrigatórios são derivados das notas fixas, não de outra decisão do modelo.
        records = self._assess(selected, reqs, config, model, key, caller,
            functools.partial(structured.explanation_request, assessments=assessments),
            functools.partial(structured.explanation_records, assessments=assessments),
            maximum=self.config['lote_fundamentacao'],
            max_repairs=self.config['correcoes_maximas_fundamento'], allow_repairs=True)
        for eid, record in records.items():
            print(f"Fundamentação {eid}: {len(record['fundamentos'])} relações; notas preservadas.", file=sys.stderr)
            for reason in record['fundamentos']:
                if re.search(r'discut[ií]vel|question[aá]vel|debatable|questionable', reason['justificativa'], re.I):
                    print(f"Ressalva de matching {eid}/{reason['requisito_id']}: "
                          + reason['justificativa'], file=sys.stderr)
        return records

    def _assess(self, items, reqs, config, model, key, caller=matching.model_json,
                request_builder=matching.assessment_request, records_parser=matching.assessment_records,
                maximum=matching.BATCH_SIZE, max_repairs=1, allow_repairs=False):
        workers = self.config['lotes_avaliacao_simultaneos']
        if type(workers) is not int or workers not in (1, 2):
            raise ValueError('Avaliação embedding aceita um ou dois lotes simultâneos.')
        if workers == 1 and request_builder is matching.assessment_request:
            return matching.assess(items, reqs, config, model, key, caller)
        values = list(items.values())
        pending = deque((start, values[start:start + maximum])
                        for start in range(0, len(values), maximum))
        repairs = Counter()
        active, output, failure = {}, {}, None
        checkpoint = getattr(caller, 'checkpoint', None)
        delegate = getattr(caller, 'delegate', caller) if checkpoint is not None else caller
        repair_enabled = allow_repairs or records_parser is structured.assessment_records
        feedback_slot = ('feedback_' + request_builder(values[:1], reqs, config, model, key)[3]
                         if repair_enabled and values else None)
        feedback = (checkpoint.get(feedback_slot) or {}) if checkpoint is not None and feedback_slot else {}
        repairs.update({eid: entry['tentativas'] for eid, entry in feedback.items()})
        def build(batch):
            request = list(request_builder(batch, reqs, config, model, key))
            errors = {item['id']: feedback[item['id']]['erro'] for item in batch if item['id'] in feedback}
            if errors:
                request[0] = dict(request[0], feedback_validacao=errors)
                request[1] += (' Corrija os erros apontados em feedback_validacao. Retorne a resposta completa '
                    'para os IDs recebidos, mantendo fonte integral, requisitos e escala. '
                    'Toda nota elegível precisa de fundamento; não contradiga as categorias do mesmo componente.')
            return tuple(request)
        if checkpoint is not None:
            # Falhas concorrentes têm chave própria; close(failed=True) não deve
            # remover a última resposta válida de outro lote já concluído.
            checkpoint.last = None
        print(f'Avaliação embedding: até {workers} lotes simultâneos; prompts e critérios vigentes.',
              file=sys.stderr, flush=True)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            while pending or active:
                while pending and len(active) < workers and failure is None:
                    start, batch = pending.popleft()
                    request = build(batch)
                    token = matching.ResumeResponses.response_key(*request[:5])
                    cached = checkpoint.get(token) if checkpoint is not None else None
                    # O lote completo tem precedência sobre caches de itens de
                    # correções; filtrar antes mudaria a chave e repetiria a API.
                    if checkpoint is not None and cached is None:
                        missing = []
                        for item in batch:
                            one = build([item])
                            saved = checkpoint.get(matching.ResumeResponses.response_key(*one[:5]))
                            if saved is None:
                                missing.append(item)
                            else:
                                output.update(records_parser(saved, [item], reqs))
                        batch = missing
                        if not batch:
                            continue
                        request = build(batch)
                        token = matching.ResumeResponses.response_key(*request[:5])
                        cached = checkpoint.get(token)
                    print(f'Matching {start + 1}-{start + len(batch)} de {len(values)} | concorrente',
                          file=sys.stderr, flush=True)
                    if cached is None:
                        if any(repairs[item['id']] > max_repairs for item in batch):
                            failure = ValueError('Limite de correções de fundamento esgotado; nenhuma chamada adicional.')
                            pending.clear()
                            break
                        future = executor.submit(delegate, *request)
                    else:
                        future = Future()
                        future.set_result(cached)
                        print('Retomada: resposta validada reutilizada (matching); sem nova chamada de IA.',
                              file=sys.stderr, flush=True)
                    active[future] = (start, batch, token)
                if not active:
                    continue
                done, _ = wait(active, return_when=FIRST_COMPLETED)
                for future in sorted(done, key=lambda f: active[f][0]):
                    start, batch, token = active.pop(future)
                    try:
                        response = future.result()
                        matching.validate_assessment_ids(
                            [{'id': eid} for eid in response.get('avaliacoes', {})], batch)
                        try:
                            records = records_parser(response, batch, reqs)
                        except ValueError:
                            if records_parser is not structured.assessment_records and not allow_repairs:
                                raise
                            # Preservar itens válidos e corrigir só os inválidos,
                            # até o limite, com todos os requisitos e fonte integral.
                            records = {}
                            for offset, item in enumerate(batch):
                                eid = item['id']
                                single = {'avaliacoes': {eid: response.get('avaliacoes', {}).get(eid)}}
                                try:
                                    good = records_parser(single, [item], reqs)
                                except (ValueError, TypeError, KeyError) as error:
                                    repairs[eid] += 1
                                    feedback[eid] = {'tentativas': repairs[eid], 'erro': str(error)}
                                    if checkpoint is not None:
                                        checkpoint.put(feedback_slot, feedback)
                                    if repairs[eid] > max_repairs:
                                        raise ValueError(f'Fundamento inválido após correção: {eid}: {error}') from None
                                    pending.appendleft((start + offset, [item]))
                                    print(f'Correção de fundamento: {eid}; fonte e requisitos integrais.', file=sys.stderr)
                                else:
                                    records.update(good)
                                    if checkpoint is not None:
                                        one = build([item])
                                        checkpoint.put(matching.ResumeResponses.response_key(*one[:5]), single)
                            output.update(records)
                            continue
                        if checkpoint is not None:
                            checkpoint.put(token, response)
                        output.update(records)
                    except matching.extrair_vaga.TokenBudgetError as error:
                        if len(batch) == 1:
                            failure = failure or matching.extrair_vaga.TokenBudgetError(
                                f'{error} Mesmo um lote de um item com seu contexto integral não cabe. '
                                'Etapa interrompida sem cortar textos, requisitos ou famílias.')
                        elif failure is None:
                            half = max(1, len(batch) // 2)
                            pending.appendleft((start + half, batch[half:]))
                            pending.appendleft((start, batch[:half]))
                            print(f'Ajuste automático: lote de {len(batch)} para {half} itens '
                                  'por limite de tokens; fontes e requisitos integrais.', file=sys.stderr)
                    except Exception as error:
                        if checkpoint is not None:
                            checkpoint.discard(token)
                        failure = failure or error
                if failure is not None:
                    # Não iniciar novos pedidos. Drenar apenas os já em execução,
                    # validando e salvando seus sucessos antes de propagar a falha.
                    pending.clear()
        if failure is not None:
            raise failure
        matching.validate_assessment_ids(list(output.values()), values)
        return {eid: output[eid] for eid in items}

    def retrieve(self, index, base, reqs, model, key, caller=None):
        started = time.perf_counter()
        matching.validate_realizations(index, base)
        _, items = matching.catalog(base)
        vectors = read_vectors(index, base, self.config, self.path)
        config = self.config
        queries = [r['texto'] for r in reqs]
        aggregate = structured.role_query(reqs)
        long_aggregate = len(aggregate.encode('utf-8')) > 8191
        if reqs and not long_aggregate:
            queries.append(aggregate)
        missing = list(dict.fromkeys(text for text in queries if text not in self.query_cache))
        for start in range(0, len(missing), config['lote_api']):
            batch = missing[start:start + config['lote_api']]
            encoded = self.embedder(batch, key, config, self.telemetry)
            if len(encoded) != len(batch):
                raise ValueError('Embeddings de requisitos incompletos.')
            self.query_cache.update({text: normalize(vector, config['dimensoes'])
                                     for text, vector in zip(batch, encoded)})
        if reqs and long_aggregate:
            # Equal-weight mean of complete requirement vectors, with no extra API call.
            self.query_cache[aggregate] = normalize([
                sum(self.query_cache[r['texto']][i] for r in reqs) / len(reqs)
                for i in range(config['dimensoes'])], config['dimensoes'])
        scores = similarities(vectors, [self.query_cache[r['texto']] for r in reqs]) if reqs else []
        doc_tokens = {eid: tokens(item['texto']) for eid, item in items.items()}
        counts = Counter(t for terms in doc_tokens.values() for t in terms)
        traces, requirements, recovered = {}, {}, set()
        self.origens_recuperacao = {}
        for req, semantic in zip(reqs, scores):
            query_terms = tokens(req['texto'])
            lexical = {eid: sum(math.log(1 + len(items) / counts[t]) for t in terms & query_terms)
                       for eid, terms in doc_tokens.items()}
            records = index['realizacoes']
            best = lambda record, values: max(values[eid] for eid in record['experiencias_ids'])
            # Uma versão composta pode pertencer a várias realizações. O peso da
            # fonte principal evita atribuir a todas elas o assunto daquela versão.
            weight = config['peso_fonte_principal']
            rank_score = lambda record: (weight * semantic[record['evidencia_resumo_id']]
                                         + (1 - weight) * best(record, semantic))
            semantic_rank = sorted(records, key=lambda r: (-rank_score(r), r['id']))
            lexical_rank = sorted((r for r in records if best(r, lexical) > 0),
                                  key=lambda r: (-best(r, lexical), r['id']))
            chosen = {r['id']: r for r in semantic_rank[:config['realizacoes_semanticas_por_requisito']]}
            chosen.update({r['id']: r for r in lexical_rank[:config['realizacoes_lexicais_por_requisito']]})
            component_floor = max(semantic.values()) * config['fracao_similaridade_minima_componente']
            component_rank = sorted((r for r in records if r.get('componentes') and
                max(semantic[c['evidencia_id']] for c in r['componentes']) >= component_floor),
                key=lambda r: (-max(semantic[c['evidencia_id']] for c in r['componentes']), r['id']))
            chosen.update({r['id']: r for r in component_rank[:config['realizacoes_componentes_por_requisito']]})
            ranks = {
                'semantica': {r['id']: i + 1 for i, r in enumerate(semantic_rank[:config['realizacoes_semanticas_por_requisito']])},
                'lexical': {r['id']: i + 1 for i, r in enumerate(lexical_rank[:config['realizacoes_lexicais_por_requisito']])},
                'componentes': {r['id']: i + 1 for i, r in enumerate(component_rank[:config['realizacoes_componentes_por_requisito']])},
            }
            traces[req['id']] = []
            groups = set()
            for record in chosen.values():
                refs = record['experiencias_ids']
                primary = record['evidencia_resumo_id']
                selected = {primary}
                additions = [eid for eid in refs if eid != primary and semantic[eid] >=
                             semantic[primary] + config['margem_minima_versao_semantica']]
                selected.update(sorted(additions, key=lambda eid: (-semantic[eid], eid))[:config['versoes_semanticas_por_realizacao']])
                # Siglas e nomes explícitos podem exigir mais de uma fonte. A
                # cobertura mínima usa o resolvedor vigente, sem cortar por top-k.
                detail_queries = [{'conceito': term, 'termos': [term]} for term in sorted(identifiers(req['texto']))
                                  if any(term in doc_tokens[eid] for eid in refs)]
                detail_sources, _ = matching.retrieve_versions(record, items, detail_queries)
                selected.update(detail_sources)
                # Componentes com fontes literais verificadas têm proteção própria,
                # além do único slot de versão semântica da realização.
                for component in record.get('componentes', []):
                    eid = component['evidencia_id']
                    novel = (tokens(component['nome']) | tokens(component['trecho_original'])) & query_terms - doc_tokens[primary]
                    if ((novel and semantic[eid] >= component_floor)
                            or semantic[eid] >= semantic[primary] + config['margem_minima_versao_semantica']):
                        selected.add(eid)
                for eid in sorted(selected):
                    self.origens_recuperacao.setdefault(eid, []).append({
                        'requisito_id': req['id'], 'realizacao_id': record['id'],
                        'papel_fonte': 'principal' if eid == primary else 'versao_adicional',
                        'buscas': {name: rank[record['id']] for name, rank in ranks.items()
                                   if record['id'] in rank},
                    })
                recovered.update(selected)
                groups.update(record['grupos_ids'])
                traces[req['id']].append({'realizacao_id': record['id'], 'evidencia_principal_id': primary,
                    'versoes_adicionais': [{'evidencia_id': eid,
                        'pistas_cobertas': sorted(query_terms & doc_tokens[eid])} for eid in sorted(selected - {primary})],
                    'pistas_nao_encontradas': [], 'pistas_detalhes_avaliadas': False,
                    'metodo': 'embedding_e_busca_lexical',
                    'similaridade_maxima': best(record, semantic)})
                print(f'Recuperação embedding {req["id"]} | realização {record["id"]} | '
                      f'principal {primary} | adicionais: {", ".join(sorted(selected - {primary})) or "nenhuma"}',
                      file=sys.stderr)
            requirements[req['id']] = {'grupos_ids': sorted(groups), 'busca_ampla': False}
        if recovered == set(items) and not self.allow_full_base:
            raise ValueError('Recuperação embedding integral; revisar os limites sem avaliar toda a base.')
        candidates = {eid: item for eid, item in items.items() if eid in recovered}
        gaps = [dict(r, nota=1) for r in reqs if not traces[r['id']]]
        metrics = {'etapa': 'recuperacao_embedding', 'segundos': time.perf_counter() - started,
                   'requisitos': len(reqs), 'total_base': len(items), 'total_recuperadas': len(candidates),
                   'chamadas_triagem_llm': 0}
        if self.telemetry:
            self.telemetry(metrics)
        print(f'Recuperação embedding: {len(candidates)}/{len(items)} textos; '
              f'{len(reqs)} requisitos; {metrics["segundos"]:.3f}s; nenhuma chamada LLM de triagem.',
              file=sys.stderr, flush=True)
        return candidates, dict(metrics, requisitos=requirements, realizacoes=traces, lacunas=gaps,
            busca_ampla=False, referencias_identicas_deduplicadas={})
