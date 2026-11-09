#!/usr/bin/env python3
"""Atribui IDs persistentes à base, preservando IDs e textos existentes."""
import argparse
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo


def assign_ids(data):
    seen = set()
    changed = False

    def identifier(item, prefix):
        nonlocal changed
        if 'id' not in item:
            item['id'] = prefix + uuid4().hex
            changed = True
        value = item['id']
        if not isinstance(value, str) or not value.strip() or value in seen:
            raise ValueError('ID vazio, inválido ou duplicado na base.')
        seen.add(value)

    for group in data['experiencias']:
        identifier(group, 'EMP_')
        for index, item in enumerate(group['experiencia']):
            if isinstance(item, str):
                item = {'texto': item}
                group['experiencia'][index] = item
                changed = True
            if not isinstance(item, dict) or not isinstance(item.get('texto'), str):
                raise ValueError('Experiência deve ter texto preservado.')
            identifier(item, 'EXP_')
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    args = parser.parse_args()
    raw = args.base.read_bytes()
    data = json.loads(raw)
    if not assign_ids(data):
        print('IDs existentes preservados; nenhum arquivo alterado.')
        return
    root = Path(__file__).resolve().parents[2]
    stamp = datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y%m%d-%H%M%S-%f')
    backup = root / 'historico' / 'correcoes_base' / (stamp + '-ids-persistentes')
    backup.mkdir(parents=True, exist_ok=False)
    (backup / 'curriculo_base.antes.json').write_bytes(raw)
    output = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    # A segunda aplicação deve preservar todos os IDs.
    check = json.loads(output)
    assert not assign_ids(check)
    args.base.write_text(output, encoding='utf-8')
    assert json.loads(args.base.read_text(encoding='utf-8')) == data
    print(f'IDs atribuídos. Cópia anterior em {backup}')


if __name__ == '__main__':
    main()
