import base64
import json
import os
import secrets
import struct
import subprocess
import tempfile
import threading
import urllib.request
import urllib.error
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'imagens'
TOKEN = secrets.token_urlsafe(32)
KEY = ''
JOB = {'state': 'idle'}
LOCK = threading.Lock()
SIZES = {'1080x1350', '1024x1024', '1536x1024', '1024x1536', '1536x864', '864x1536'}
QUALITIES = {'low', 'medium', 'high', 'xhigh', 'max'}

MAX_REFERENCE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024

def decode_references(items):
    if not isinstance(items, list) or len(items) > 4:
        raise ValueError('Escolha até 4 imagens de referência.')
    decoded = []
    total = 0
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('data'), str):
            raise ValueError('Referência inválida. Selecione a imagem novamente.')
        try:
            data = base64.b64decode(item['data'], validate=True)
        except (ValueError, TypeError):
            raise ValueError('Referência inválida. Selecione a imagem novamente.')
        total += len(data)
        if not data or len(data) > MAX_REFERENCE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError('Use até 10 MB por imagem e 20 MB no total.')
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            mime, ext = 'image/png', 'png'
        elif data.startswith(b'\xff\xd8\xff'):
            mime, ext = 'image/jpeg', 'jpg'
        elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
            mime, ext = 'image/webp', 'webp'
        else:
            raise ValueError('Use imagens PNG, JPG ou WebP.')
        decoded.append((data, mime, ext))
    return decoded

def api_size(size):
    return '1024x1280' if size == '1080x1350' else size

def prepare_output(data, size):
    if size != '1080x1350':
        return data
    width, height = struct.unpack('>II', data[16:24])
    if (width, height) == (1080, 1350):
        return data
    if width * 5 != height * 4:
        raise ValueError('A imagem recebida não está na proporção 4:5.')
    with tempfile.TemporaryDirectory(prefix='studio-resize-') as tmp:
        source, target = Path(tmp) / 'source.png', Path(tmp) / 'output.png'
        source.write_bytes(data)
        subprocess.run(['/usr/bin/sips', '--resampleHeightWidth', '1350', '1080',
                        str(source), '--out', str(target)], check=True,
                       capture_output=True, timeout=60)
        result = target.read_bytes()
    if struct.unpack('>II', result[16:24]) != (1080, 1350):
        raise ValueError('Não foi possível exportar em 1080 × 1350.')
    return result

def image_request(payload, key):
    fields = dict(model='gpt-image-2.5-sunburst', prompt=payload['prompt'],
                  size=api_size(payload['size']), quality=payload['quality'], output_format='png', n=1)
    references = decode_references(payload.get('references', []))
    if not references:
        body = json.dumps(fields).encode()
        endpoint, content_type = 'generations', 'application/json'
    else:
        boundary = 'studio-' + secrets.token_hex(24)
        parts = []
        for name, value in fields.items():
            parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n').encode())
        for i, (data, mime, ext) in enumerate(references, 1):
            parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="reference-{i}.{ext}"\r\nContent-Type: {mime}\r\n\r\n').encode() + data + b'\r\n')
        parts.append(f'--{boundary}--\r\n'.encode())
        body = b''.join(parts)
        endpoint, content_type = 'edits', 'multipart/form-data; boundary=' + boundary
    return urllib.request.Request('https://api.openai.com/v1/images/' + endpoint, data=body,
           headers={'Content-Type': content_type, 'Authorization': 'Bearer ' + key})

def markdown_document(item):
    body = item['prompt']
    if not body.lstrip().startswith('#'):
        body = '# Briefing de imagem\n\n## Objetivo\n' + body
    return (f"---\npadrao: sunburst-brief-v1\nformato: {item['size']}\n"
            f"qualidade: {item['quality']}\n---\n\n{body.rstrip()}\n\n"
            f"<!-- sunburst-result -->\n## Imagem gerada\n\n![Imagem gerada]({item['name']})\n")


def generate(payload, key):
    global JOB
    try:
        req = image_request(payload, key)
        with urllib.request.urlopen(req, timeout=600) as response:
            result = json.load(response)
        data = base64.b64decode(result['data'][0]['b64_json'], validate=True)
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('invalid image')
        data = prepare_output(data, payload['size'])
        OUTPUT.mkdir(exist_ok=True)
        name = datetime.now().strftime('imagem-%Y%m%d-%H%M%S-') + secrets.token_hex(3)
        (OUTPUT / (name + '.png')).write_bytes(data)
        item = {'name': name + '.png', 'prompt': payload['prompt'], 'size': payload['size'],
                'reference_count': len(payload.get('references', [])),
                'generation_size': api_size(payload['size']),
                'quality': payload['quality'], 'created': datetime.now().isoformat(timespec='seconds')}
        (OUTPUT / (name + '.md')).write_text(markdown_document(item), encoding='utf-8')
        (OUTPUT / (name + '.json')).write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
        with LOCK:
            JOB = {'state': 'done', 'item': item}
    except urllib.error.HTTPError as e:
        messages = {401: 'Chave inválida. Informe uma nova chave e tente novamente.',
                    403: 'Seu projeto não tem acesso ao modelo. Confira as permissões e a verificação da organização na OpenAI.',
                    404: 'O modelo Sunburst não está disponível para esta solicitação. Confira o acesso do seu projeto.',
                    429: 'Confira o saldo e os limites de uso na plataforma OpenAI antes de tentar novamente.',
                    400: 'A OpenAI recusou a solicitação. Revise a descrição e as opções escolhidas.'}
        message = messages.get(e.code, 'A OpenAI retornou um erro. Tente novamente mais tarde.')
        with LOCK:
            JOB = {'state': 'error', 'message': message}
    except (TimeoutError, urllib.error.URLError):
        with LOCK:
            JOB = {'state': 'error', 'message': 'A conexão não terminou. Confira seu uso na OpenAI antes de repetir, pois o pedido pode ter sido processado.'}
    except Exception:
        with LOCK:
            JOB = {'state': 'error', 'message': 'Não foi possível salvar o resultado. Confira o uso na OpenAI antes de repetir a geração.'}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, body, mime='application/json'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        return secrets.compare_digest(self.headers.get('X-Studio-Token', ''), TOKEN)

    def do_GET(self):
        if self.path == '/health':
            return self.send(200, {'app': 'sunburst-studio-v2', 'pid': os.getpid()})
        if self.path == '/session':
            expected_host = f'127.0.0.1:{self.server.server_port}'
            if (self.headers.get('Host') != expected_host
                    or self.headers.get('X-Studio-Client') != '1'
                    or self.headers.get('Sec-Fetch-Site') != 'same-origin'):
                return self.send(403, {'message': 'Abra o Studio pelo aplicativo.'})
            return self.send(200, {'token': TOKEN})
        if self.path == '/':
            return self.send(200, (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if not self.authorized():
            return self.send(403, {'message': 'Abra a interface pelo atalho Gerar imagens.'})
        if self.path == '/status':
            with LOCK:
                return self.send(200, {**JOB, 'has_key': bool(KEY)})
        if self.path == '/history':
            items = []
            for p in sorted(OUTPUT.glob('imagem-*.json'), reverse=True):
                try:
                    item = json.loads(p.read_text())
                    if (OUTPUT / item['name']).is_file():
                        items.append(item)
                except (ValueError, KeyError, OSError):
                    continue
            return self.send(200, items[:100])
        if self.path.startswith('/brief/'):
            name = self.path[len('/brief/'):]
            if '/' in name or '\\' in name or not name.startswith('imagem-') or not name.endswith('.png'):
                return self.send(404, {})
            path = OUTPUT / (name[:-4] + '.json')
            if path.is_file():
                item = json.loads(path.read_text())
                return self.send(200, markdown_document(item).encode(), 'text/markdown; charset=utf-8')
        if self.path.startswith('/image/'):
            name = self.path[len('/image/'):]
            if '/' in name or '\\' in name or not name.startswith('imagem-') or not name.endswith('.png'):
                return self.send(404, {})
            path = OUTPUT / name
            if path.is_file():
                return self.send(200, path.read_bytes(), 'image/png')
        self.send(404, {})

    def do_POST(self):
        global KEY, JOB
        if not self.authorized() or self.headers.get('Origin') != f'http://127.0.0.1:{self.server.server_port}':
            return self.send(403, {'message': 'Solicitação não autorizada.'})
        if self.path == '/shutdown':
            with LOCK:
                if JOB['state'] == 'running':
                    return self.send(409, {'message': 'Aguarde a geração terminar antes de encerrar.'})
            self.send(200, {})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if self.path != '/generate':
            return self.send(404, {})
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length < 29 * 1024 * 1024:
                raise ValueError()
            payload = json.loads(self.rfile.read(length))
            decode_references(payload.get('references', []))
            prompt = payload.get('prompt', '').strip()
            key = payload.get('key', '').strip() or KEY
            if not prompt or len(prompt) > 10000:
                raise ValueError('Escreva uma descrição de até 10.000 caracteres.')
            if payload.get('size') not in SIZES or payload.get('quality') not in QUALITIES:
                raise ValueError('Escolha um formato e uma qualidade válidos.')
            if not key.startswith('sk-') or any(c.isspace() for c in key):
                raise ValueError('Informe somente sua chave secreta da OpenAI, iniciada por sk-.')
        except (ValueError, TypeError, AttributeError) as e:
            return self.send(400, {'message': str(e) or 'Revise os campos.'})
        with LOCK:
            if JOB['state'] == 'running':
                return self.send(409, {'message': 'Já existe uma imagem sendo gerada. Aguarde.'})
            KEY = key
            JOB = {'state': 'running'}
        payload['prompt'] = prompt
        threading.Thread(target=generate, args=(payload, key), daemon=True).start()
        self.send(202, {'state': 'running'})

if __name__ == '__main__':
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer(('127.0.0.1', 62028), Handler)
    url = f'http://127.0.0.1:{server.server_port}/#{TOKEN}'
    if os.environ.get('STUDIO_NO_BROWSER'):
        print(url, flush=True)
    else:
        webbrowser.open(url)
        print('Sunburst Studio aberto no navegador. Use Encerrar na interface para fechar.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        KEY = ''
        server.server_close()
