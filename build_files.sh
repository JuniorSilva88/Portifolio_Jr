#!/usr/bin/env bash
# build_files.sh — script de build da Vercel.
#
# A Vercel roda este arquivo antes de publicar. Aqui eu só instalo as
# dependências e gero a pasta staticfiles (CSS/JS comprimidos com hash).
#
# Não rodo migrate aqui: o build da Vercel é efêmero e o banco de produção
# é externo (Neon/Supabase/Render). As migrações eu aplico uma vez, pelo
# meu terminal, apontando DATABASE_URL para esse banco.
set -o errexit   # aborta no primeiro erro, em vez de publicar site quebrado

echo "==> Instalando dependências"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "==> Coletando arquivos estáticos"
python3 manage.py collectstatic --noinput --clear

echo "==> Build concluído"
