const el = id => document.getElementById(id);
let token = '', configured = false, busy = false, mode = 'url', result = null, savedFolder = "";
function message(id, text, error = false) { el(id).textContent = text; el(id).classList.toggle('error', error); }
function resetResult() { result = null; savedFolder = ""; el('download').disabled = true; el('result').hidden = true; el('empty').hidden = false; }
function controls() { el('extract').disabled = busy || !configured; el('extract').textContent = busy ? 'Extraindo…' : 'Extrair vaga'; for (const id of ['url','text','mode-url','mode-text','save-key','key']) el(id).disabled = busy; }
async function post(path, data) {
  const response = await fetch(path, {method:'POST',headers:{'Content-Type':'application/json','X-Local-Token':token},body:JSON.stringify(data)});
  const body = await response.json(); if (!response.ok) throw new Error(body.erro || 'Não foi possível concluir.');
  if (path === '/api/extract') savedFolder = response.headers.get('X-Candidatura-Pasta') || '';
  return body;
}
el('settings').onclick = () => { el('config').hidden = !el('config').hidden; if (!el('config').hidden) el('key').focus(); };
el('key-form').onsubmit = async event => {
  event.preventDefault(); el('save-key').disabled = true;
  try { await post('/api/key', {key:el('key').value}); el('key').value = ''; configured = true; el('settings').textContent = 'Chave configurada'; message('key-message','Chave salva neste Mac. Ela será reutilizada nas próximas extrações.'); message('status','Pronto para extrair.'); }
  catch(error) { message('key-message', error.message, true); }
  finally { controls(); }
};
for (const chosen of ['url','text']) el('mode-'+chosen).onclick = () => {
  mode = chosen; resetResult(); el('url-area').hidden = mode !== 'url'; el('text-area').hidden = mode !== 'text';
  for (const item of ['url','text']) { el('mode-'+item).classList.toggle('selected',item === mode); el('mode-'+item).setAttribute('aria-pressed',String(item === mode)); el(item).required = item === mode; }
  message('status', configured ? 'Pronto para extrair.' : 'Configure sua chave para começar.'); el(mode).focus();
};
for (const id of ['url','text']) el(id).addEventListener('input', resetResult);
function list(id, items) { el(id).replaceChildren(); for (const text of items.length ? items : ['Não informado no anúncio.']) { const li = document.createElement('li'); li.textContent = text; el(id).append(li); } }
el('extract-form').onsubmit = async event => {
  event.preventDefault(); if (busy || !configured) return; busy = true; resetResult(); controls();
  message('status', mode === 'url' ? 'Lendo o anúncio e organizando os requisitos. Isso pode levar até dois minutos.' : 'Organizando os requisitos. Aguarde a análise.');
  try {
    result = await post('/api/extract', mode === 'url' ? {url:el('url').value} : {text:el('text').value});
    el('company').textContent = result.nome_empresa || 'Empresa não informada'; el('role').textContent = result.nome_vaga || 'Cargo não informado'; el('language').textContent = result.idioma_cv || 'idioma a confirmar';
    el('ats').textContent = result.ats || 'desconhecido';
    list('required',result.requisitos_obrigatorios); list('preferred',result.requisitos_desejaveis); list('skills',result.competencias); list('tools',result.ferramentas); el('json').textContent = JSON.stringify(result,null,2);
    el('empty').hidden = true; el('result').hidden = false; el('download').disabled = false; message('status', savedFolder ? 'Extração concluída. JSON salvo em ' + savedFolder + '/requisitos-vaga.json. Confira os dados.' : 'Extração concluída. Confira os dados.');
  } catch(error) { message('status', error.message === 'Failed to fetch' ? 'A interface perdeu a conexão. Reabra o extrator e tente novamente.' : error.message, true); }
  finally { busy = false; controls(); }
};
el('download').onclick = () => {
  if (!result) return;
  const blob = new Blob([JSON.stringify(result,null,2)+'\n'],{type:'application/json;charset=utf-8'});
  const url = URL.createObjectURL(blob), link = document.createElement('a');
  link.href=url; link.download='requisitos-vaga.json'; document.body.append(link); link.click(); link.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000);
};
(async () => { try { const response = await fetch('/api/status'); if (!response.ok) throw new Error(); const data = await response.json(); token=data.token; configured=data.configured; el('config').hidden=configured; el('settings').textContent=configured?'Chave configurada':'Configurar chave'; message('status',configured?'Pronto para extrair.':'Configure sua chave para começar.'); controls(); } catch { message('status','Não foi possível iniciar. Reabra o extrator.',true); } })();
