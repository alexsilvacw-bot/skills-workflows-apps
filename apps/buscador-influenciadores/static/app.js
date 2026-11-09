const $ = id => document.getElementById(id);
let all = [], shown = [], config, favoritesOnly = false, editing = null, candidates = [], toastTimer;
let selectedHandles;
try { const stored = JSON.parse(localStorage.getItem('aggeo-crm-selection') || '[]'); selectedHandles = new Set(Array.isArray(stored) ? stored.filter(h=>typeof h==='string') : []); }
catch { selectedHandles = new Set(); }
let exportingCRM = false, currentView = 'discovery', searchResults = []; 
function updateSelection() {
  const count = selectedHandles.size;
  $('selectedCount').textContent = `${count} ${count===1?'perfil selecionado':'perfis selecionados'}`;
  $('exportCRM').disabled = count===0 || exportingCRM;
  $('clearSelection').disabled = count===0;
  $('selectVisible').disabled = shown.length===0;
  try { localStorage.setItem('aggeo-crm-selection',JSON.stringify([...selectedHandles])); } catch {}
}
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const profileUrl = p => 'https://www.instagram.com/' + encodeURIComponent(p.handle) + '/';
const humanDate = value => value ? value.split('-').reverse().join('/') : 'Não informada';
function toast(message) { $('toast').textContent = message; $('toast').classList.remove('hidden'); clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').classList.add('hidden'), 9000); }
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'A operação falhou.');
  return body;
}
function params() {
  const p = new URLSearchParams({q:$('query').value,tag:$('tag').value,status:$('status').value});
  if (favoritesOnly) p.set('favorites','1');
  if(currentView==='all') p.set('saved','1');
  return p;
}
function searchCriteria() {
  const p = new URLSearchParams();
  for(const [key,id] of [['min_followers','minFollowers'],['max_followers','maxFollowers'],['region','regionFilter'],['category','categoryFilter'],['keywords','keywordsFilter'],['scope','contentScope'],['match','matchMode'],['hashtags','hashtagsFilter']]) p.set(key,$(id).value);
  for(const [key,id] of [['include_unknown_region','includeUnknownRegion'],['include_unknown_followers','includeUnknownFollowers'],['exclude_companies','excludeCompanies']]) p.set(key,$(id).checked?'1':'0');
  return Object.fromEntries(p);
}
function collectionHTML(p) {
  const when = p.profile_collected_at ? new Date(p.profile_collected_at).toLocaleString('pt-BR') : '';
  const count = p.followers_display ? esc(p.followers_display) : 'Não disponível';
  return `<div class="public-data"><div><span>Seguidores</span><strong>${count}</strong><small>${esc(p.followers_precision || 'Ainda não coletado')}</small></div><div><span>Leitura do perfil</span><strong class="fetch-state">${esc(p.profile_fetch_status || 'Não consultado')}</strong><small>${when ? esc(when) : 'Aguardando coleta'}</small></div></div><div class="bio"><span class="bio-label">BIO DO INSTAGRAM</span><p>${esc(p.bio || 'Bio não disponível nesta coleta.')}</p></div>${p.profile_fetch_status === 'Indisponível' ? `<p class="hint">${esc(p.profile_fetch_error || 'Perfil não acessível.')} ${when ? 'Dados exibidos são da última coleta disponível.' : ''}</p>` : ''}${p.profile_data_source ? `<a class="data-source" href="${esc(p.profile_data_source)}" target="_blank" rel="noopener noreferrer">Fonte dos dados: Instagram público ↗</a>` : ''}`;
}
function postsHTML(p) {
  if(!p.posts_count)return '';
  return `<details class="post-evidence"><summary>Ver publicações disponíveis (${p.posts_count})</summary>${p.posts.map(post=>`<div><p>${esc(post.text.slice(0,1200))}</p><a href="${esc(post.source_url)}" target="_blank" rel="noopener noreferrer">Ver publicação de origem ↗</a><small>${esc(post.source_type)} · ${esc(post.collected_at)}</small></div>`).join('')}</details>`;
}
function renderCards(items) {
  $('resultCount').textContent = `${items.length} ${items.length === 1 ? 'perfil' : 'perfis'}`;
  $('cards').innerHTML = items.length ? items.map(p => `<article class="card ${selectedHandles.has(p.handle)?'export-selected':''}"><label class="export-choice"><input type="checkbox" data-select="${esc(p.handle)}" aria-label="Selecionar @${esc(p.handle)} para exportar" ${selectedHandles.has(p.handle)?'checked':''}> Selecionar para CRM</label><div class="card-top"><div class="avatar" aria-hidden="true">${esc(p.name.slice(0,1))}</div><div class="identity"><h3>${esc(p.name)}</h3><a class="handle" target="_blank" rel="noopener noreferrer" href="${profileUrl(p)}">@${esc(p.handle)}</a></div><button class="star ${p.favorite?'selected':''}" data-favorite="${esc(p.handle)}" aria-label="${p.favorite?'Remover dos':'Adicionar aos'} favoritos" aria-pressed="${p.favorite}">${p.favorite?'★':'☆'}</button></div><p class="notice">${esc(p.creator_evidence || '')}</p>${collectionHTML(p)}${postsHTML(p)}<p>${esc(p.description || 'Descrição ainda não registrada. Confira o perfil e acrescente uma fonte.')}</p><div class="tags">${p.tags.split(',').filter(Boolean).map(t=>`<span class="tag">${esc(t.trim())}</span>`).join('')}</div><div class="metadata">${esc(p.kind)} · ${esc(p.region_info?.text || 'Região não identificada')}<br>${esc(p.region_info?.source || '')}<br>${esc(p.generic_categories?.join(' · ') || 'Categoria não identificada')}<br><span title="${esc(p.categories_source || '')}">${esc(p.categories_source || '')}</span><br>${esc(p.company_info?.reason || '')}<br>Publicações disponíveis: ${p.posts_count || 0} · ${esc(p.posts_fetch_status || 'Ainda não coletadas')}<br>Fonte: <a href="${esc(p.source_url)}" target="_blank" rel="noopener noreferrer">${esc(p.source_type)} ↗</a><br>Consultada em ${humanDate(p.observed_at)}</div><div class="card-bottom"><span class="badge">${esc(p.status)}</span><a href="${profileUrl(p)}" target="_blank" rel="noopener noreferrer">Instagram ↗</a><button class="plain" data-save="${esc(p.handle)}">${p.saved?'Remover dos salvos':'Salvar perfil'}</button><button class="plain" data-edit="${esc(p.handle)}">Ver / editar</button></div></article>`).join('') : `<div class="empty"><strong>Nenhum perfil encontrado nesta seleção.</strong><p>${currentView==='all'?'Clique em Salvar perfil nos resultados ou no histórico para guardar os perfis escolhidos.':'Defina os critérios e inicie uma busca. Confira também os motivos de rejeição no resumo.'}</p></div>`;
}
let loadVersion = 0;
async function load() {
  const version = ++loadVersion;
  const p = params();
  const [base, filtered] = await Promise.all([api('/api/profiles'), api('/api/profiles?'+p)]);
  if (version !== loadVersion) return;
  all = base;
  const latest = new Map(all.map(p=>[p.handle,p]));
  shown = currentView === 'discovery' ? searchResults.map(p=>latest.get(p.handle) || p) : filtered;
  const known = new Set(all.map(p=>p.handle));
  selectedHandles = new Set([...selectedHandles].filter(h=>known.has(h)));
  $('total').textContent = all.filter(p=>p.saved).length;
  $('favorites').textContent = all.filter(p=>p.favorite).length;
  $('pending').textContent = all.length;
  const selected = $('tag').value;
  $('tag').innerHTML = '<option value="">Todos os temas</option>' + [...new Set(all.flatMap(p=>p.tags.split(',').map(t=>t.trim()).filter(Boolean)))].sort().map(t=>`<option value="${esc(t)}">${esc(t)}</option>`).join('');
  $('tag').value = selected;
  $('exportButton').href = '/api/export.csv?' + p;
  renderCards(shown);
  updateSelection();
}
function openEditor(p = {}) {
  editing = p.handle || null;
  const form = $('editForm'); form.reset();
  const values = {kind:'Não classificado',status:'A revisar',source_type:'Inserção manual',observed_at:config.today,...p};
  for (const field of form.elements) if (field.name) field.value = values[field.name] || '';
  form.elements.handle.readOnly = !!editing;
  form.elements.observed_at.max = config.today;
  $('editorTitle').textContent = editing ? 'Revisar perfil' : 'Adicionar perfil';
  $('collectedDetails').innerHTML = editing ? collectionHTML(p) : '';
  $('editor').showModal();
}
async function guarded(action) { try { await action(); } catch(error) { toast(error.message); } }
$('filterForm').addEventListener('submit', e=>{e.preventDefault();guarded(load);});
for (const id of ['tag','status']) $(id).addEventListener('change',()=>guarded(load));
document.querySelector('.chips').addEventListener('click', e=>{ const button=e.target.closest('button'); if (!button) return; $('query').value=button.dataset.query || '';
  if(button.id==='clear') {
    for(const id of ['tag','status']) $(id).value='';
  }
  guarded(load); });
function view(mode) {
  currentView=mode;
  favoritesOnly=mode==='favorites';
  $('filterForm').classList.toggle('hidden',mode==='discovery');
  document.querySelector('.chips').classList.toggle('hidden',mode==='discovery');
  $('exportButton').classList.toggle('hidden',mode==='discovery');
  $('resultsNotice').textContent=mode==='discovery' ? 'Resultados exclusivos da última descoberta, após conferir os critérios nos dados disponíveis. Selecione os perfis para exportar ao CRM. O histórico completo fica em Histórico de candidatos.' : mode==='history' ? 'Histórico acumulado de todas as coletas e testes. Inclui empresas, rejeitados e perfis sem dados. Estar aqui não significa ter sido aprovado nem salvo por você.' : 'Perfis guardados por uma ação sua. A coleta automática não preenche esta lista.';
  $('discovery').classList.toggle('hidden',mode!=='discovery');
  for (const [id,m] of [['allView','all'],['favView','favorites'],['historyView','history'],['discoverView','discovery']]) $(id).classList.toggle('active',mode===m);
  $('listTitle').textContent = mode==='discovery' ? 'Resultados desta busca' : favoritesOnly ? 'Seus favoritos' : mode==='history' ? 'Histórico de candidatos' : 'Salvos por você';
  guarded(load);
}
$('allView').onclick=()=>view('all'); $('historyView').onclick=()=>view('history'); $('favView').onclick=()=>view('favorites'); $('discoverView').onclick=()=>view('discovery');
$('newButton').onclick=()=>openEditor();
$('closeEditor').onclick=$('cancelEditor').onclick=()=>$('editor').close();
$('cards').addEventListener('change',e=>{
  const input=e.target.closest('[data-select]'); if(!input)return;
  if(input.checked) selectedHandles.add(input.dataset.select); else selectedHandles.delete(input.dataset.select);
  input.closest('.card').classList.toggle('export-selected',input.checked);
  updateSelection();
});
$('selectVisible').onclick=()=>{shown.forEach(p=>selectedHandles.add(p.handle));renderCards(shown);updateSelection();};
$('clearSelection').onclick=()=>{selectedHandles.clear();renderCards(shown);updateSelection();};
$('exportCRM').onclick=()=>guarded(async()=>{
  if(!selectedHandles.size)return;
  exportingCRM=true;updateSelection();
  try {
    const handles=[...selectedHandles];
    const response=await fetch('/api/export-crm.csv',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({handles})});
    if(!response.ok){const error=await response.json();throw new Error(error.error || 'Não foi possível exportar.');}
    const url=URL.createObjectURL(await response.blob());
    const link=document.createElement('a');link.href=url;link.download=`vio-crm-${config.today}.csv`;
    document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
    toast(`Tabela CRM exportada com ${handles.length} perfis. Preencha os contatos no arquivo.`);
  } finally {exportingCRM=false;updateSelection();}
});
$('cards').addEventListener('click', e=>guarded(async()=>{
  const favorite=e.target.closest('[data-favorite]'), edit=e.target.closest('[data-edit]');
  if(favorite) { const p=all.find(p=>p.handle===favorite.dataset.favorite); await api('/api/profiles',{handle:p.handle,favorite:!p.favorite,...(!p.favorite?{saved:true}:{})}); await load(); }
  const save=e.target.closest('[data-save]');
  if(save) {const p=all.find(p=>p.handle===save.dataset.save); await api('/api/profiles',{handle:p.handle,saved:!p.saved}); await load();}
  if(edit) openEditor(all.find(p=>p.handle===edit.dataset.edit));
}));
$('editForm').addEventListener('submit', e=>{e.preventDefault();guarded(async()=>{const data=Object.fromEntries(new FormData(e.target));if(!editing)data.saved=true;await api('/api/profiles',data);$('editor').close();await load();toast('Dados do perfil atualizados. Use Salvar perfil para guardá-lo na sua lista.');});});
$('importButton').onclick=()=>$('importer').showModal();
$('cancelImport').onclick=()=>$('importer').close();
$('importForm').addEventListener('submit',e=>{e.preventDefault();guarded(async()=>{const data=JSON.parse($('importData').value);const result=await api('/api/import',{items:data});$('importer').close();await load();toast(`${result.imported} registros importados.`);});});
async function previewPlan() {
  const plan=await api('/api/search-plan',{q:$('topic').value.trim() || 'criadores de conteúdo',criteria:searchCriteria()});
  $('queryPlan').classList.remove('hidden');
  $('queryPlan').innerHTML='<strong>Consultas para descobrir publicações e perfis</strong>'+($('discoveryProvider').value==='google'?plan.google_queries:plan.queries).map(q=>'<p><code>'+esc(q)+'</code></p>').join('')+'<strong>Buscar publicações no Google</strong>'+plan.google_links.map(link=>'<p><a href="'+esc(link.url)+'" target="_blank" rel="noopener noreferrer">'+esc(link.query)+' ↗</a></p>').join('')+'<p>'+esc(plan.verification)+'</p><p>A Vio abre resultados de perfis e publicações e tenta identificar os autores nos dados públicos. Google automático consulta até 10 páginas por busca, com limite de 1.000 autores distintos. O SearXNG consulta até duas páginas por busca e lê até 100 autores. A coleta para diante de verificação, ausência de destinos coletáveis ou repetição de página. Os links permitem conferir as consultas, sem exigir copiar resultados.</p>';
  $('assistedLink').href=plan.google_links[0]?.url || 'https://www.google.com/search?'+new URLSearchParams({q:plan.queries[0]});
  return plan;
}
$('previewQueries').onclick=()=>guarded(previewPlan);
$('discoveryForm').addEventListener('input',()=>{ $('queryPlan').classList.add('hidden'); });
$('assistedLink').addEventListener('click',e=>{
  e.preventDefault();guarded(async()=>{const plan=await previewPlan();window.open(plan.google_links[0]?.url || 'https://www.google.com/search?'+new URLSearchParams({q:plan.queries[0]}),'_blank','noopener,noreferrer');});
});
let polling = false, currentJobId = null;
function displayJob(job) {
  $('jobProgress').classList.remove('hidden');
  $('jobProgress').textContent = job.message + (job.total ? ` · ${job.done}/${job.total}` : '');
  currentJobId=job.id;
  const active=['running','needs_attention'].includes(job.state);
  $('browserActions').classList.toggle('hidden',job.state!=='needs_attention');
  $('cancelGoogle').classList.toggle('hidden',job.provider!=='google' || !active);
  $('runDiscovery').disabled = active;
  $('refreshProfiles').disabled = active;
  $('collectLinks').disabled = active;
  const sources = job.sources.map(s=>`${s.source}: ${s.status} (${s.found} perfis${s.publication_attempts?', '+s.publication_attempts+' publicações consultadas':''}${s.page?', página '+s.page:''})${s.errors?.length?' · avisos: '+s.errors.map(e=>e.join(': ')).join('; '):''}`).join(' · ');
  $('discoveryResults').innerHTML = sources ? `<p class="hint">${esc(sources)}</p>` : '';
  if (job.state === 'done') {
    if(job.executed_pages!==undefined && job.executed_pages!==null) $('discoveryResults').innerHTML+='<p><strong>Páginas do Google consultadas: '+job.executed_pages+' de até '+job.planned_pages+'.</strong></p>';
    $('discoveryResults').innerHTML += `<p><strong>Perfis compatíveis com os critérios: ${job.items.length}.</strong> Processados: ${job.done || 0}. Com bio e seguidores: ${job.collected || 0}. ${job.unavailable || 0} indisponíveis nesta tentativa. ${job.cached_count || 0} reutilizados do cache de hoje.</p><p class="hint">${job.rejected || 0} candidatos não atenderam aos critérios ou não tinham dados suficientes para confirmá-los. As consultas usam os critérios enviados no início da busca. A fonte escolhida consulta a web indexada; não há restrição a fontes do agro. Perfis e publicações não indexados podem ficar de fora. Autoria de conteúdo não comprova, sozinha, influência ou adequação à campanha.</p>`;
    if(job.partial) $('discoveryResults').innerHTML += '<p class="notice"><strong>Cobertura parcial.</strong> Há fontes, publicações ou consultas que não puderam ser processadas nesta execução. Confira os avisos; estes resultados não representam todos os perfis compatíveis.</p>';
    if(job.collection_errors?.length) $('discoveryResults').innerHTML+='<details><summary>Publicações ou perfis indisponíveis ('+job.collection_errors.length+')</summary><ul>'+job.collection_errors.map(e=>'<li>'+esc(e.url || '')+': '+esc(e.reason || '')+'</li>').join('')+'</ul></details>';
    const labels=config.rejection_labels || {};
    const counts=Object.entries(job.rejection_counts || {});
    $('discoveryResults').innerHTML += `<p><strong>Funil da busca:</strong> ${job.found || 0} candidatos distintos → ${job.done || 0} lidos → ${job.items.length} correspondências. ${job.unprocessed || 0} candidatos ainda não processados por limite da execução.</p>${counts.length?'<details><summary>Por que outros candidatos ficaram de fora?</summary><ul>'+counts.map(([code,n])=>'<li>'+esc(labels[code] || code)+': '+n+'</li>').join('')+'</ul><p class="hint">Um candidato pode ter mais de um motivo de rejeição.</p></details>':''}`;

  }
}
async function pollJob(id) {
  if (polling) return;
  polling = true;
  try {
    while (true) {
      const job = await api('/api/jobs/'+id);
      displayJob(job);
      if(job.mode!=='refresh' && currentView==='discovery' && job.items?.length) {
        searchResults=job.items; shown=job.items;
        const merged=new Map(all.map(p=>[p.handle,p]));job.items.forEach(p=>merged.set(p.handle,p));all=[...merged.values()];
        renderCards(shown); updateSelection();
      }
      if (!['running','needs_attention'].includes(job.state)) {
        localStorage.removeItem('aggeo-active-job');
        if(job.mode!=='refresh') {searchResults=job.items || []; view('discovery');}
        await load();
        toast(job.message);
        break;
      }
      await new Promise(resolve=>setTimeout(resolve,1200));
    }
  } catch(error) {
    localStorage.removeItem('aggeo-active-job');
    $('runDiscovery').disabled=false; $('refreshProfiles').disabled=false;
    throw error;
  } finally { polling = false; }
}
async function beginCollection(mode) {
  const q = $('topic').value.trim() || 'criadores de conteúdo';
  if(mode==='sources') {await previewPlan(); searchResults=[]; view('discovery');}
  const job = await api('/api/discover',{q,mode,provider:$('discoveryProvider').value,criteria:mode==='sources'?searchCriteria():{}});
  localStorage.setItem('aggeo-active-job',job.id);
  history.replaceState(null,'','?job='+encodeURIComponent(job.id));
  displayJob(job);
  await pollJob(job.id);
}
$('linksForm').addEventListener('submit',e=>{e.preventDefault();guarded(async()=>{
  const urls=$('publicationLinks').value.trim().split(/\s+/);
  const job=await api('/api/collect-links',{urls,q:$('topic').value.trim() || 'Conteúdo encontrado',criteria:searchCriteria()});
  searchResults=[];view('discovery');localStorage.setItem('aggeo-active-job',job.id);displayJob(job);await pollJob(job.id);
});});
$('resumeGoogle').onclick=()=>guarded(()=>api('/api/google-control',{id:currentJobId,action:'resume'}));
$('cancelGoogle').onclick=()=>guarded(()=>api('/api/google-control',{id:currentJobId,action:'cancel'}));
$('discoveryForm').addEventListener('submit',e=>{e.preventDefault();guarded(()=>beginCollection('sources'));});
$('refreshProfiles').onclick=()=>guarded(()=>beginCollection('refresh'));
guarded(async()=>{
  config=await api('/api/config');
  $('categoryFilter').insertAdjacentHTML('beforeend',[...config.categories,'Não identificada'].map(s=>`<option value="${esc(s)}">${esc(s)}</option>`).join(''));
  $('categoryOptions').innerHTML=config.categories.map(c=>`<option value="${esc(c)}"></option>`).join('');
  $('regionOptions').innerHTML=[...new Set(['Brasil',...Object.values(config.states).map(s=>s[1]),...Object.entries(config.states).flatMap(([code,s])=>[code,s[0]])])].map(s=>`<option value="${esc(s)}"></option>`).join('');
  for(const [id,values] of [['status',config.statuses],['statusInput',config.statuses],['kindInput',config.kinds]]) $(id).insertAdjacentHTML('beforeend',values.map(s=>`<option value="${esc(s)}">${esc(s)}</option>`).join(''));
  $('provider').textContent=config.google_ready?'Pronto':'Indisponível';
  $('providerCaption').textContent='Google automático · navegador isolado';
  $('discoveryHelp').textContent=config.google_ready?'O navegador da Vio faz as consultas e abre publicações e perfis automaticamente. Se houver CAPTCHA ou login obrigatório, a busca pausa e pede sua intervenção. Não utiliza seu navegador pessoal nem API paga.':'Navegador automático não instalado. Execute python3 install_google.py e reinicie a Vio.';
  if(config.brave_ready) $('discoveryProvider').insertAdjacentHTML('beforeend','<option value="brave">Fontes setoriais + Brave API · conforme seu plano</option>');
  $('runDiscovery').disabled=false;
  view('discovery');
  await load();
  const activeJob=new URLSearchParams(window.location.search).get('job') || localStorage.getItem('aggeo-active-job');
  if(activeJob) {
    const job=await api('/api/jobs/'+encodeURIComponent(activeJob));
    $('topic').value=job.topic || '';
    const criteria=job.plan?.criteria || {};
    for(const [key,id] of [['min_followers','minFollowers'],['max_followers','maxFollowers'],['region','regionFilter'],['category','categoryFilter'],['keywords','keywordsFilter'],['scope','contentScope'],['match','matchMode'],['hashtags','hashtagsFilter']]) if(criteria[key]!==undefined) $(id).value=criteria[key] ?? '';
    for(const [key,id] of [['include_unknown_region','includeUnknownRegion'],['include_unknown_followers','includeUnknownFollowers'],['exclude_companies','excludeCompanies']]) $(id).checked=!!criteria[key];
    await pollJob(activeJob);
  }
});
