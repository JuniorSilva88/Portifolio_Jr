# Guia de deploy — Render e Vercel

Passo a passo que eu sigo para publicar este portfólio. As duas plataformas são
gratuitas no plano inicial e o mesmo código roda nas duas sem alteração: muda
apenas as variáveis de ambiente.

| Plataforma | Papel                             | Banco                  | Formulário e admin |
| ---------- | --------------------------------- | ---------------------- | ------------------ |
| **Render** | Ambiente completo (recomendado)   | Postgres do Render     | Funcionam          |
| **Vercel** | Vitrine rápida, serverless        | Postgres externo       | Só com Postgres    |

---

## Antes de qualquer deploy

```bash
python manage.py test              # tudo verde
python manage.py check --deploy    # checklist de segurança
git add . && git commit -m "deploy" && git push
```

Gere uma `SECRET_KEY` nova para produção (nunca use a de desenvolvimento):

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

---

## Parte 1 — Render

### Opção A: Blueprint (mais rápido)

O repositório já tem `render.yaml`, que descreve o serviço web **e** o banco
Postgres, com as variáveis ligadas entre eles.

1. Acesse <https://dashboard.render.com> → **New** → **Blueprint**.
2. Conecte o repositório do GitHub.
3. O Render lê o `render.yaml`, mostra o que vai criar (web service +
   Postgres) e você confirma com **Apply**.
4. Aguarde o build. Ao final, a URL é `https://portfolio-django.onrender.com`
   (ou o nome que você escolher).

### Opção B: manual

1. **New** → **PostgreSQL** → plano Free → **Create Database**. Copie a
   *Internal Database URL*.
2. **New** → **Web Service** → conecte o repositório.
3. Preencha:

   | Campo               | Valor                                                                                                      |
   | ------------------- | ---------------------------------------------------------------------------------------------------------- |
   | Runtime             | Python 3                                                                                                   |
   | Build Command       | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`   |
   | Start Command       | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60`                           |
   | Health Check Path   | `/healthz`                                                                                                 |

4. Em **Environment**, adicione:

   ```
   PYTHON_VERSION=3.12.6
   SECRET_KEY=<a chave gerada>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   CSRF_TRUSTED_ORIGINS=https://*.onrender.com
   DATABASE_URL=<Internal Database URL do Postgres>
   ```

5. **Create Web Service** e acompanhe o log do build.

### Depois do primeiro deploy

No **Shell** do serviço (aba Shell no painel do Render):

```bash
python manage.py carregar_dados      # popula perfil, stack e projetos
python manage.py createsuperuser     # cria meu acesso ao /admin
```

### Domínio próprio

**Settings** → **Custom Domains** → adicione o domínio e crie o CNAME apontando
para o host que o Render mostra. Depois acrescente o domínio em
`ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.

### Detalhe do plano gratuito

O serviço "dorme" após 15 minutos sem acesso e o primeiro carregamento depois
disso leva alguns segundos. É comportamento do plano Free, não do projeto.

---

## Parte 2 — Vercel

Na Vercel o Django roda como **função serverless Python**. O arquivo
`vercel.json` manda todas as rotas para `api/index.py`, que apenas expõe o WSGI
do projeto.

### 2.1 Banco de dados (obrigatório)

O sistema de arquivos da função é **somente leitura**: SQLite não funciona.
Crie um Postgres gerenciado gratuito — [Neon](https://neon.tech),
[Supabase](https://supabase.com) ou o próprio Postgres do Render — e guarde a
connection string.

Aplique as migrações do seu terminal, apontando para esse banco:

```bash
export DATABASE_URL="postgres://usuario:senha@host/banco"
python manage.py migrate
python manage.py carregar_dados
python manage.py createsuperuser
```

### 2.2 Deploy

```bash
npm i -g vercel
vercel login
vercel            # preview
vercel --prod     # produção
```

Ou pelo painel: **Add New** → **Project** → importe o repositório do GitHub. A
Vercel detecta o `vercel.json` sozinha.

### 2.3 Variáveis de ambiente

Em **Settings** → **Environment Variables** (marque Production e Preview):

```
SECRET_KEY=<a chave gerada>
DEBUG=False
ALLOWED_HOSTS=.vercel.app
CSRF_TRUSTED_ORIGINS=https://*.vercel.app
DATABASE_URL=postgres://usuario:senha@host/banco
```

Depois de mudar variável, faça um **Redeploy** — a função só lê o novo valor no
próximo build.

### 2.4 Como os arquivos estáticos funcionam aqui

`build_files.sh` roda no build, instala as dependências e executa
`collectstatic`, gerando `staticfiles/`. O `vercel.json` serve
`/static/*` a partir dessa pasta e manda todo o resto para a função.

### 2.5 Limitações que eu documento porque já me pegaram

- Sem `DATABASE_URL` apontando para Postgres, o site abre mas quebra em
  qualquer consulta ao banco.
- Não rode `migrate` no build da Vercel: o build é efêmero e pode rodar em
  paralelo. Migração é passo manual, feito uma vez.
- Upload de arquivo (mídia) exige storage externo (S3, Cloudinary). Este
  portfólio não usa upload, então não é problema aqui.

---

## Parte 3 — Depois de publicar

Checklist que eu passo em toda publicação:

- [ ] Home, projetos, detalhe, contato e documentação abrindo (status 200)
- [ ] `/healthz` respondendo `{"status": "ok"}`
- [ ] `/admin/` acessível e com meu superusuário funcionando
- [ ] CSS e JS carregando (sem 404 no console do navegador)
- [ ] Formulário de contato gravando e mostrando a mensagem de sucesso
- [ ] Tema claro/escuro alternando
- [ ] Layout conferido no celular
- [ ] URL inexistente mostrando o meu 404 (e não o do Django)
- [ ] `DEBUG=False` em produção (nenhuma página de erro amarela do Django)

---

## Parte 4 — Problemas comuns

| Sintoma                                    | Causa provável                    | Solução                                                        |
| ------------------------------------------ | --------------------------------- | -------------------------------------------------------------- |
| `DisallowedHost`                           | Domínio fora de `ALLOWED_HOSTS`   | Adicione o domínio na variável e faça redeploy                  |
| CSS sem carregar em produção               | `collectstatic` não rodou         | Confirme o Build Command / `build_files.sh`                     |
| `CSRF verification failed`                 | Falta `CSRF_TRUSTED_ORIGINS`      | Inclua `https://seu-dominio`                                    |
| Loop infinito de redirect                  | Proxy + `SECURE_SSL_REDIRECT`     | `SECURE_PROXY_SSL_HEADER` (já está no `settings.py`)            |
| `Missing staticfiles manifest entry`       | Rodou antes do `collectstatic`    | `python manage.py collectstatic` (ou use o storage tolerante)   |
| `no such table` / erro de conexão          | Migração não aplicada             | `python manage.py migrate` com a `DATABASE_URL` de produção     |
| Site em branco na Vercel                   | SQLite em ambiente read-only      | Aponte `DATABASE_URL` para um Postgres externo                  |
| Primeira visita muito lenta no Render      | Plano Free "dormindo"             | Normal; um plano pago mantém o serviço ativo                    |
