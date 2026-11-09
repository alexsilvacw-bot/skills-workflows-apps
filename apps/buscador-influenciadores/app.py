"""Busca pessoal de candidatos do Instagram. Python 3.11+, sem dependências."""
import csv
from collections import Counter
import html
import io
import json
import os
import queue
import re
import sqlite3
import threading
import time
import unicodedata
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from collector import collect_instagram, discover_sources, profile_handle, publication_url, collect_publication
from filtering import CATEGORY_TERMS, STATES, enrich, filter_options, matches, rejection_reasons, REJECTION_GROUPS
import web_search
import google_browser
from search_service import start_local, stop_local

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('AGGEO_INFLUENCERS_DB', ROOT / 'data/profiles.sqlite3'))
STATUSES = ('A revisar', 'Em avaliação', 'Selecionado', 'Descartado')
KINDS = ('Não classificado', 'Criador', 'Empresa', 'Escola / concorrente', 'Instituição')
JOBS = {}
GOOGLE_WORKERS = {}
JOB_LOCK = threading.Lock()
COLLECTION_LOCK = threading.Lock()
LAST_WEB_REQUEST = 0.0
RESERVED = {'p', 'reel', 'reels', 'stories', 'explore', 'accounts', 'direct', 'about', 'legal', 'developer', 'web', 'share', 'tv'}


def today():
    return datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()


def fold(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))


def handle_from(value):
    return profile_handle(value)


def safe_url(value):
    value = str(value).strip()
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Informe uma URL de fonte http ou https válida.')
    return value[:2000]


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def connect():
    con = sqlite3.connect(DB, factory=ClosingConnection)
    con.row_factory = sqlite3.Row
    return con


def initialize():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.execute('CREATE TABLE IF NOT EXISTS profiles (handle TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        con.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)')
        con.execute('CREATE TABLE IF NOT EXISTS searches (query TEXT PRIMARY KEY, created_at TEXT, payload TEXT)')
        con.execute('CREATE TABLE IF NOT EXISTS search_jobs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        for row in con.execute('SELECT id,payload FROM search_jobs').fetchall():
            job=json.loads(row[1])
            if job.get('state') in ('running','needs_attention'):
                job.update(state='interrupted',message='A Vio foi reiniciada. Resultados anteriores foram preservados; inicie outra execução.')
                con.execute('UPDATE search_jobs SET payload=? WHERE id=?',(json.dumps(job,ensure_ascii=False),row[0]))
        if not con.execute("SELECT 1 FROM metadata WHERE key='seeded'").fetchone():
            for record in json.loads((ROOT / 'seeds.json').read_text()):
                save_profile(record, con)
            con.execute("INSERT INTO metadata VALUES ('seeded', '1')")


def save_profile(data, con=None):
    if not isinstance(data, dict):
        raise ValueError('Perfil precisa ser um objeto JSON.')
    handle = handle_from(data.get('handle', ''))
    owned = con is None
    con = con or connect()
    try:
        row = con.execute('SELECT payload FROM profiles WHERE handle=?', (handle,)).fetchone()
        current = json.loads(row[0]) if row else {}
        result = {**current, 'handle': handle}
        for field in ('name', 'description', 'tags', 'location', 'kind', 'source_url', 'source_type', 'observed_at', 'notes', 'status',
                      'bio', 'public_name', 'followers_display', 'followers_precision', 'profile_fetch_status',
                      'profile_fetch_error', 'profile_data_source', 'profile_collected_at', 'profile_attempted_at',
                      'categories', 'posts_fetch_status', 'posts_attempted_at'):
            if field in data:
                if not isinstance(data[field], str):
                    raise ValueError(f'O campo {field} precisa ser texto.')
                result[field] = data[field].strip()[:5000]
        if any(c.strip() not in CATEGORY_TERMS for c in result.get('categories', '').split(',') if c.strip()):
            raise ValueError('Use as categorias genéricas disponíveis, separadas por vírgula.')
        if 'posts' in data:
            if not isinstance(data['posts'], list) or len(data['posts']) > 20:
                raise ValueError('Informe uma lista de até 20 publicações por perfil.')
            posts = []
            for post in data['posts']:
                if not isinstance(post, dict) or not isinstance(post.get('text'), str):
                    raise ValueError('Cada publicação deve ter texto e URL de origem.')
                url = safe_url(post.get('source_url', ''))
                parsed = urlsplit(url)
                if parsed.hostname not in ('www.instagram.com', 'instagram.com') or not re.fullmatch(r'/(?:p|reel)/[A-Za-z0-9_-]+/?', parsed.path):
                    raise ValueError('A origem da publicação deve ser uma URL de post ou reel do Instagram.')
                if handle_from(post.get('author_handle', handle)) != handle:
                    raise ValueError('O autor da publicação deve corresponder ao perfil.')
                posts.append({'text': post['text'][:10000], 'source_url': url, 'author_handle': handle,
                              'source_type': str(post.get('source_type', 'Conteúdo importado; autoria a revisar'))[:300],
                              'collected_at': str(post.get('collected_at', datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()))[:80]})
            result['posts'] = posts
        if 'followers_count' in data:
            count = data['followers_count']
            if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 0):
                raise ValueError('Seguidores deve ser um inteiro positivo ou nulo.')
            result['followers_count'] = count
        if result.get('profile_data_source'):
            result['profile_data_source'] = safe_url(result['profile_data_source'])
        for field, default in {'name': handle, 'description': '', 'tags': '', 'location': '', 'kind': 'Não classificado', 'source_type': 'Inserção manual', 'notes': '', 'status': 'A revisar', 'observed_at': today()}.items():
            result.setdefault(field, default)
        result['source_url'] = safe_url(result.get('source_url', ''))
        if result['status'] not in STATUSES or result['kind'] not in KINDS:
            raise ValueError('Situação ou categoria inválida.')
        try:
            observed = datetime.strptime(result['observed_at'], '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('A data da fonte deve usar AAAA-MM-DD.')
        if observed.isoformat() > today():
            raise ValueError('A data da fonte não pode ser futura.')
        favorite = data.get('favorite', current.get('favorite', False))
        if not isinstance(favorite, bool):
            raise ValueError('Favorito precisa ser verdadeiro ou falso.')
        result['favorite'] = favorite
        saved = data.get('saved', current.get('saved', bool(favorite or result.get('status') == 'Selecionado')))
        if not isinstance(saved, bool):
            raise ValueError('Salvo precisa ser verdadeiro ou falso.')
        result['saved'] = saved
        result['updated_at'] = datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()
        con.execute('INSERT INTO profiles VALUES (?, ?) ON CONFLICT(handle) DO UPDATE SET payload=excluded.payload', (handle, json.dumps(result, ensure_ascii=False)))
        if owned:
            con.commit()
        return result
    finally:
        if owned:
            con.close()


def profiles(query='', tag='', status='', favorites=False, **options):
    with connect() as con:
        items = [json.loads(r[0]) for r in con.execute('SELECT payload FROM profiles')]
    terms = fold(query).split()
    options_saved = options.pop('saved_only', False)
    options = filter_options(options)
    found = []
    for item in items:
        item = enrich(item)
        if options_saved and not item.get('saved', item.get('favorite') or item.get('status') == 'Selecionado'):
            continue
        text = fold(' '.join(item.get(f, '') for f in ('handle', 'name', 'description', 'tags', 'location', 'bio')))
        if terms and not all(t in text for t in terms):
            continue
        if tag and fold(tag) not in [fold(t.strip()) for t in item['tags'].split(',')]:
            continue
        if status and item['status'] != status or favorites and not item['favorite']:
            continue
        if not matches(item, options):
            continue
        found.append(item)
    return sorted(found, key=lambda p: fold(p['name']))


def search_plan(topic, criteria=None):
    topic = str(topic).strip()
    if not 2 <= len(topic) <= 180:
        raise ValueError('Use um tema de 2 a 180 caracteres.')
    if criteria is not None and not isinstance(criteria, dict):
        raise ValueError('Os critérios da busca devem ser um objeto.')
    options = filter_options(criteria or {})
    quote = lambda value: '"' + str(value).replace('"', '').replace('\n', ' ').strip() + '"'
    terms = [topic]
    if options['category'] and options['category'] != 'Não identificada':
        terms.append(options['category'])
    keywords = [quote(t.strip()) for t in options['keywords'].split(',') if t.strip()]
    if keywords:
        terms.append(('(' + ' OR '.join(keywords) + ')') if options['match'] == 'any' else ' '.join(keywords))
    terms.extend(quote('#' + h.lstrip('#')) for h in re.split(r'[,\s]+', options['hashtags']) if h)
    subject = ' '.join(terms)
    subjects = [subject]
    if keywords and options['match'] == 'any':
        # Várias portas de entrada: cada termo é uma alternativa real de descoberta.
        # O mercado é conferido nas evidências, sem exigir topic AND categoria em toda consulta.
        subjects = list(dict.fromkeys([subject, topic] + [term + ' ' + (options['category'] if options['category'] != 'Não identificada' else '') for term in keywords]))[:9]
        if options['hashtags']:
            subjects = [value + ' ' + ' '.join(quote('#'+h.lstrip('#')) for h in re.split(r'[,\s]+', options['hashtags']) if h) for value in subjects]
    regions = [options['region']] if options['region'] else ['']
    if options['region'] and options['include_unknown_region']:
        regions.append('')
    profile_queries = ['site:instagram.com ' + value.strip() + (' ' + quote(region) if region else '') +
               ' -inurl:/p/ -inurl:/reel/ -inurl:/explore/' for value in subjects for region in regions]
    content_subjects = [subject] if options['match']=='all' else list(dict.fromkeys([topic] + keywords))[:5]
    if options['hashtags']:
        tag_terms=' '.join(quote('#'+h.lstrip('#')) for h in re.split(r'[,\s]+', options['hashtags']) if h)
        content_subjects=[value+' '+tag_terms for value in content_subjects]
    publication_queries = ['site:instagram.com/' + kind + '/ ' + value + (' ' + quote(options['region']) if options['region'] and not options['include_unknown_region'] else '')
                           for value in content_subjects for kind in ('reel','p')]
    # Alterna portas de entrada sem perder posts, nem exigir tema e categoria em cada legenda.
    queries = []
    if options['scope'] in ('posts','bio_posts','hashtags'):
        for index in range(max(len(publication_queries),len(profile_queries))):
            if index<len(publication_queries): queries.append(publication_queries[index])
            if index<len(profile_queries): queries.append(profile_queries[index])
    else:
        queries = profile_queries + publication_queries
    queries = list(dict.fromkeys(queries))[:16]
    google_terms = ([ ' '.join(keywords) ] if keywords and options['match']=='all' else keywords) or [quote(t.strip()) for t in topic.split(',') if t.strip()]
    google_terms=list(dict.fromkeys(google_terms+[quote(topic)]))[:9]
    google_queries=[]
    tags=' '.join(quote('#'+h.lstrip('#')) for h in re.split(r'[,\s]+',options['hashtags']) if h)
    category_terms=CATEGORY_TERMS.get(options['category'],[])
    market='('+' OR '.join(quote(term) for term in category_terms[:7])+')' if category_terms else ''
    # Distribui o orçamento entre termos antes de acrescentar variações.
    # O limite não pode consumir todas as consultas só nos primeiros termos.
    for prefix in ('site:instagram.com', 'site:instagram.com/reel/', 'site:instagram.com/p/'):
        for region in regions:
            for term in google_terms:
                value=' '.join(value for value in (prefix,term,market,tags,quote(region) if region else '') if value)
                google_queries.append(value)
    google_queries=list(dict.fromkeys(google_queries))[:16]
    if not keywords and not tags and market:
        google_queries=[' '.join(value for value in ('site:instagram.com',market,quote(region) if region else '') if value) for region in regions]
    return {'topic': topic, 'criteria': options, 'queries': queries,
            'source_terms': [subject + (' ' + region if region else '') for region in regions],
            'max_profiles': 100, 'pages_per_query': 2, 'google_pages_per_query':10, 'google_max_profiles':1000, 'publication_queries':publication_queries, 'google_queries':google_queries,
            'google_links':[{'query':q,'url':'https://www.google.com/search?'+urlencode({'q':q})} for q in publication_queries],
            'verification': 'Seguidores, região, tipo de perfil e correspondência na bio/publicações são conferidos nos dados acessíveis dos candidatos encontrados. Conteúdo ausente não comprova correspondência.'}


def discover(topic, query=None):
    topic = str(topic).strip()
    if not 2 <= len(topic) <= 180:
        raise ValueError('Use entre 2 e 180 caracteres na busca.')
    key = os.environ.get('BRAVE_SEARCH_API_KEY', '')
    if not key:
        raise ValueError('Descoberta automática não configurada. Configure BRAVE_SEARCH_API_KEY no servidor ou use a busca assistida e adicione os perfis encontrados.')
    query = query or f'site:instagram.com {topic} -inurl:/p/ -inurl:/reel/ -inurl:/reels/ -inurl:/explore/'
    # Cache diário: repetir a mesma busca não faz outra chamada ao fornecedor.
    with connect() as con:
        row = con.execute('SELECT payload FROM searches WHERE query=? AND created_at=?', (query, today())).fetchone()
    if row:
        return {'items': json.loads(row[0]), 'cached': True, 'query': query}
    params = urlencode({'q': query, 'count': 20, 'country': 'BR', 'search_lang': 'pt-br'})
    req = Request('https://api.search.brave.com/res/v1/web/search?' + params,
                  headers={'X-Subscription-Token': key, 'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=20) as response:
            raw = json.load(response)
    except HTTPError as error:
        raise ValueError(f'O provedor retornou HTTP {error.code}. Confira a chave, o plano e os limites de uso.') from None
    except (URLError, TimeoutError, json.JSONDecodeError):
        raise ValueError('Não foi possível consultar o provedor. Tente novamente mais tarde.') from None
    items, seen = [], set()
    for hit in raw.get('web', {}).get('results', []):
        try:
            handle = handle_from(hit.get('url', ''))
        except ValueError:
            continue
        if handle in seen:
            continue
        seen.add(handle)
        items.append({'handle': handle, 'name': html.unescape(hit.get('title', handle)),
                      'description': re.sub('<[^>]*>', '', html.unescape(hit.get('description', ''))),
                      'tags': '', 'source_url': hit['url'], 'source_type': 'Trecho de resultado do Brave Search; não verificado no Instagram',
                      'observed_at': today(), 'notes': 'Descoberto pela consulta: ' + topic})
    with connect() as con:
        con.execute('INSERT INTO searches VALUES (?, ?, ?) ON CONFLICT(query) DO UPDATE SET created_at=excluded.created_at, payload=excluded.payload', (query, today(), json.dumps(items, ensure_ascii=False)))
    return {'items': items, 'cached': False, 'query': query}


def get_job(job_id):
    with JOB_LOCK:
        if job_id in JOBS:
            return json.loads(json.dumps(JOBS[job_id]))
    with connect() as con:
        row=con.execute('SELECT payload FROM search_jobs WHERE id=?',(job_id,)).fetchone()
    if row:
        return json.loads(row[0])
    raise ValueError('Busca não encontrada. Inicie uma nova busca.')


def update_job(job_id, **values):
    with JOB_LOCK:
        JOBS[job_id].update(values)
        snapshot=json.dumps(JOBS[job_id],ensure_ascii=False)
    with connect() as con:
        con.execute('INSERT INTO search_jobs VALUES (?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',(job_id,snapshot))


def merge_candidates(candidates, incoming):
    by_handle = {p['handle']:p for p in candidates}
    for candidate in incoming:
        existing = by_handle.get(candidate['handle'])
        if existing is None:
            candidates.append(candidate)
            by_handle[candidate['handle']] = candidate
        elif candidate.get('posts'):
            posts = {post['source_url']:post for post in existing.get('posts', []) + candidate['posts']}
            existing['posts'] = list(posts.values())[:20]
            existing['source_url'] = candidate['source_url']
            existing['source_type'] = candidate['source_type']


def paced_web_search(query, page):
    """Cadência conservadora e pausa persistente após limite, sem contornar desafios."""
    global LAST_WEB_REQUEST
    with connect() as con:
        row = con.execute("SELECT value FROM metadata WHERE key='web_cooldown_until'").fetchone()
    until = float(row[0]) if row else 0
    if time.time() < until:
        when = datetime.fromtimestamp(until, ZoneInfo('America/Sao_Paulo')).strftime('%H:%M:%S')
        return {'items':[], 'engines':[], 'raw_count':0,
                'errors':[['buscador', 'too many requests — pausa preventiva até '+when]]}
    delay = min(3,max(0,3 - (time.monotonic() - LAST_WEB_REQUEST)))
    if delay > 0:
        time.sleep(delay)
    result = web_search.search(query, page)
    LAST_WEB_REQUEST = time.monotonic()
    if any('too many requests' in str(error).lower() for error in result['errors']):
        with connect() as con:
            con.execute("INSERT INTO metadata VALUES ('web_cooldown_until',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(time.time()+180),))
    return result


def collect_candidate(candidate):
    handle=candidate['handle']
    with connect() as con:
        row=con.execute('SELECT payload FROM profiles WHERE handle=?',(handle,)).fetchone()
    record=json.loads(row[0]) if row else save_profile({**candidate,'observed_at':today()})
    data=candidate.get('profile_data')
    cached=data is None and record.get('profile_collected_at','')[:10]==today() and record.get('profile_fetch_status') in ('Coletado','Parcial')
    if not cached:
        data=dict(data) if data is not None else collect_instagram(handle)
        if data.get('public_name') and record['name']==handle:
            data['name']=data['public_name']
        if data.get('profile_fetch_status') in ('Coletado','Parcial'):
            data['profile_fetch_error']=''
        if 'posts' in data:
            data['posts']=list({post['source_url']:post for post in record.get('posts',[])+data['posts']}.values())[:20]
        record=save_profile({'handle':handle,**data})
    if candidate.get('posts'):
        merged={post['source_url']:post for post in record.get('posts',[])+candidate['posts']}
        record=save_profile({'handle':handle,'posts':list(merged.values())[:20],'posts_fetch_status':'Publicações de autoria identificada disponíveis'})
    return enrich(record),cached


def google_summary(records,options):
    items,rejections,counts=[],[],Counter()
    for record in records.values():
        reasons=rejection_reasons(record,options)
        if reasons:
            counts.update(reasons)
            rejections.append({'handle':record['handle'],'reasons':reasons})
        else:
            items.append(record)
    return {'items':items,'found':len(records),'done':len(records),'total':len(records),
            'rejected':len(rejections),'rejections':rejections,'rejection_counts':dict(counts),
            'collected':sum(bool(p.get('bio')) and p.get('followers_count') is not None for p in records.values()),
            'unavailable':sum(p.get('profile_fetch_status')=='Indisponível' for p in records.values())}


def run_google_collection(job_id,plan):
    update_job(job_id,message='Iniciando o navegador automático da Vio…')
    process=google_browser.start({'queries':plan.get('google_queries',plan['queries']), 'pages_per_query':plan.get('google_pages_per_query',10),'max_profiles':plan.get('google_max_profiles',1000)})
    with JOB_LOCK:
        GOOGLE_WORKERS[job_id]=process
    records,sources,errors={},[],[]
    completed=False
    events=queue.Queue()
    def read_events():
        try:
            for line in process.stdout:
                events.put(line)
        finally:
            events.put(None)
    threading.Thread(target=read_events,daemon=True).start()
    last_event=time.monotonic()
    try:
        while True:
            try:
                line=events.get(timeout=1)
            except queue.Empty:
                state=get_job(job_id)['state']
                if state!='needs_attention' and time.monotonic()-last_event>90:
                    raise ValueError('O navegador deixou de responder. A busca foi interrompida; resultados coletados foram preservados.')
                continue
            if line is None:
                break
            last_event=time.monotonic()
            event=json.loads(line)
            kind=event.get('event')
            if kind=='status':
                update_job(job_id,state='running',message=event['message'],attention_url='')
            elif kind=='attention':
                update_job(job_id,state='needs_attention',message=event['message'],attention_url=event.get('url',''))
            elif kind=='source':
                sources.append({k:v for k,v in event.items() if k!='event'})
                update_job(job_id,sources=sources)
            elif kind=='candidate':
                candidate=event['candidate']
                record,_=collect_candidate(candidate)
                records[record['handle']]=record
                update_job(job_id,**google_summary(records,plan['criteria']))
            elif kind=='unavailable':
                errors.append({'url':event.get('url'),'reason':event['message']})
                update_job(job_id,collection_errors=errors)
            elif kind=='complete':
                completed=True
                summary=google_summary(records,plan['criteria'])
                message='Busca automática no Google concluída.' if records else 'O Google não retornou perfis coletáveis nestas consultas. Confira consultas e eventuais avisos.'
                update_job(job_id,state='done',message=message,partial=bool(errors or event.get('unsearched_queries') or event.get('unsearched_pages')),collection_errors=errors,executed_pages=event.get('pages'),planned_pages=event.get('planned_pages'),unsearched_pages=event.get('unsearched_pages',0),executed_queries=event.get('queries'),planned_queries=event.get('planned_queries'),unsearched_queries=event.get('unsearched_queries',0),**summary)
            elif kind=='cancelled':
                completed=True
                update_job(job_id,state='cancelled',message=event['message'],partial=True)
            elif kind=='error':
                completed=True
                update_job(job_id,state='error',message='Navegador Google: '+event['message'],partial=True)
        process.wait(timeout=10)
        if not completed:
            update_job(job_id,state='error',message='O navegador foi encerrado antes de concluir a busca. Dados coletados foram preservados.',partial=True)
    finally:
        if process.poll() is None:
            try:
                google_browser.command(process,'cancel')
                process.wait(timeout=5)
            except Exception:
                process.terminate()
        if process.stdin:process.stdin.close()
        if process.stdout:process.stdout.close()
        with JOB_LOCK:
            GOOGLE_WORKERS.pop(job_id,None)


def control_google_job(job_id,action):
    with JOB_LOCK:
        process=GOOGLE_WORKERS.get(job_id)
    if process is None:
        raise ValueError('Esta execução não tem navegador ativo.')
    google_browser.command(process,action)
    return {'ok':True,'action':action}


def run_collection(job_id, topic, mode, provider, criteria=None, links=None):
    try:
        plan = search_plan(topic, criteria)
        options = plan['criteria']
        if provider=='google' and mode=='sources':
            run_google_collection(job_id,plan)
            return
        update_job(job_id, plan=plan, message='Consultando fontes com os critérios desta busca…')
        candidates, sources = [], []
        if mode == 'links':
            for link in links or []:
                update_job(job_id,message='Identificando autor de publicação fornecida…')
                try:
                    if link['type']=='publication':
                        candidate=collect_publication(link['url'])
                    else:
                        handle=handle_from(link['url'])
                        candidate={'handle':handle,'name':handle,'source_url':link['url'],'source_type':'Link de perfil fornecido pelo usuário'}
                    merge_candidates(candidates,[candidate])
                    sources.append({'source':'Link público fornecido','query':link['url'],'found':1,'status':'Autoria/perfil identificado'})
                except (ValueError, URLError, TimeoutError, OSError) as error:
                    sources.append({'source':'Publicação Instagram','query':link['url'],'found':0,'status':'Não identificada','errors':[['Instagram',str(error)[:250]]]})
                update_job(job_id,sources=sources,found=len(candidates))
        elif mode == 'sources':
            known = set()
            if provider == 'searxng':
                exhausted, stop_queries = set(), False
                for page in (1, 2):
                    for query in plan['queries']:
                        if query in exhausted:
                            continue
                        update_job(job_id, message=f'Buscando na web · consulta {plan["queries"].index(query)+1}, página {page}…')
                        key = 'searxng:v1:' + web_search.base_url() + ':' + str(page) + ':' + query
                        with connect() as con:
                            row = con.execute('SELECT payload FROM searches WHERE query=? AND created_at=?', (key, today())).fetchone()
                        cached = bool(row)
                        extra = json.loads(row[0]) if row else paced_web_search(query, page)
                        if not cached and extra['items']:
                            with connect() as con:
                                con.execute('INSERT INTO searches VALUES (?, ?, ?) ON CONFLICT(query) DO UPDATE SET created_at=excluded.created_at,payload=excluded.payload', (key, today(), json.dumps(extra, ensure_ascii=False)))
                        merge_candidates(candidates, extra['items'])
                        known.update(p['handle'] for p in extra['items'])
                        sources.append({'source':'SearXNG · ' + (', '.join(extra['engines']) or 'motores configurados'),
                                        'query':query, 'page':page, 'found':len(extra['items']),
                                        'raw_count':extra['raw_count'], 'errors':extra['errors'], 'publication_attempts':extra.get('publication_attempts',0), 'publication_errors':extra.get('publication_errors',[]),
                                        'status':'Cache de hoje' if cached else 'Consultada'})
                        update_job(job_id, sources=sources, found=len(candidates))
                        if not extra['raw_count']:
                            exhausted.add(query)
                        if any('too many requests' in str(error).lower() for error in extra['errors']):
                            stop_queries = True
                            break
                    if stop_queries:
                        break
            else:
                for terms in plan['source_terms']:
                    batch, reports = discover_sources(terms)
                    candidates.extend(p for p in batch if p['handle'] not in known)
                    known.update(p['handle'] for p in batch)
                    sources.extend({**r, 'query': terms} for r in reports)
            if provider == 'brave':
                for query in plan['queries']:
                    try:
                        extra = discover(topic, query=query)
                        candidates.extend(p for p in extra['items'] if p['handle'] not in known)
                        known.update(p['handle'] for p in extra['items'])
                        sources.append({'source': 'Brave Search', 'query': query, 'found': len(extra['items']), 'status': 'Consultada'})
                    except ValueError as error:
                        sources.append({'source': 'Brave Search', 'found': 0, 'status': 'Indisponível', 'detail': str(error)})
        else:
            candidates = profiles()
        # Limite conservador; uma leitura por perfil, sem tentativas de contornar bloqueios.
        terms = fold(topic).split()
        candidates.sort(key=lambda p: -sum(t in fold(p.get('description', '') + ' ' + p.get('tags', '')) for t in terms))
        selected = candidates[:100]
        update_job(job_id, found=len(candidates), total=len(selected), sources=sources)
        results, processed, cache_hits = [], [], 0
        rejections, rejection_counts = [], Counter()
        for index, candidate in enumerate(selected):
            handle = candidate['handle']
            update_job(job_id, message=f'Lendo @{handle} ({index + 1}/{len(selected)})…')
            record,cached=collect_candidate(candidate)
            cache_hits+=int(cached)
            if not cached:time.sleep(1)
            processed.append(record)
            reasons = [] if mode == 'refresh' else rejection_reasons(record, options)
            if not reasons:
                results.append(record)
            else:
                rejection_counts.update(reasons)
                rejections.append({'handle':handle, 'reasons':reasons})
            update_job(job_id, done=index + 1, items=results, rejected=len(processed)-len(results), cached_count=cache_hits,
                       rejection_counts=dict(rejection_counts), rejections=rejections)
        partial = any(source.get('errors') or source.get('publication_errors') for source in sources)
        update_job(job_id, state='done', message=('Busca parcial: houve bloqueios nos motores. A cobertura ficou limitada.' if partial else 'Busca concluída. Veja os resultados desta execução.'), partial=partial, items=results,
                   collected=sum(bool(p.get('bio')) and p.get('followers_count') is not None for p in processed),
                   unavailable=sum(p.get('profile_fetch_status') == 'Indisponível' for p in processed), rejected=len(processed)-len(results),
                   unprocessed=max(0,len(candidates)-len(processed)), rejection_counts=dict(rejection_counts), rejections=rejections)
    except ValueError as error:
        update_job(job_id, state='error', message=str(error))
    except Exception:
        update_job(job_id, state='error', message='A coleta foi interrompida. Os perfis já salvos foram preservados.')
    finally:
        COLLECTION_LOCK.release()


def start_collection(topic, mode='sources', provider='google', criteria=None, urls=None):
    plan = search_plan(topic, criteria)
    topic = str(topic).strip()
    links = []
    if mode=='links':
        if not isinstance(urls,list) or not 1<=len(urls)<=20 or any(not isinstance(url,str) for url in urls):
            raise ValueError('Informe de 1 a 20 URLs de perfis, posts ou reels.')
        for url in dict.fromkeys(urls):
            try:
                links.append({'type':'publication','url':publication_url(url)})
            except ValueError:
                if '://' not in url:
                    raise ValueError('Informe URLs completas do Instagram.')
                handle=handle_from(url)
                links.append({'type':'profile','url':f'https://www.instagram.com/{handle}/'})
    if mode not in ('sources', 'refresh', 'links') or not 2 <= len(topic) <= 180:
        raise ValueError('Use um tema de 2 a 180 caracteres.')
    if provider not in ('public', 'brave', 'searxng', 'google'):
        raise ValueError('Fonte de descoberta inválida.')
    if provider=='google' and not google_browser.installed():
        raise ValueError('Navegador automático não instalado. Execute python3 install_google.py.')
    if provider == 'brave' and not os.environ.get('BRAVE_SEARCH_API_KEY'):
        raise ValueError('A API do buscador ainda não foi configurada.')
    if not COLLECTION_LOCK.acquire(blocking=False):
        with JOB_LOCK:
            active = next((j for j in JOBS.values() if j['state'] in ('running','needs_attention')), None)
        if active:
            raise ValueError('Outra busca está em andamento. Aguarde antes de enviar novos critérios.')
        raise ValueError('Outra coleta está em andamento. Aguarde sua conclusão.')
    job_id = uuid.uuid4().hex
    with JOB_LOCK:
        # Mantém apenas o histórico recente em memória.
        for old_id in list(JOBS)[:-15]:
            if JOBS[old_id]['state'] not in ('running','needs_attention'):
                JOBS.pop(old_id)
        JOBS[job_id] = {'id': job_id, 'state': 'running', 'topic': topic, 'found': 0, 'total': 0, 'done': 0,
                        'items': [], 'sources': [], 'plan': plan, 'mode': mode, 'provider':provider, 'message': 'Iniciando descoberta automática…'}
    threading.Thread(target=run_collection, args=(job_id, topic, mode, provider, plan['criteria'], links), daemon=True).start()
    return get_job(job_id)


def csv_export(items):
    out = io.StringIO()
    fields = ['handle', 'name', 'bio', 'followers_display', 'followers_count', 'followers_precision', 'profile_data_source', 'profile_collected_at', 'profile_fetch_status', 'profile_attempted_at', 'description', 'tags', 'location', 'kind', 'categories', 'posts_fetch_status', 'posts_count', 'status', 'favorite', 'source_url', 'source_type', 'observed_at', 'notes']
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for record in items:
        # Evita interpretar conteúdo externo como fórmula no Excel.
        writer.writerow({k: ("'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v) for k, v in record.items() if k in fields})
    return ('\ufeff' + out.getvalue()).encode('utf-8')


CRM_COLUMNS = [
    ('Nome', 'name'), ('Usuário do Instagram', 'handle'), ('Link do perfil', 'instagram_url'),
    ('Bio', 'bio'), ('Seguidores publicados', 'followers_display'),
    ('Precisão dos seguidores', 'followers_precision'), ('Dados coletados em', 'profile_collected_at'),
    ('Temas', 'tags'), ('Localização informada', 'location'), ('Categoria', 'kind'),
    ('Avaliação do perfil', 'status'), ('Fonte da descoberta', 'source_url'),
    ('Observações do perfil', 'notes'),
    ('Categorias genéricas', 'generic_categories_text'), ('Origem das categorias', 'categories_source'),
    ('Região identificada', 'region_display'), ('Origem da região', 'region_source'),
    ('Regra de empresa', 'company_rule'),
    ('Nome do contato', None), ('WhatsApp / telefone', None), ('E-mail', None),
    ('Canal preferido', None), ('Responsável', None), ('Etapa do contato', None),
    ('Prioridade', None), ('Data do primeiro contato', None), ('Data do último contato', None),
    ('Próximo retorno', None), ('Próxima ação', None), ('Valor proposto (R$)', None),
    ('Observações do contato', None),
]


def crm_export(handles):
    if not isinstance(handles, list) or not 1 <= len(handles) <= 500 or any(not isinstance(h, str) for h in handles):
        raise ValueError('Selecione entre 1 e 500 perfis para exportar.')
    ordered = list(dict.fromkeys(handle_from(h) for h in handles))
    base = {p['handle']: p for p in profiles()}
    if any(h not in base for h in ordered):
        raise ValueError('Um perfil selecionado não está mais na base. Atualize a página e tente novamente.')
    out = io.StringIO(newline='')
    writer = csv.writer(out, delimiter=';', lineterminator='\r\n')
    writer.writerow([label for label, _ in CRM_COLUMNS])
    for handle in ordered:
        original = base[handle]
        record = {**original, 'instagram_url': f'https://www.instagram.com/{handle}/',
                  'generic_categories_text': ', '.join(original['generic_categories']),
                  'region_display': original['region_info']['text'], 'region_source': original['region_info']['source'],
                  'company_rule': original['company_info']['reason']}
        row = []
        for _, key in CRM_COLUMNS:
            value = record.get(key, '') if key else ''
            value = '' if value is None else value
            if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
                value = "'" + value
            row.append(value)
        writer.writerow(row)
    return ('\ufeff' + out.getvalue()).encode('utf-8')


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, status, data, mime='application/json; charset=utf-8', filename=None):
        body = json.dumps(data, ensure_ascii=False).encode() if mime.startswith('application/json') else data
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def allowed(self):
        expected = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if self.headers.get('Host') not in expected:
            return False
        origin = self.headers.get('Origin')
        return not origin or origin in {'http://' + h for h in expected}

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {'error': 'Origem não permitida.'})
        parsed = urlsplit(self.path)
        args = parse_qs(parsed.query)
        arg = lambda k: args.get(k, [''])[0]
        if parsed.path == '/api/config':
            return self.send(200, {'discovery_ready': True, 'searxng_ready': web_search.ready(), 'google_ready':google_browser.installed(), 'brave_ready': bool(os.environ.get('BRAVE_SEARCH_API_KEY')), 'statuses': STATUSES, 'kinds': KINDS, 'today': today(), 'categories': list(CATEGORY_TERMS), 'states': STATES, 'rejection_labels': {key:value[0] for key,value in REJECTION_GROUPS.items()}})
        if parsed.path.startswith('/api/jobs/'):
            try:
                return self.send(200, get_job(parsed.path.rsplit('/', 1)[-1]))
            except ValueError as error:
                return self.send(404, {'error': str(error)})
        if parsed.path in ('/api/profiles', '/api/export.csv'):
            try:
                options = {k: arg(k) for k in ('min_followers', 'max_followers', 'include_unknown_followers', 'region', 'include_unknown_region', 'exclude_companies', 'category', 'keywords', 'scope', 'match', 'hashtags')}
                items = profiles(arg('q'), arg('tag'), arg('status'), arg('favorites') == '1', saved_only=arg('saved')=='1', **options)
            except ValueError as error:
                return self.send(400, {'error': str(error)})
            if parsed.path.endswith('.csv'):
                return self.send(200, csv_export(items), 'text/csv; charset=utf-8')
            return self.send(200, items)
        static = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if parsed.path in static:
            name, mime = static[parsed.path]
            return self.send(200, (ROOT / 'static' / name).read_bytes(), mime)
        return self.send(404, {'error': 'Página não encontrada.'})

    def do_POST(self):
        if not self.allowed() or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.send(403, {'error': 'Origem ou formato não permitido.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 1 or size > 1_000_000:
                raise ValueError('Tamanho de requisição inválido.')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('Envie um objeto JSON.')
            if self.path=='/api/google-control':
                return self.send(200,control_google_job(str(data.get('id','')),data.get('action')))
            if self.path == '/api/profiles':
                return self.send(200, save_profile(data))
            if self.path == '/api/export-crm.csv':
                return self.send(200, crm_export(data.get('handles')), 'text/csv; charset=utf-8', f'vio-crm-{today()}.csv')
            if self.path == '/api/collect-links':
                return self.send(202,start_collection(data.get('q') or 'Conteúdo encontrado','links','searxng',data.get('criteria'),data.get('urls')))
            if self.path == '/api/search-plan':
                return self.send(200, search_plan(data.get('q', ''), data.get('criteria')))
            if self.path == '/api/discover':
                return self.send(202, start_collection(data.get('q', ''), data.get('mode', 'sources'), data.get('provider', 'google'), data.get('criteria')))
            if self.path == '/api/import':
                items = data.get('items')
                if not isinstance(items, list) or len(items) > 500:
                    raise ValueError('Importe uma lista de até 500 perfis.')
                with connect() as con:
                    for item in items:
                        save_profile(item, con)
                return self.send(200, {'imported': len(items)})
            return self.send(404, {'error': 'Rota não encontrada.'})
        except (ValueError, TypeError) as error:
            return self.send(400, {'error': str(error)})
        except Exception:
            return self.send(500, {'error': 'Falha interna. Os detalhes não são expostos no navegador.'})


if __name__ == '__main__':
    initialize()
    search_process = start_local(ROOT)
    port = int(os.environ.get('AGGEO_INFLUENCERS_PORT', '8765'))
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'Vio · Radar de criadores: http://127.0.0.1:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        with JOB_LOCK:
            workers=list(GOOGLE_WORKERS.values())
        for process in workers:
            try:
                google_browser.command(process,'cancel')
                process.wait(timeout=5)
            except Exception:
                process.terminate()
        stop_local(search_process)
