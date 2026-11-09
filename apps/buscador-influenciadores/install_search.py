"""Instalação reproduzível e isolada do SearXNG usado pela Vio."""
from pathlib import Path
import secrets
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REVISION = '629368e40c2aa4edffb05636a8bbc23d2eaa5923'


def install():
    runtime = ROOT / 'runtime'
    runtime.mkdir(exist_ok=True)
    source = runtime / 'searxng'
    if not source.exists():
        subprocess.run(['git', 'clone', '--depth', '1', 'https://github.com/searxng/searxng.git', str(source)], check=True)
        subprocess.run(['git', '-C', str(source), 'fetch', '--depth', '1', 'origin', REVISION], check=True)
        subprocess.run(['git', '-C', str(source), 'checkout', '--detach', REVISION], check=True)
    elif subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != REVISION:
        raise SystemExit('O código local do SearXNG usa outra revisão. Revise antes de atualizar; arquivos locais foram preservados.')
    python = runtime / 'venv/bin/python'
    if not python.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(runtime / 'venv')], check=True)
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(source / 'requirements.txt')], check=True)
    settings = runtime / 'settings.yml'
    if not settings.exists():
        settings.write_text('''use_default_settings:
  engines:
    keep_only: [duckduckgo, brave, startpage]
general:
  instance_name: "Vio · Busca web local"
search:
  formats: [html, json]
  default_lang: pt-BR
  autocomplete: ""
server:
  port: 8888
  bind_address: 127.0.0.1
  limiter: false
  public_instance: false
  secret_key: "''' + secrets.token_hex(32) + '''"
valkey:
  url: false
outgoing:
  request_timeout: 10.0
  max_request_timeout: 15.0
engines:
  - name: duckduckgo
    disabled: false
  - name: brave
    disabled: false
  - name: startpage
    disabled: false
''')
    limiter = runtime / 'limiter.toml'
    if not limiter.exists():
        shutil.copyfile(source / 'searx/limiter.toml', limiter)
        content = limiter.read_text()
        begin = content.index('trusted_proxies = [')
        end = content.index(']', begin) + 1
        limiter.write_text(content[:begin] + 'trusted_proxies = []' + content[end:])
    print('Buscador instalado. Abra Iniciar.command para iniciar a Vio e o SearXNG.')


if __name__ == '__main__':
    install()
