#!/usr/bin/env python3
"""Variante API com matching embedding estruturado; redação e montagem vigentes."""
import argparse
from pathlib import Path
import sys
import time

import avaliar_experiencias as matching
import criar_curriculo
import recuperar_embeddings as embedding


def main(argv=None, *, allow_full_base=False):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--url')
    source.add_argument('--arquivo', type=Path)
    source.add_argument('--candidatura', type=Path)
    source.add_argument('--preparar-embeddings', action='store_true',
                        help='Prepara ou atualiza apenas o índice vetorial local; não cria candidatura.')
    parser.add_argument('--aprovado', action='store_true', help='Registra aprovação humana já dada.')
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args(argv)
    try:
        config = embedding.settings()
        if args.preparar_embeddings:
            if args.aprovado or args.pdf:
                raise ValueError('--preparar-embeddings não aceita --aprovado ou --pdf.')
            # Preparação explicitamente separada de criação de candidatura.
            rules = matching.load(matching.ROOT / 'config/regras_matching.json')
            if 'indice_matching' not in rules:
                raise ValueError('Índice de realizações ausente; nenhuma leitura da base iniciada.')
            base = matching.load(matching.ROOT / 'base/curriculo_base.json')
            def check():
                if (matching.load(matching.ROOT / 'base/curriculo_base.json') != base
                        or matching.load(matching.ROOT / 'config/regras_matching.json') != rules
                        or embedding.settings() != config):
                    raise ValueError('Fontes/configuração mudaram durante a preparação; índice não liberado.')
            started = time.perf_counter()
            result = embedding.prepare(rules['indice_matching'], base, config, matching.get_key(),
                                       source_check=check)
            print(f'Índice local pronto: {result}; {time.perf_counter() - started:.3f}s.')
            return 0
        return criar_curriculo.main(argv, caller_override=embedding.EmbeddingCaller(config, allow_full_base=allow_full_base),
                                    editorial_policy=config.get("redacao"))
    except (ValueError, KeyError, OSError, embedding.sqlite3.Error) as error:
        print(f'Variante embedding não concluída: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
