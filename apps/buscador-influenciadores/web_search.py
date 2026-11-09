"""Cliente do SearXNG: resultados públicos, sem chaves ou fontes setoriais fixas."""
import html
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from collector import profile_handle, publication_url, collect_publication


def base_url():
    value = os.environ.get('SEARXNG_URL', 'http://127.0.0.1:8888').rstrip('/')
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('SEARXNG_URL deve ser o endereço HTTP/HTTPS da instância.')
    return value


def ready():
    try:
        with urlopen(base_url() + '/healthz', timeout=1) as response:
            return response.status == 200
    except (ValueError, URLError, TimeoutError, OSError):
        return False


def search(query, page=1):
    params = urlencode({'q': query, 'format': 'json', 'language': 'pt-BR',
                        'categories': 'general', 'pageno': page, 'safesearch': 0})
    req = Request(base_url() + '/search?' + params, headers={'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=35) as response:
            payload = response.read(4_000_001)
        if len(payload) > 4_000_000:
            raise ValueError('Resposta do buscador excedeu o limite de leitura.')
        raw = json.loads(payload)
        if not isinstance(raw, dict) or not isinstance(raw.get('results'), list):
            raise ValueError('Resposta inválida do SearXNG.')
    except HTTPError as error:
        raise ValueError(f'SearXNG retornou HTTP {error.code}. Verifique se o formato JSON está habilitado.') from None
    except (URLError, TimeoutError, OSError):
        raise ValueError('O buscador SearXNG não respondeu. Reinicie a Vio pelo arquivo Iniciar.command.') from None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError('O buscador não retornou JSON válido.') from None
    items, seen, engines = [], set(), set()
    publication_attempts, publication_errors = 0, []
    for hit in raw['results']:
        if not isinstance(hit, dict):
            continue
        engines.update(str(e) for e in hit.get('engines', []))
        try:
            # Exige URL de perfil: posts, reels e outros domínios não viram perfis.
            url = hit.get('url', '')
            if '://' not in url:
                continue
            handle = profile_handle(url)
        except (ValueError, TypeError):
            try:
                post_url = publication_url(hit.get('url', ''))
            except ValueError:
                continue
            if publication_attempts >= 5:
                continue
            publication_attempts += 1
            try:
                candidate = collect_publication(post_url)
                existing = next((p for p in items if p['handle'] == candidate['handle']), None)
                if existing:
                    existing['posts'] = list({p['source_url']:p for p in existing.get('posts', []) + candidate['posts']}.values())[:20]
                else:
                    items.append(candidate)
                    seen.add(candidate['handle'])
            except (ValueError, URLError, TimeoutError, OSError) as error:
                publication_errors.append({'url':post_url, 'reason':str(error)[:250]})
            continue
        if handle in seen:
            continue
        seen.add(handle)
        clean = lambda text: re.sub('<[^>]*>', '', html.unescape(str(text)))[:5000]
        items.append({'handle': handle, 'name': clean(hit.get('title') or handle),
                      'description': clean(hit.get('content', '')), 'tags': '',
                      'source_url': f'https://www.instagram.com/{handle}/',
                      'source_type': 'Resultado web via SearXNG · ' + ', '.join(hit.get('engines', [])),
                      'notes': 'Consulta de descoberta: ' + query})
    return {'items': items, 'query': query, 'page': page, 'raw_count': len(raw['results']),
            'engines': sorted(engines), 'errors': raw.get('unresponsive_engines', []),
            'publication_attempts':publication_attempts, 'publication_errors':publication_errors}
