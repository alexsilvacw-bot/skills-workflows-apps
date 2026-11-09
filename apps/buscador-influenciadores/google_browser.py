"""Protocolo local do navegador Google da Vio e parsing de resultados públicos."""
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import parse_qs, urlsplit, urlencode

from collector import parse_html, profile_handle, publication_url

ROOT = Path(__file__).resolve().parent
BROWSER_RUNTIME = Path(os.environ.get('VIO_BROWSER_RUNTIME', Path.home()/'Library/Caches/VioBrowser'))


def search_pages(queries, pages_per_query=10):
    queries=list(dict.fromkeys(queries))[:16]
    pages=max(1,min(10,int(pages_per_query)))
    return [{'query':query,'query_index':index,'page':page,
             'url':'https://www.google.com/search?'+urlencode({'q':query,'hl':'pt-BR','udm':'14','start':(page-1)*10})}
            for page in range(1,pages+1) for index,query in enumerate(queries)]


def normalized_instagram_url(value):
    value=str(value or '')
    parsed = urlsplit(value)
    if parsed.hostname in ('google.com', 'www.google.com', 'google.com.br', 'www.google.com.br') or value.startswith('/url?'):
        if parsed.path != '/url':
            raise ValueError('Não é um resultado de destino.')
        args = parse_qs(parsed.query)
        value = (args.get('q') or args.get('url') or [''])[0]
    try:
        return publication_url(value), 'publication'
    except ValueError:
        if '://' not in value:
            raise ValueError('Destino não é URL pública.')
        handle = profile_handle(value)
        return f'https://www.instagram.com/{handle}/', 'profile'


def extract_result_links(links):
    results, seen = [], set()
    for entry in links:
        try:
            url, kind = normalized_instagram_url(entry['url'])
        except (ValueError, TypeError, KeyError):
            # Algumas páginas do Google usam um destino opaco /goto.
            # Seguir o link no navegador é necessário antes de validar a URL final.
            parsed=urlsplit(str(entry.get('url','')))
            if parsed.hostname in ('google.com','www.google.com','google.com.br','www.google.com.br') and parsed.path=='/goto' and 'instagram' in str(entry.get('title','')).lower():
                url,kind=str(entry['url']),'redirect'
            else:
                continue
        if url not in seen:
            seen.add(url)
            results.append({'url':url, 'type':kind, 'title':str(entry.get('title',''))[:1000]})
    return results


def challenge_reason(url, text, status=None):
    """Apenas detecta barreiras; nenhuma tentativa de resolver ou ocultar automação."""
    path = urlsplit(url).path.lower()
    text = text.lower()
    if '/sorry/' in path or any(term in text for term in (
            'our systems have detected unusual traffic', 'nossos sistemas detectaram tráfego incomum',
            'confirme que você não é um robô', 'verify you are human', 'confirm you are human')):
        return 'O site solicitou uma verificação humana no navegador da Vio.'
    if status in (403, 429) or any(term in text for term in ('too many requests','muitas solicitações','access denied','acesso negado')):
        return f'O site limitou o acesso (HTTP {status}). Aguarde; a Vio não repetirá a solicitação automaticamente.'
    if '/accounts/login' in path or '/challenge/' in path or '/checkpoint/' in path:
        return 'O Instagram solicitou login ou verificação. A coleta está pausada.'
    return ''


def installed():
    python = BROWSER_RUNTIME / 'venv/bin/python'
    packages = list((BROWSER_RUNTIME / 'venv/lib').glob('python*/site-packages/playwright'))
    browsers = list((BROWSER_RUNTIME / 'google-browser-binaries').glob('chromium-*'))
    return bool(python.exists() and packages and browsers)


def start(payload):
    if not installed():
        raise ValueError('Navegador Google não instalado. Execute python3 install_google.py.')
    runtime = BROWSER_RUNTIME
    env = {**os.environ, 'PLAYWRIGHT_BROWSERS_PATH':str(runtime/'google-browser-binaries')}
    log = (runtime/'google-browser.log').open('a')
    try:
        process = subprocess.Popen([str(runtime/'venv/bin/python'), '-u', str(ROOT/'google_worker.py')],
                                   cwd=ROOT, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=log, text=True, bufsize=1)
    finally:
        log.close()
    process.stdin.write(json.dumps(payload, ensure_ascii=False)+'\n')
    process.stdin.flush()
    return process


def command(process, action):
    if action not in ('resume','cancel'):
        raise ValueError('Ação inválida para o navegador.')
    if process.poll() is not None:
        raise ValueError('O navegador desta execução já foi encerrado.')
    try:
        process.stdin.write(json.dumps({'action':action})+'\n')
        process.stdin.flush()
    except (BrokenPipeError, OSError):
        raise ValueError('O navegador não está mais disponível.') from None
