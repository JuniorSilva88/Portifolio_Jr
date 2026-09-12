#!/usr/bin/env bash

set -e

echo "==> Criando ambiente virtual"
python3 -m venv .venv

echo "==> Atualizando pip"
.venv/bin/python -m pip install --upgrade pip

echo "==> Instalando dependências"
.venv/bin/python -m pip install -r requirements.txt

echo "==> Coletando arquivos estáticos"
.venv/bin/python manage.py collectstatic --noinput --clear

echo "==> Build concluído"
