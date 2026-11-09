"""Regras explícitas, revisáveis e sem inferir audiência a partir do criador."""
import re
import unicodedata


def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value)) if not unicodedata.combining(c)).lower()


STATES = {
    'AC': ('Acre', 'Norte'), 'AL': ('Alagoas', 'Nordeste'), 'AP': ('Amapá', 'Norte'),
    'AM': ('Amazonas', 'Norte'), 'BA': ('Bahia', 'Nordeste'), 'CE': ('Ceará', 'Nordeste'),
    'DF': ('Distrito Federal', 'Centro-Oeste'), 'ES': ('Espírito Santo', 'Sudeste'),
    'GO': ('Goiás', 'Centro-Oeste'), 'MA': ('Maranhão', 'Nordeste'), 'MT': ('Mato Grosso', 'Centro-Oeste'),
    'MS': ('Mato Grosso do Sul', 'Centro-Oeste'), 'MG': ('Minas Gerais', 'Sudeste'),
    'PA': ('Pará', 'Norte'), 'PB': ('Paraíba', 'Nordeste'), 'PR': ('Paraná', 'Sul'),
    'PE': ('Pernambuco', 'Nordeste'), 'PI': ('Piauí', 'Nordeste'), 'RJ': ('Rio de Janeiro', 'Sudeste'),
    'RN': ('Rio Grande do Norte', 'Nordeste'), 'RS': ('Rio Grande do Sul', 'Sul'),
    'RO': ('Rondônia', 'Norte'), 'RR': ('Roraima', 'Norte'), 'SC': ('Santa Catarina', 'Sul'),
    'SP': ('São Paulo', 'Sudeste'), 'SE': ('Sergipe', 'Nordeste'), 'TO': ('Tocantins', 'Norte'),
}
CATEGORY_TERMS = {
    'Agro': ['agro', 'agrônomo', 'agrônoma', 'agronomia', 'agricultura', 'agrícola', 'agrícolas',
             'agricola', 'agricolas', 'agriculture', 'agricultural', 'agricultor', 'agricultora',
             'agricultores', 'agricultoras', 'rural', 'produtor rural', 'produtora rural', 'pecuária',
             'lavoura', 'cafeicultura', 'pulverização agrícola'],
    'Tecnologia': ['tecnologia', 'drones', 'drone', 'software', 'programação', 'geoprocessamento', 'inteligência artificial'],
    'Educação': ['professor', 'professora', 'cursos', 'ensino', 'educação', 'mentoria', 'treinamentos'],
    'Beleza': ['beleza', 'maquiagem', 'cosméticos', 'skincare', 'cabeleireiro', 'cabeleireira'],
    'Moda': ['moda', 'fashion', 'estilista', 'looks'],
    'Saúde e bem-estar': ['saúde', 'médico', 'médica', 'nutricionista', 'psicologia', 'fisioterapia'],
    'Esportes e fitness': ['fitness', 'esportes', 'atleta', 'personal trainer', 'musculação', 'corrida'],
    'Gastronomia': ['gastronomia', 'culinária', 'receitas', 'chef', 'restaurante'],
    'Viagens': ['viagens', 'turismo', 'viajante', 'travel'],
    'Negócios': ['negócios', 'empreendedor', 'empreendedora', 'marketing', 'empresário', 'empresária'],
    'Entretenimento': ['humor', 'comediante', 'música', 'cantor', 'cantora', 'entretenimento'],
    'Casa e decoração': ['decoração', 'arquitetura', 'interiores', 'reforma'],
    'Pets': ['pets', 'pet', 'veterinária', 'veterinário', 'cães', 'gatos'],
    'Automóveis': ['automóveis', 'automotivo', 'motociclismo', 'carros'],
    'Meio ambiente': ['meio ambiente', 'sustentabilidade', 'ecologia', 'ambiental'],
}
COMPANY_TERMS = ['ltda', 'distribuidora', 'distribuidor', 'loja', 'comércio', 'indústria', 'equipamentos',
                 'soluções', 'cursos', 'treinamentos', 'academy', 'escola', 'agência', 'consultoria',
                 'imobiliária', 'clínica', 'restaurante', 'construtora', 'associação', 'cooperativa', 'cases',
                 'concessionária', 'concessionario', 'prefeitura', 'sindicato',
                 'universidade', 'faculdade', 'instituto', 'portal', 'plataforma', 'ead', 'importadora', 'pulverizações']


def contains(text, term):
    return bool(re.search(r'(?<!\w)' + re.escape(normalize(term)) + r'(?!\w)', normalize(text)))


def location_info(record):
    manual = record.get('location', '').strip()
    # Só considera linhas com sinal de localização ou estado/UF explícito.
    lines = [line.strip() for line in record.get('bio', '').splitlines() if '📍' in line or '📌' in line]
    if not lines:
        lines = [line.strip() for line in record.get('bio', '').splitlines()
                 if any((bool(re.search(r'\bPará\b', line, re.I)) if name == 'Pará' else contains(line, name)) for name, _ in STATES.values())
                 or re.search(r'(?:[,/|–-]\s*|^|\b(?:de|do|em)\s+)(?:' + '|'.join(STATES) + r')\b', line)]
    text = manual or ' | '.join(lines)
    codes = []
    # Nomes longos primeiro para não interpretar Mato Grosso do Sul como Mato Grosso.
    remaining = normalize(text)
    for code, (name, _) in sorted(STATES.items(), key=lambda item: -len(item[1][0])):
        if contains(remaining, name) and (name != 'Pará' or manual or re.search(r'\bPará\b', text, re.I)):
            codes.append(code)
            remaining = remaining.replace(normalize(name), '')
    codes.extend(code for code in STATES if re.search(r'(?<![A-Za-z])' + code + r'(?![A-Za-z])', text) and code not in codes)
    return {'text': text, 'states': codes, 'regions': sorted({STATES[c][1] for c in codes}),
            'known': bool(text), 'source': 'Local registrado' if manual else ('Indicação na bio; revisar' if text else 'Não identificada')}


def company_info(record):
    kind = record.get('kind', 'Não classificado')
    if kind in ('Empresa', 'Escola / concorrente', 'Instituição'):
        return {'is_company': True, 'reason': 'Classificação registrada: ' + kind}
    if kind == 'Criador':
        return {'is_company': False, 'reason': 'Classificação registrada: Criador'}
    name = record.get('public_name') or record.get('name', '')
    terms = [term for term in COMPANY_TERMS if contains(name, term)]
    bio = normalize(record.get('bio', ''))
    explicit = [phrase for phrase in ('somos a distribuidora', 'somos uma empresa', 'maior empresa',
                'atacado e varejo', 'concessionaria oficial', 'nossas lojas', 'com lojas no',
                'revenda autorizada', 'revenda oficial', 'revendedora oficial', 'revendedor autorizado',
                'revendedora autorizada', 'revendedor oficial', 'distribuidor oficial',
                'maior revenda', 'loja fisica', 'loja autorizada', 'tienda oficial',
                'dealer oficial', 'dealer autorizado', 'fabricacao de aeronaves',
                'venta de drones', 'venda drones agricola', 'venda de drones agricolas',
                'empresa especializada', 'escola de drones', 'a escola que',
                'revenda e assistencia', 'recrutamento e selecao',
                'formacao manutencao e vendas', 'sindicato nacional', 'dealer de drones',
                'banco de talentos', 'revistas e portais', 'conecte-se ao portal',
                'loja oficial', 'uma empresa do', 'revenda master', 'importadora oficial', 'venda de drones',
                'ead nota maxima', 'nota maxima no mec', 'representante oficial dji') if phrase in bio]
    signals = [phrase for phrase in ('clientes satisfeitos', 'nossos vendedores', 'assistencia tecnica',
               'maior rede', 'distribuidora', 'atacado', 'varejo',
               'fazendas atendidas', 'anos de mercado') if phrase in bio]
    commercial = explicit or (signals if len(signals) >= 2 else [])
    handle_company = bool(re.search(r'(?:^|[_.])ltda(?:$|[_.])', record.get('handle', '')))
    evidence = (['nome: ' + ', '.join(terms)] if terms else []) + (['bio: ' + ', '.join(commercial)] if commercial else []) + (['LTDA no usuário'] if handle_company else [])
    if bio.startswith(('escola de ','universidade de ','faculdade de ')):
        evidence.append('bio apresenta uma instituição de ensino')
    if 'matricule-se' in bio and any(term in bio for term in ('medicina','graduacao','cursos')):
        evidence.append('bio oferece matrícula em formação educacional')
    if contains(name,'notícias') and any(phrase in bio for phrase in ('noticias diarias','portal de noticias')):
        evidence.append('perfil editorial: nome de página de notícias e bio institucional')
    if bio.startswith('noticias sobre ') and not contains(name+' '+bio,'jornalista'):
        evidence.append('perfil editorial: bio descreve uma página de notícias')
    return {'is_company': bool(evidence), 'reason': 'Provável empresa — ' + '; '.join(evidence) if evidence else 'Identidade não confirmada; nenhum sinal comercial forte nas regras atuais'}


def categories_info(record):
    manual = record.get('categories', '')
    if manual:
        return [c.strip() for c in manual.split(',') if c.strip()], 'Classificação manual'
    text = ' '.join(record.get(k, '') for k in ('name', 'public_name', 'bio', 'tags')) + ' ' + ' '.join(post['text'] for post in record.get('posts', []))
    result = [category for category, terms in CATEGORY_TERMS.items() if any(contains(text, t) for t in terms)]
    return result, 'Sugestão por palavras do nome, bio, temas e publicações; revisar'


def enrich(record):
    result = dict(record)
    result.setdefault('saved', bool(record.get('favorite') or record.get('status') == 'Selecionado'))
    result['region_info'] = location_info(record)
    result['company_info'] = company_info(record)
    result['generic_categories'], result['categories_source'] = categories_info(record)
    result['posts_count'] = len(record.get('posts', []))
    result['creator_evidence'] = ('Provável empresa; revisar' if result['company_info']['is_company'] else 'Classificado como criador por você' if record.get('kind')=='Criador' else 'Autoria de publicação identificada; avaliar o criador' if result['posts_count'] else 'Sem publicação de autoria identificada nesta coleta')
    result['hashtags_found'] = sorted(set(re.findall(r'(?<!\w)#(\w+)', record.get('bio', '') + ' ' + ' '.join(p['text'] for p in record.get('posts', [])), re.UNICODE)))
    return result


def filter_options(args):
    def flag(key):
        value = args.get(key, '')
        return value is True or value in ('1', 'true')
    result = {k: str(args.get(k, '')).strip()[:1000] for k in ('region', 'category', 'keywords', 'scope', 'match', 'hashtags')}
    for key in ('min_followers', 'max_followers'):
        value = args.get(key, '')
        if value in ('', None):
            result[key] = None
        elif isinstance(value, bool) or not re.fullmatch(r'\d{1,12}', str(value)):
            raise ValueError('A faixa de seguidores deve conter números inteiros positivos.')
        else:
            result[key] = int(value)
    if result['min_followers'] is not None and result['max_followers'] is not None and result['min_followers'] > result['max_followers']:
        raise ValueError('O mínimo de seguidores não pode ser maior que o máximo.')
    for key in ('include_unknown_region', 'include_unknown_followers', 'exclude_companies'):
        result[key] = flag(key)
    result['scope'] = result['scope'] or 'bio_posts'
    result['match'] = result['match'] or 'all'
    if result['scope'] not in ('bio', 'posts', 'bio_posts', 'hashtags') or result['match'] not in ('all', 'any'):
        raise ValueError('Opção de busca de conteúdo inválida.')
    if result['category'] and result['category'] not in CATEGORY_TERMS and result['category'] != 'Não identificada':
        raise ValueError('Categoria genérica inválida.')
    return result


def matches(record, options):
    count = record.get('followers_count')
    low, high = options['min_followers'], options['max_followers']
    if low is not None or high is not None:
        if count is None:
            if not options['include_unknown_followers']:
                return False
        elif (low is not None and count < low) or (high is not None and count > high):
            return False
    region = options['region']
    if region:
        info = record['region_info']
        target = normalize(region)
        match = contains(info['text'], region) or any(target == normalize(code) or target == normalize(STATES[code][0]) for code in info['states'])
        match = match or any(target == normalize(r) for r in info['regions'])
        if target in ('brasil', 'brazil', 'br') and info['states']:
            match = True
        if not match and not (not info['known'] and options['include_unknown_region']):
            return False
    if options['exclude_companies'] and record['company_info']['is_company']:
        return False
    category = options['category']
    if category == 'Não identificada' and record['generic_categories']:
        return False
    if category and category != 'Não identificada' and category not in record['generic_categories']:
        return False
    scope = options['scope']
    posts = ' '.join(p['text'] for p in record.get('posts', []))
    if scope == 'hashtags':
        text = ' '.join('#' + t for t in record['hashtags_found'])
    else:
        text = ' '.join([record.get('bio', '') if scope != 'posts' else '', posts if scope != 'bio' else ''])
    terms = [t.strip().lstrip('#') if scope == 'hashtags' else t.strip() for t in options['keywords'].split(',') if t.strip()]
    if terms:
        tests = [contains(text, '#' + t if scope == 'hashtags' else t) for t in terms]
        if not (all(tests) if options['match'] == 'all' else any(tests)):
            return False
    hashtags = [normalize(t.lstrip('#')) for t in re.split(r'[\s,]+', options['hashtags']) if t.lstrip('#')]
    available = {normalize(t) for t in record['hashtags_found']}
    if hashtags and not all(t in available for t in hashtags):
        return False
    return True


REJECTION_GROUPS = {
    'followers': ('Fora da faixa ou seguidores indisponíveis', ('min_followers', 'max_followers', 'include_unknown_followers')),
    'region': ('Região diferente ou não confirmada', ('region', 'include_unknown_region')),
    'company': ('Sinais de empresa', ('exclude_companies',)),
    'category': ('Categoria sem correspondência nas evidências', ('category',)),
    'keywords': ('Palavras-chave ausentes no conteúdo disponível', ('keywords', 'scope', 'match')),
    'hashtags': ('Hashtags ausentes no conteúdo disponível', ('hashtags',)),
}


def rejection_reasons(record, options):
    reasons = []
    for code, (_, keys) in REJECTION_GROUPS.items():
        isolated = filter_options({})
        isolated.update({key: options[key] for key in keys})
        if not matches(record, isolated):
            reasons.append(code)
    return reasons
