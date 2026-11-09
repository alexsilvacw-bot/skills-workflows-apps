"""Respostas estruturadas via Codex CLI e conta ChatGPT, sem chave de API."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import extrair_vaga

CALL_TIMEOUT_SECONDS = 180


class CodexAccount:
    backend = 'codex-chatgpt'

    def __init__(self, extraction_model, matching_model, writing_model):
        self.models = {'extracao_vaga': extraction_model, 'redacao_curriculo': writing_model}
        self.matching_model = matching_model
        self.backend += ':' + hashlib.sha256(json.dumps({
            'modelos': [extraction_model, matching_model, writing_model],
            'esforcos': {k: os.environ.get(k) for k in ('OPENAI_REASONING_EFFORT',
                'OPENAI_EXTRACTION_REASONING_EFFORT', 'OPENAI_MATCHING_REASONING_EFFORT')}
        }, sort_keys=True).encode()).hexdigest()
        self.executable = None
        self.env = {k: v for k, v in os.environ.items()
                    if k not in {'OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_BASE_URL',
                                 'OPENAI_API_BASE', 'CODEX_ACCESS_TOKEN'} and not k.startswith('RUST_LOG')}
        self.env['PYTHONDONTWRITEBYTECODE'] = '1'
        self.authenticated = False

    def check_login(self):
        self.executable = shutil.which('codex')
        if not self.executable:
            raise ValueError('Codex CLI não encontrado. Instale/configure o cliente oficial; não usar API como alternativa.')
        try:
            status = subprocess.run([self.executable, 'login', 'status'], env=self.env,
                                    capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            raise ValueError('Não foi possível verificar a autenticação do Codex CLI.') from None
        # Não imprimir a saída: um cliente autenticado por chave pode exibir informações dela.
        if status.returncode or 'Logged in using ChatGPT' not in status.stdout + status.stderr:
            raise ValueError('Codex CLI precisa estar autenticado com ChatGPT. Use codex login; não usar chave de API.')
        self.authenticated = True

    def extract(self, text, key, model, timeout=CALL_TIMEOUT_SECONDS, correction=None):
        payload = extrair_vaga.model_payload(text, model, correction)
        return self(json.loads(payload['input']), payload['instructions'], extrair_vaga.SCHEMA,
                    'extracao_vaga', model, None,
                    reasoning_effort=payload.get('reasoning', {}).get('effort'))

    def __call__(self, data, instructions, schema, name, model, key,
                 telemetry=None, reasoning_effort=None):
        if key is not None:
            raise ValueError('O modo de conta não aceita chave de API.')
        if any(not isinstance(value, str) or not value.strip()
               for value in (*self.models.values(), self.matching_model)):
            raise ValueError('Modelo por etapa ausente; não usar o modelo padrão do cliente como alternativa.')
        if not self.authenticated:
            self.check_login()
        chosen = model
        if not isinstance(chosen, str) or not chosen.strip():
            raise ValueError('Modelo da chamada ausente; não usar o modelo padrão do cliente como alternativa.')
        if reasoning_effort is None:
            variable = ('OPENAI_REASONING_EFFORT' if name == 'redacao_curriculo'
                        else 'OPENAI_EXTRACTION_REASONING_EFFORT' if name == 'extracao_vaga'
                        else 'OPENAI_MATCHING_REASONING_EFFORT')
            default = 'low' if name == 'extracao_vaga' else 'medium'
            reasoning_effort = os.environ.get(variable, os.environ.get('OPENAI_REASONING_EFFORT', default))
        if reasoning_effort not in {'low', 'medium', 'high', 'xhigh', 'max'}:
            raise ValueError('Esforço de raciocínio inválido.')
        print(f'Codex pela conta: {name}; modelo={chosen}; esforço={reasoning_effort}; '
              f'prazo={CALL_TIMEOUT_SECONDS}s por chamada.',
              file=sys.stderr, flush=True)
        with tempfile.TemporaryDirectory(prefix='adaptar-vaga-codex-') as temporary:
            directory = Path(temporary)
            schema_path = directory/'schema.json'
            output = directory/'resposta.json'
            schema_path.write_text(json.dumps(schema, ensure_ascii=False), encoding='utf-8')
            schema_path.chmod(0o600)
            command = [self.executable, 'exec', '--ignore-user-config', '--ephemeral',
                       '--skip-git-repo-check', '--sandbox', 'read-only', '--cd', str(directory),
                       '--model', chosen, '--output-schema', str(schema_path),
                       '--output-last-message', str(output), '--json',
                       '-c', 'forced_login_method="chatgpt"', '-c', 'model_provider="openai"',
                       '-c', 'web_search="disabled"',
                       '-c', 'model_reasoning_effort=' + json.dumps(reasoning_effort)]
            for feature in ('shell_tool', 'unified_exec', 'code_mode_host', 'apps', 'plugins',
                            'hooks', 'computer_use', 'browser_use', 'image_generation',
                            'multi_agent', 'unbounded_connection_retries'):
                command.extend(['--disable', feature])
            command.append('-')
            prompt = instructions + '\n\n' + json.dumps(data, ensure_ascii=False)
            try:
                result = subprocess.run(command, input=prompt, env=self.env, capture_output=True,
                                        text=True, timeout=CALL_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                raise ValueError(f'Codex excedeu o prazo de {CALL_TIMEOUT_SECONDS} segundos na etapa {name}; '
                                 'retome sem trocar modelo ou usar API.') from None
            except OSError:
                raise ValueError(f'Não foi possível iniciar Codex na etapa {name}.') from None
            if result.returncode:
                # Diagnóstico apenas por categoria, sem expor prompt, resposta ou autenticação.
                detail = (result.stderr + result.stdout).casefold()
                cause = ('limite de uso' if any(x in detail for x in ('usage limit', 'rate limit', 'quota'))
                         else 'modelo indisponível' if any(x in detail for x in ('model is not', 'model not', 'unsupported model'))
                         else 'autenticação' if any(x in detail for x in ('unauthorized', 'authentication', 'login'))
                         else 'falha do cliente ou conexão')
                raise ValueError(f'Codex falhou em {name} com {chosen}: {cause} (código {result.returncode}). '
                                 'Nenhuma troca de modelo ou chamada de API realizada pelo fluxo.')
            completed = False
            for line in result.stdout.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get('type') in {'error', 'turn.failed'}:
                    raise ValueError(f'Codex não completou {name}; resposta não aceita.')
                if event.get('type') == 'turn.completed':
                    completed = True
                    if telemetry is not None:
                        telemetry({'status': 'completed', 'usage': event.get('usage')})
            if not completed or not output.is_file():
                raise ValueError('Codex não produziu resposta final completa; nenhum resultado aceito.')
            try:
                value = json.loads(output.read_text(encoding='utf-8'))
            except (ValueError, OSError):
                raise ValueError('Codex não devolveu JSON válido.') from None
            from avaliar_experiencias import validate, validate_assessment_ids
            if name == 'matching' and isinstance(value, dict) and isinstance(value.get('avaliacoes'), dict):
                validate_assessment_ids([{'id': x} for x in value['avaliacoes']], data['evidencias'])
            validate(value, schema)
            return value
