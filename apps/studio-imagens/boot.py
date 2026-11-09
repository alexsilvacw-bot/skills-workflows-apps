import fcntl
import json
import subprocess
import time
import urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:62028/'

def healthy():
    try:
        with urllib.request.urlopen(URL + 'health', timeout=1) as r:
            return json.load(r).get('app') == 'sunburst-studio-v2'
    except Exception:
        return False

with (ROOT / '.startup.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    if not healthy():
        python = Path(__import__('sys').executable)
        with (ROOT / 'startup.log').open('a') as log:
            process = subprocess.Popen([str(python), str(ROOT / 'server.py')], cwd=ROOT,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=log,
                start_new_session=True, env={**__import__('os').environ, 'STUDIO_NO_BROWSER': '1'})
        for _ in range(100):
            if healthy():
                break
            if process.poll() is not None:
                raise SystemExit('Não foi possível iniciar o Studio. Consulte startup.log na pasta do aplicativo.')
            time.sleep(.1)
        else:
            process.terminate()
            raise SystemExit('O Studio não iniciou no tempo esperado.')
    print(URL, flush=True)
