#!/usr/bin/env python3
"""Interface local para extrair vagas. Execute pelo aplicativo Adaptar Vaga.app."""
import argparse
import json
import os
from pathlib import Path
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import webbrowser

from extrair_vaga import ExtractionError, MAX_CHARS, extract_validated, normalize, read_source, save_candidatura

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / '.local' / 'openai-key'
TOKEN = secrets.token_urlsafe(32)
KEY_LOCK = threading.Lock()


def get_key():
    with KEY_LOCK:
        if KEY_FILE.exists():
            return KEY_FILE.read_text(encoding='utf-8').strip()
    return os.environ.get('OPENAI_API_KEY', '').strip()


def save_key(key):
    if not isinstance(key, str) or not key.strip().startswith('sk-') or len(key.strip()) < 20:
        raise ExtractionError('Cole uma chave válida da API OpenAI, começando com sk-.')
    key = key.strip()
    if any(c.isspace() for c in key) or len(key) > 1024:
        raise ExtractionError('A chave contém caracteres inválidos.')
    with KEY_LOCK:
        KEY_FILE.parent.mkdir(mode=0o700, exist_ok=True)
        os.chmod(KEY_FILE.parent, 0o700)
        fd = os.open(KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(key)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Não registra links, texto de vagas ou credenciais.

    def reply(self, status, body, content_type='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        if status == 200 and getattr(self, 'candidatura_path', None):
            self.send_header('X-Candidatura-Pasta', self.candidatura_path)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def trusted_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def do_GET(self):
        if not self.trusted_host():
            return self.reply(403, {'erro': 'Acesso permitido apenas pela interface local.'})
        if self.path == '/api/status':
            return self.reply(200, {'configured': bool(get_key()), 'token': TOKEN})
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if self.path not in files:
            return self.reply(404, {'erro': 'Página não encontrada.'})
        name, kind = files[self.path]
        self.reply(200, (ROOT / 'interface' / name).read_bytes(), kind)

    def do_POST(self):
        origin = f'http://127.0.0.1:{self.server.server_port}'
        if (not self.trusted_host() or self.headers.get('Origin') != origin
                or not secrets.compare_digest(self.headers.get('X-Local-Token', ''), TOKEN)):
            return self.reply(403, {'erro': 'Reabra a interface para continuar.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 650000:
                raise ExtractionError('Conteúdo vazio ou muito grande.')
            if self.headers.get_content_type() != 'application/json':
                raise ExtractionError('Formato de pedido inválido.')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ExtractionError('Pedido inválido.')
            if self.path == '/api/key':
                save_key(data.get('key'))
                return self.reply(200, {'configured': True})
            if self.path != '/api/extract':
                return self.reply(404, {'erro': 'Operação não encontrada.'})
            key = get_key()
            if not key:
                raise ExtractionError('Configure sua chave da API para extrair a vaga.')
            text = data.get('text', '')
            url = data.get('url', '')
            if not isinstance(text, str) or not isinstance(url, str):
                raise ExtractionError('Link ou texto inválido.')
            if text.strip():
                if len(normalize(text)) < 80 or len(text) > MAX_CHARS:
                    raise ExtractionError('Cole a descrição completa, entre 80 e 100 mil caracteres.')
            else:
                text = read_source(url=url.strip())
            model = os.environ.get('OPENAI_EXTRACTION_MODEL',
                                   os.environ.get('OPENAI_MODEL', 'gpt-6.1-sol'))
            result = extract_validated(text, key, model)
            self.candidatura_path = str(save_candidatura(result).relative_to(ROOT))
            return self.reply(200, result)
        except ExtractionError as exc:
            message = str(exc).replace('use --arquivo', 'cole o texto na opção “Colar descrição”').replace('Use o anúncio completo em --arquivo.', 'Cole o anúncio completo na opção “Colar descrição”.').replace('Tente --arquivo.', 'Use a opção “Colar descrição”.')
            return self.reply(400, {'erro': message})
        except (ValueError, UnicodeError):
            return self.reply(400, {'erro': 'Não foi possível interpretar os dados recebidos.'})
        except Exception:
            return self.reply(500, {'erro': 'Não foi possível concluir. Verifique a conexão e tente novamente.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.daemon_threads = True
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Extrator de vagas aberto em {url}\nMantenha esta janela aberta. Para encerrar, pressione Ctrl+C.', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
