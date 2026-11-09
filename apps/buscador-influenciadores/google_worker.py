"""Navegador automatizado do produto Vio. Entrada/saída JSONL local.

Usa exclusivamente o perfil isolado runtime/google-profile. Não lê o Chrome
pessoal, não usa proxies, stealth ou solucionadores de CAPTCHA.
"""
import json
from pathlib import Path
import queue
import signal
import sys
import threading
import time
from urllib.parse import urlencode, urlsplit, parse_qs

from collector import parse_publication, parse_instagram, profile_handle
from google_browser import extract_result_links, challenge_reason, normalized_instagram_url, BROWSER_RUNTIME, search_pages

ROOT = Path(__file__).resolve().parent
COMMANDS = queue.Queue()


def emit(event, **values):
    print(json.dumps({'event':event, **values},ensure_ascii=False),flush=True)


def read_commands():
    for line in sys.stdin:
        try:
            COMMANDS.put(json.loads(line).get('action'))
        except (ValueError, AttributeError):
            continue
    COMMANDS.put('cancel')


class Cancelled(Exception):
    pass


def check_cancel():
    try:
        while True:
            if COMMANDS.get_nowait()=='cancel':
                raise Cancelled()
    except queue.Empty:
        return


def pause(page, reason):
    page.bring_to_front()
    emit('attention',message=reason, url=page.url)
    # Mantém o mesmo documento aberto. Continuar não recarrega nem resolve desafios.
    deadline = time.monotonic()+1800
    while time.monotonic()<deadline:
        try:
            action=COMMANDS.get(timeout=.5)
        except queue.Empty:
            if page.is_closed():
                raise Cancelled()
            page.wait_for_timeout(50)
            continue
        if action=='cancel':
            raise Cancelled()
        if action=='resume':
            text=page.locator('body').inner_text(timeout=5000)
            if challenge_reason(page.url,text):
                emit('attention',message='A verificação ainda está presente. Conclua no navegador antes de continuar.',url=page.url)
            else:
                emit('status',message='Retomando a coleta no mesmo navegador…')
                return
    raise ValueError('A verificação ficou pendente por 30 minutos. Inicie novamente quando puder acompanhar.')


def navigate(page,url,label):
    check_cancel()
    emit('status',message=label)
    response=page.goto(url,wait_until='domcontentloaded',timeout=35000)
    page.locator('body').wait_for(state='attached',timeout=10000)
    reason=challenge_reason(page.url,page.locator('body').inner_text(timeout=10000),response.status if response else None)
    if reason:
        pause(page,reason)
    return page.content()


def main(payload):
    emit('status',message='Preparando o navegador automático…')
    from playwright.sync_api import sync_playwright
    threading.Thread(target=read_commands,daemon=True).start()
    queries=list(dict.fromkeys(payload['queries']))[:16]
    page_limit=max(1,min(10,int(payload.get('pages_per_query',10))))
    max_profiles=max(100,min(1000,int(payload.get('max_profiles',1000))))
    tasks=search_pages(queries,page_limit)
    visited_queries, exhausted, signatures=set(),set(),{}
    visited_pages=0
    seen_urls, seen_authors = set(), set()
    candidate_count=0
    emit('status',message='Abrindo navegador isolado da Vio…')
    with sync_playwright() as pw:
        context=pw.chromium.launch_persistent_context(str(BROWSER_RUNTIME/'google-profile'),headless=False,timeout=30000,
                                                     locale='pt-BR',viewport={'width':1280,'height':900})
        try:
            search_page=context.pages[0] if context.pages else context.new_page()
            content_page=context.new_page()
            search_page.on('dialog',lambda dialog:dialog.dismiss())
            content_page.on('dialog',lambda dialog:dialog.dismiss())
            for task in tasks:
                index,query,page_number=task['query_index'],task['query'],task['page']
                if query in exhausted: continue
                check_cancel()
                navigate(search_page,task['url'],f'Google · consulta {index+1}/{len(queries)} · página {page_number}/{page_limit}: {query}')
                # Rejeita somente consentimento opcional de cookies, se esse aviso aparecer.
                if urlsplit(search_page.url).hostname=='consent.google.com':
                    reject=search_page.get_by_role('button',name='Rejeitar tudo',exact=True)
                    if not reject.count(): reject=search_page.get_by_role('button',name='Reject all',exact=True)
                    if reject.count(): reject.click()
                    else: pause(search_page,'O Google está exibindo uma tela de consentimento. Escolha no navegador e continue.')
                search_page.locator('body').wait_for(state='attached')
                if urlsplit(search_page.url).hostname not in ('google.com','www.google.com','google.com.br','www.google.com.br'):
                    raise ValueError('A janela de pesquisa não está mais no Google. Inicie uma nova busca.')
                if not parse_qs(urlsplit(search_page.url).query).get('q'):
                    raise ValueError('A janela está no Google, mas a consulta não está mais exibida. Inicie uma nova busca.')
                try:
                    search_page.locator('#search, #rso, #topstuff').first.wait_for(state='attached',timeout=12000)
                except Exception:
                    reason=challenge_reason(search_page.url,search_page.locator('body').inner_text())
                    if reason: pause(search_page,reason)
                anchors=search_page.locator('a[href]').evaluate_all("""elements => elements.filter(a=>a.getClientRects().length).map(a=>({url:a.href,title:a.innerText}))""")
                hits=extract_result_links(anchors)
                visited_pages+=1
                visited_queries.add(query)
                signature=tuple(sorted(hit['title'] if hit['type']=='redirect' else hit['url'] for hit in hits))
                repeated=bool(hits and signature in signatures.setdefault(query,set()))
                signatures[query].add(signature)
                if repeated or not hits: exhausted.add(query)
                emit('source',source='Google · navegador Vio',query=query,page=page_number,found=len(hits),status='Página repetida; consulta encerrada' if repeated else ('Consultada' if hits else 'Sem destinos Instagram coletáveis; consulta encerrada'),url=search_page.url)
                if repeated or not hits:
                    search_page.wait_for_timeout(4000)
                    continue
                for hit in hits[:15]:
                    check_cancel()
                    if hit['url'] in seen_urls: continue
                    seen_urls.add(hit['url'])
                    try:
                        if hit['type']=='redirect':
                            navigate(content_page,hit['url'],'Seguindo resultado do Google para validar o destino…')
                            target,kind=normalized_instagram_url(content_page.url)
                            hit={**hit,'url':target,'type':kind}
                            if target in seen_urls: continue
                            seen_urls.add(target)
                        if hit['type']=='publication':
                            text=navigate(content_page,hit['url'],'Abrindo publicação para identificar o autor…')
                            candidate=parse_publication(text,hit['url'])
                        else:
                            handle=profile_handle(hit['url'])
                            candidate={'handle':handle,'name':handle,'tags':'','description':'Perfil encontrado nos resultados do Google.',
                                       'source_url':hit['url'],'source_type':'Resultado do Google no navegador Vio'}
                        handle=candidate['handle']
                        candidate['google_query']=query
                        # O mesmo autor pode trazer várias publicações; não perde a evidência.
                        if handle not in seen_authors:
                            profile_url=f'https://www.instagram.com/{handle}/'
                            text=navigate(content_page,profile_url,f'Lendo bio e seguidores de @{handle}…')
                            try:
                                candidate['profile_data']=parse_instagram(text,handle)
                            except ValueError as error:
                                candidate['profile_data']={'profile_fetch_status':'Indisponível','profile_fetch_error':str(error)}
                            seen_authors.add(handle)
                            candidate_count+=1
                        emit('candidate',candidate=candidate)
                    except Cancelled:
                        raise
                    except Exception as error:
                        emit('unavailable',url=hit['url'],message=str(error)[:350])
                    content_page.wait_for_timeout(1000)
                    if candidate_count>=max_profiles: break
                if candidate_count>=max_profiles: break
                search_page.wait_for_timeout(4000)
            emit('complete',candidates=candidate_count,queries=len(visited_queries),planned_queries=len(queries),unsearched_queries=len(queries)-len(visited_queries),pages=visited_pages,planned_pages=len(tasks),unsearched_pages=len(tasks)-visited_pages,message='Consultas ao Google concluídas.')
        finally:
            context.close()


if __name__=='__main__':
    signal.signal(signal.SIGTERM,lambda *_: (_ for _ in ()).throw(Cancelled()))
    try:
        payload=json.loads(sys.stdin.readline())
        main(payload)
    except Cancelled:
        emit('cancelled',message='Busca cancelada. Os perfis já coletados foram preservados.')
    except Exception as error:
        if 'has been closed' in str(error):
            emit('cancelled',message='O navegador da Vio foi fechado. Dados coletados foram preservados; inicie outra execução para continuar.')
        else:
            emit('error',message=str(error)[:600])
