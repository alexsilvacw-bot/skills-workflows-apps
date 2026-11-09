#!/bin/zsh
cd "$(dirname "$0")" || exit 1
echo 'Abra http://127.0.0.1:8765 no navegador. Para encerrar, pressione Ctrl+C.'
exec python3 app.py
