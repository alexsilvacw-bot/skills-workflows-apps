"""Instala o navegador oficial do Playwright para a automação solicitada."""
import os
from pathlib import Path
import subprocess
import sys
import shutil
from google_browser import BROWSER_RUNTIME

ROOT=Path(__file__).resolve().parent


def install():
    runtime=BROWSER_RUNTIME
    runtime.mkdir(parents=True,exist_ok=True)
    python=runtime/'venv/bin/python'
    if not python.exists(): subprocess.run([sys.executable,'-m','venv',str(runtime/'venv')],check=True)
    subprocess.run([str(python),'-m','pip','install','playwright==1.64.1'],check=True)
    env={**os.environ,'PLAYWRIGHT_BROWSERS_PATH':str(runtime/'google-browser-binaries')}
    subprocess.run([str(python),'-m','playwright','install','chromium'],env=env,check=True)
    old_profile=ROOT/'runtime/google-profile'
    # A sessão exige cookies e configuração, não o cache de páginas (que pode
    # estar apenas na nuvem). Não substitui uma sessão já migrada e usada.
    if old_profile.exists() and not (runtime/'google-profile/.migrated').exists():
        profile=runtime/'google-profile'
        profile.mkdir(parents=True,exist_ok=True)
        for relative in ('Local State','Default/Cookies','Default/Cookies-journal','Default/Preferences','Default/Secure Preferences','Default/Network/Cookies','Default/Network/Cookies-journal'):
            source=old_profile/relative
            if source.is_file():
                target=profile/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,target)
        (profile/'.migrated').write_text('Sessão isolada Vio migrada; caches de páginas não são necessários.\n')
    print('Navegador instalado. Reinicie a Vio e escolha Google automático.')


if __name__=='__main__': install()
