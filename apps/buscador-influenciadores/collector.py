"""Descoberta em fontes públicas e leitura de metadados públicos do Instagram."""
import html
import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

AGRI = 'https://www.agrishow.com.br/imprensa/embaixadores/'
USER_AGENT = 'AgGeoResearch/0.2 (personal local research)'
RESERVED = {'p', 'reel', 'reels', 'stories', 'explore', 'accounts', 'direct', 'about', 'legal', 'developer', 'web', 'share', 'tv'}


def profile_handle(value):
    value = str(value).strip()
    if '://' in value:
        parsed = urlsplit(value)
        if parsed.scheme not in ('https', 'http') or parsed.hostname not in ('instagram.com', 'www.instagram.com', 'm.instagram.com') or parsed.username or parsed.password:
            raise ValueError('Use um endereço de perfil do Instagram.')
        parts = parsed.path.strip('/').split('/')
        if len(parts) != 1:
            raise ValueError('Use o endereço do perfil, não de uma publicação.')
        value = parts[0]
    value = value.lstrip('@').lower()
    if not re.fullmatch(r'[a-z0-9_](?:[a-z0-9_.]{0,28}[a-z0-9_])?', value) or '..' in value or value in RESERVED:
        raise ValueError('Nome de usuário inválido.')
    return value


def fetch_public(url):
    req = Request(url, headers={'User-Agent': USER_AGENT, 'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'})
    with urlopen(req, timeout=15) as response:
        if response.status != 200:
            raise ValueError(f'Fonte indisponível (HTTP {response.status}).')
        body = response.read(3_000_001)
        if len(body) > 3_000_000:
            raise ValueError('Página excede o limite de leitura.')
        return body.decode('utf-8', 'replace'), response.geturl()


class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.blocks = {}, [], []
        self.anchor = None
        self.block = None
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.ignored += 1
        if self.ignored:
            return
        if tag == 'meta':
            key = attrs.get('property', attrs.get('name', '')).lower()
            self.meta[key] = attrs.get('content', '')
        if tag == 'a':
            self.anchor = [attrs.get('href', ''), '']
        if tag in ('p', 'h2', 'h3'):
            self.block = []

    def handle_data(self, data):
        if self.ignored:
            return
        if self.anchor is not None:
            self.anchor[1] += data
        if self.block is not None:
            self.block.append(data)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.ignored = max(0, self.ignored - 1)
        if self.ignored:
            return
        if tag == 'a' and self.anchor is not None:
            self.links.append(tuple(self.anchor))
            self.anchor = None
        if tag in ('p', 'h2', 'h3') and self.block is not None:
            self.blocks.append(' '.join(''.join(self.block).split()))
            self.block = None


def parse_html(text):
    parser = PublicHTML()
    parser.feed(text)
    return parser


def followers_from(text):
    """Mantém o texto publicado; a expansão de K/M é aproximada, não exata."""
    match = re.search(r'(?<![\w.,])([0-9][0-9.,\u00a0 ]*\s*(?:milhões|milhão|million|mil|[KMB])?)\s+(followers|seguidores)\b', text, re.I)
    if not match:
        return {'followers_count': None, 'followers_display': '', 'followers_precision': 'Indisponível'}
    raw = match.group(1).strip()
    suffix = re.search(r'(milhões|milhão|million|mil|[KMB])$', raw, re.I)
    number = re.sub(r'\s', '', raw[:suffix.start()] if suffix else raw)
    try:
        if suffix:
            multiplier = 1000 if suffix.group().lower() in ('k', 'mil') else (1_000_000_000 if suffix.group().lower() == 'b' else 1_000_000)
            if ',' in number and '.' in number:
                decimal = ',' if number.rfind(',') > number.rfind('.') else '.'
                number = number.replace('.' if decimal == ',' else ',', '').replace(decimal, '.')
            else:
                number = number.replace(',', '.')
            count = int(Decimal(number) * multiplier)
        else:
            count = int(re.sub(r'[.,]', '', number))
    except (InvalidOperation, ValueError):
        count = None
    return {'followers_count': count, 'followers_display': raw,
            'followers_precision': 'Abreviado pelo Instagram' if suffix else 'Inteiro publicado pelo Instagram'}


def parse_instagram(text, handle):
    meta = parse_html(text).meta
    title = meta.get('og:title', '')
    description = meta.get('description', '')
    og_description = meta.get('og:description', '')
    if not any(re.search(r'@' + re.escape(handle) + r'(?![a-z0-9_.])', value, re.I) for value in (title, description, og_description)):
        raise ValueError('O Instagram não entregou metadados identificáveis deste perfil (login, bloqueio ou perfil indisponível).')
    followers = followers_from(description or og_description)
    if followers['followers_count'] is None:
        followers = followers_from(og_description)
    # A bio aparece em meta[name=description], após o texto "no/on Instagram:".
    # Não usamos texto de post, inferência de IA nem apresentação de terceiros como bio.
    bio_match = re.search(r'\b(?:no|on) Instagram:\s*["“](.*)["”]\s*$', description, re.S | re.I)
    bio = bio_match.group(1).strip() if bio_match else ''
    name = re.sub(r'\s*\(@' + re.escape(handle) + r'\).*$', '', title, flags=re.I).strip()
    posts = posts_from_public_html(text, handle)
    return {**followers, 'bio': bio, 'public_name': name, 'posts': posts,
            'posts_fetch_status': 'Conteúdo público parcial' if posts else 'Publicações não disponibilizadas no HTML público',
            'posts_attempted_at': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
            'profile_fetch_status': 'Coletado' if bio and followers['followers_count'] is not None else 'Parcial',
            'profile_data_source': f'https://www.instagram.com/{handle}/',
            'profile_collected_at': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()}


def posts_from_public_html(text, handle):
    """Apenas dados estruturados publicados, com URL de post e autor identificáveis."""
    posts = {}
    def walk(value):
        if isinstance(value, list):
            for entry in value:
                walk(entry)
        elif isinstance(value, dict):
            author = value.get('author', {})
            author = author if isinstance(author, dict) else {}
            identity = author.get('url') or author.get('alternateName') or ''
            try:
                owner = profile_handle(identity)
            except ValueError:
                owner = ''
            url = value.get('url', '')
            content = value.get('articleBody') or value.get('caption') or value.get('description')
            if isinstance(url, str) and isinstance(content, str) and owner == handle:
                parsed = urlsplit(url)
                if parsed.hostname in ('www.instagram.com', 'instagram.com') and re.fullmatch(r'/(?:p|reel)/[A-Za-z0-9_-]+/?', parsed.path):
                    posts[url] = {'text': content[:10000], 'source_url': url, 'author_handle': owner,
                                  'source_type': 'Dados estruturados públicos do Instagram',
                                  'collected_at': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()}
            for entry in value.values():
                if isinstance(entry, (dict, list)):
                    walk(entry)
    for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.S | re.I):
        try:
            walk(json.loads(raw))
        except (ValueError, RecursionError):
            continue
    return list(posts.values())[:20]


def publication_url(value):
    """Normaliza apenas URLs de posts/reels, sem permitir destinos arbitrários."""
    parsed = urlsplit(str(value))
    if parsed.scheme not in ('https', 'http') or parsed.hostname not in ('instagram.com', 'www.instagram.com') or parsed.username or parsed.password:
        raise ValueError('Use uma URL pública de publicação do Instagram.')
    parts = parsed.path.strip('/').split('/')
    if len(parts) == 3:
        profile_handle(parts.pop(0))
    if len(parts) != 2 or parts[0] not in ('p', 'reel') or not re.fullmatch(r'[A-Za-z0-9_-]+', parts[1]):
        raise ValueError('Use o link de um post ou reel do Instagram.')
    return f'https://www.instagram.com/{parts[0]}/{parts[1]}/'


def parse_publication(text, url):
    url = publication_url(url)
    meta = parse_html(text).meta
    identities = set()
    canonical = meta.get('og:url', '')
    if canonical:
        if publication_url(canonical) != url:
            raise ValueError('Os metadados pertencem a outra publicação.')
        parts = urlsplit(canonical).path.strip('/').split('/')
        if len(parts) == 3:
            identities.add(profile_handle(parts[0]))
    description = meta.get('description') or meta.get('og:description', '')
    # O autor está no cabeçalho dos metadados, antes da data/legenda.
    # @menções da legenda não são evidência de autoria.
    author = re.match(r'^.*?\s[-–—]\s([A-Za-z0-9_.]+)\s+(?:no|on|em)\s+[^:]+:', description, re.S)
    if author:
        identities.add(profile_handle(author.group(1)))
    if len(identities) != 1:
        raise ValueError('Autoria não confirmada nos metadados públicos da publicação.')
    handle = identities.pop()
    caption = re.search(r':\s*["“](.*)["”]\s*\.?\s*$', description, re.S)
    if not caption:
        raise ValueError('O texto da publicação não foi disponibilizado publicamente.')
    name = re.split(r'\s+(?:no|on) Instagram:', meta.get('og:title', ''), maxsplit=1, flags=re.I)[0].strip()
    post = {'text': caption.group(1).strip()[:10000], 'source_url': url, 'author_handle': handle,
            'source_type': 'Metadados públicos da publicação; autoria pelo cabeçalho/canônico',
            'collected_at': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()}
    return {'handle':handle, 'name':name or handle, 'description':'Autor identificado em publicação sobre o tema pesquisado.',
            'tags':'', 'source_url':url, 'source_type':'Publicação pública do Instagram com autoria identificada',
            'posts':[post], 'posts_fetch_status':'Publicação de descoberta coletada'}


def collect_publication(url):
    url = publication_url(url)
    text, final_url = fetch_public(url)
    if publication_url(final_url) != url:
        raise ValueError('A publicação redirecionou para outra página.')
    return parse_publication(text, url)


def collect_instagram(handle):
    handle = profile_handle(handle)
    try:
        text, final_url = fetch_public(f'https://www.instagram.com/{handle}/')
        if profile_handle(final_url) != handle:
            raise ValueError('O Instagram redirecionou para outra página.')
        return parse_instagram(text, handle)
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        if isinstance(error, HTTPError):
            reason = f'Instagram respondeu HTTP {error.code}; nenhuma tentativa de contornar o bloqueio.'
        else:
            reason = str(error)[:300]
        return {'profile_fetch_status': 'Indisponível', 'profile_fetch_error': reason,
                'profile_attempted_at': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()}


def extract_candidates(text, source_url, source_type, context='', exclude=()):
    doc = parse_html(text)
    # Links visíveis no documento, sem extrair nomes de scripts ou inventar usuários.
    found = {}
    for href, label in doc.links:
        try:
            if '://' not in href:
                continue
            handle = profile_handle(href)
        except ValueError:
            continue
        if handle in exclude:
            continue
        found.setdefault(handle, {'handle': handle, 'name': handle, 'description': context[:1200],
                                  'tags': '', 'source_url': source_url, 'source_type': source_type})
    return list(found.values())


def discover_sources(topic):
    """Fontes abertas finitas, renovadas a cada execução; não é busca global."""
    candidates, reports = {}, []
    try:
        text, final = fetch_public(AGRI)
        items = extract_candidates(text, final, 'Links públicos da Agrishow',
                                   'Perfil citado na página de embaixadores da Agrishow. Adequação à Ag.Geo a revisar.',
                                   exclude=('feiraagrishowoficial',))
        for item in items:
            candidates[item['handle']] = item
        reports.append({'source': 'Agrishow', 'found': len(items), 'status': 'Consultada'})
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        reports.append({'source': 'Agrishow', 'found': 0, 'status': 'Indisponível', 'detail': str(error)[:200]})
    # API WordPress pública, sem chave. Busca artigos que contenham o tema e Instagram.
    params = urlencode({'search': topic + ' instagram', 'orderby': 'relevance', 'per_page': 10, '_fields': 'link,title,content'})
    try:
        text, _ = fetch_public('https://mundogeo.com/wp-json/wp/v2/posts?' + params)
        posts = json.loads(text)
        if not isinstance(posts, list):
            raise ValueError('Resposta inesperada da fonte.')
        count = 0
        for post in posts:
            source_url = post.get('link', '')
            if urlsplit(source_url).hostname != 'mundogeo.com':
                continue
            title = html.unescape(re.sub('<[^>]*>', '', post.get('title', {}).get('rendered', '')))
            for item in extract_candidates(post.get('content', {}).get('rendered', ''), source_url,
                                           'Link em artigo do MundoGEO', 'Encontrado no artigo: ' + title,
                                           exclude=('mundogeo', 'mundogeoconnect', 'droneshowla', 'expoevtol', 'spacebrshow')):
                candidates.setdefault(item['handle'], item)
                count += 1
        reports.append({'source': 'MundoGEO · busca temática', 'found': count, 'status': 'Consultada'})
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        reports.append({'source': 'MundoGEO · busca temática', 'found': 0, 'status': 'Indisponível', 'detail': str(error)[:200]})
    return list(candidates.values()), reports
