"""Inicialização do SearXNG instalado localmente; sem downloads durante o uso."""
import os
from pathlib import Path
import subprocess
import time

from web_search import ready


def start_local(root):
    if ready() or os.environ.get('SEARXNG_URL'):
        return None
    runtime = Path(root) / 'runtime'
    python = runtime / 'venv/bin/python'
    source = runtime / 'searxng'
    settings = runtime / 'settings.yml'
    if not python.exists() or not settings.exists() or not source.exists():
        print('SearXNG local não instalado. Consulte README.md.', flush=True)
        return None
    env = {**os.environ, 'SEARXNG_SETTINGS_PATH': str(settings), 'PYTHONPATH': str(source)}
    with (runtime / 'searxng.log').open('a') as log:
        process = subprocess.Popen([str(python), '-m', 'searx.webapp'], cwd=source,
                                   env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(40):
        if process.poll() is not None or ready():
            return process
        time.sleep(.25)
    print('SearXNG ainda iniciando. Detalhes em runtime/searxng.log.', flush=True)
    return process


def stop_local(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
