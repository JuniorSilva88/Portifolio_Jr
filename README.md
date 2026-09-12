# Portfólio — Junior Alexandre da Silva

Meu portfólio pessoal feito em **Python + Django**, pronto para hospedar no
**Render** (aplicação completa) e na **Vercel** (função serverless).

O site é responsivo, tem tema claro/escuro, painel administrativo para eu
editar o conteúdo sem novo deploy, documentação técnica dentro da própria
página (`/documentacao/`) e todo o código comentado explicando as decisões.

- Curitiba, Paraná — Brasil
- GitHub: [@JuniorSilva88](https://github.com/JuniorSilva88)

---

## Índice

1. [O que tem no site](#o-que-tem-no-site)
2. [Stack](#stack)
3. [Estrutura de pastas](#estrutura-de-pastas)
4. [Como rodar na minha máquina](#como-rodar-na-minha-máquina)
5. [Comandos que eu uso](#comandos-que-eu-uso)
6. [Variáveis de ambiente](#variáveis-de-ambiente)
7. [Deploy](#deploy)
8. [Testes e qualidade](#testes-e-qualidade)
9. [Paleta e tipografia](#paleta-e-tipografia)
10. [Boas práticas aplicadas](#boas-práticas-aplicadas)
11. [Documentação complementar](#documentação-complementar)

---

## O que tem no site

| Página            | Rota                  | Conteúdo                                                             |
| ----------------- | --------------------- | -------------------------------------------------------------------- |
| Início            | `/`                   | Hero, sobre mim, stack com níveis, projetos em destaque e contato    |
| Projetos          | `/projetos/`          | Lista completa com busca, filtro por linguagem e paginação           |
| Detalhe           | `/projetos/<slug>/`   | Descrição, ficha técnica, links e projetos relacionados              |
| Contato           | `/contato/`           | Formulário validado que grava a mensagem no banco                    |
| Documentação      | `/documentacao/`      | A documentação técnica do projeto, navegável                          |
| Admin             | `/admin/`             | Painel para editar perfil, stack, projetos e ler mensagens            |
| Health check      | `/healthz/`           | `{"status": "ok"}` — usado pelo monitoramento do Render               |

Extras: tema claro/escuro, menu mobile, animações ao rolar, páginas 404 e 500
personalizadas, honeypot anti-robô no formulário.

---

## Stack

| Camada        | Tecnologia                          | Por quê                                                     |
| ------------- | ----------------------------------- | ----------------------------------------------------------- |
| Back-end      | Python 3.12 + Django                | Admin pronto, ORM maduro, segurança por padrão              |
| Banco (dev)   | SQLite                              | Zero configuração para desenvolver                          |
| Banco (prod)  | PostgreSQL via `dj-database-url`    | Troco de banco só mudando `DATABASE_URL`                    |
| Front-end     | HTML5, CSS3, JavaScript puro        | Site pequeno — framework só adicionaria peso                |
| Estáticos     | WhiteNoise                          | CSS/JS comprimido e com hash, sem Nginx nem CDN             |
| Servidor      | Gunicorn                            | Padrão de produção para WSGI                                |
| Hospedagem    | Render + Vercel                     | Render roda tudo; Vercel roda como serverless               |

---

## Estrutura de pastas

```
portfolio-django/
├── config/                      # configuração do projeto
│   ├── settings.py              # tudo por variável de ambiente
│   ├── storages.py              # storage estático tolerante (WhiteNoise)
│   ├── urls.py                  # rotas raiz + health check
│   ├── wsgi.py / asgi.py        # entradas do servidor
├── portfolio/                   # meu app
│   ├── models.py                # Perfil, Habilidade, Projeto, Mensagem
│   ├── views.py                 # Class-Based Views
│   ├── forms.py                 # formulário de contato + honeypot
│   ├── urls.py                  # rotas do app (namespace "portfolio")
│   ├── admin.py                 # painel de conteúdo
│   ├── context_processors.py    # perfil e ano em todos os templates
│   ├── tests.py                 # 16 testes automatizados
│   └── management/commands/
│       └── carregar_dados.py    # popula o banco (com opção --github)
├── templates/
│   ├── base.html                # esqueleto de todas as páginas
│   ├── 404.html / 500.html      # páginas de erro personalizadas
│   └── portfolio/
│       ├── home.html
│       ├── projetos.html
│       ├── projeto_detalhe.html
│       ├── contato.html
│       ├── documentacao.html
│       └── partials/            # header, footer, card de projeto
├── static/
│   ├── css/main.css             # design system + componentes (comentado)
│   ├── js/main.js               # tema, menu, animações (comentado)
│   └── img/favicon.svg
├── docs/
│   ├── ARQUITETURA.md
│   └── DEPLOY.md
├── api/index.py                 # entrada serverless da Vercel
├── build_files.sh               # build da Vercel
├── vercel.json                  # roteamento da Vercel
├── render.yaml                  # blueprint do Render
├── Procfile                     # alternativa de start command
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Como rodar na minha máquina

```bash
# 1. clonar
git clone https://github.com/JuniorSilva88/portfolio-django.git
cd portfolio-django

# 2. ambiente virtual
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate

# 3. dependências
pip install -r requirements.txt

# 4. variáveis de ambiente
cp .env.example .env              # e ajusto os valores

# 5. banco + conteúdo
python manage.py migrate
python manage.py carregar_dados
python manage.py createsuperuser

# 6. subir o servidor
python manage.py runserver
```

Site em <http://127.0.0.1:8000> e painel em <http://127.0.0.1:8000/admin/>.

---

## Comandos que eu uso

```bash
python manage.py carregar_dados             # perfil, stack e projetos (lista curada)
python manage.py carregar_dados --github    # importa meus repositórios da API do GitHub
python manage.py carregar_dados --limpar    # apaga e recria o conteúdo
python manage.py test                       # roda os 16 testes
python manage.py check --deploy             # checklist de segurança de produção
python manage.py collectstatic --noinput    # gera a pasta staticfiles/
```

`carregar_dados` é idempotente (usa `update_or_create`): rodar duas vezes não
duplica nada.

---

## Variáveis de ambiente

| Variável               | Exemplo                              | Para que serve                                    |
| ---------------------- | ------------------------------------ | ------------------------------------------------- |
| `SECRET_KEY`           | string longa e aleatória             | Assina sessão e CSRF. Obrigatória em produção.    |
| `DEBUG`                | `False`                              | Em produção sempre `False`.                       |
| `ALLOWED_HOSTS`        | `meusite.onrender.com`               | Domínios que podem servir o site.                 |
| `CSRF_TRUSTED_ORIGINS` | `https://meusite.onrender.com`       | Origens confiáveis para POST via HTTPS.           |
| `DATABASE_URL`         | `postgres://user:senha@host:5432/db` | Sem ela, o projeto usa SQLite local.              |
| `LOG_LEVEL`            | `INFO`                               | Nível dos logs no console da plataforma.          |

Gerar uma chave nova:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

---

## Deploy

Passo a passo completo (com prints do que preencher) em
[`docs/DEPLOY.md`](docs/DEPLOY.md). Resumo:

### Render — aplicação completa

```bash
# Build Command
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

# Start Command
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT

# Health Check Path
/healthz
```

O `render.yaml` já descreve o serviço web e o Postgres, então dá para usar o
modo **Blueprint** e não preencher nada à mão.

### Vercel — serverless

`vercel.json` manda todas as rotas para `api/index.py`, que só expõe o WSGI do
Django. Dois pontos importantes:

- O sistema de arquivos é **somente leitura**: SQLite não funciona. Aponte
  `DATABASE_URL` para um Postgres gerenciado (Neon, Supabase ou o do Render).
- Sem banco de escrita, formulário e admin não gravam. Por isso eu trato a
  Vercel como vitrine e o Render como ambiente completo.

---

## Testes e qualidade

```bash
python manage.py test
# Ran 16 tests — OK
```

Cobrem: geração de slug, properties dos modelos, os atalhos do QuerySet,
status 200 das páginas, projeto despublicado retornando 404, busca, filtro por
linguagem, health check, validação do formulário e o honeypot anti-robô.

---

## Paleta e tipografia

Paleta em azul e verde (sem vermelho, amarelo ou rosa), definida como
variáveis CSS em um único bloco no topo do `main.css`:

| Papel               | Claro     | Escuro    |
| ------------------- | --------- | --------- |
| Marca (azul)        | `#17497a` | `#7fb4de` |
| Destaque (verde)    | `#0f7a5f` | `#22c58f` |
| Fundo               | `#f6f9fc` | `#061420` |
| Superfície          | `#ffffff` | `#0c2032` |
| Texto               | `#08182c` | `#e8f1f8` |

Tipografia: **Cabinet Grotesk** nos títulos e **Satoshi** no texto (Fontshare),
com **JetBrains Mono** nos blocos de código. Escala fluida com `clamp()`.

---

## Boas práticas aplicadas

- **Configuração por ambiente** — o mesmo código roda local, no Render e na Vercel.
- **Nenhum segredo no repositório** — `.env` fora do Git, `.env.example` versionado.
- **Segurança** — com `DEBUG=False` ligo HSTS, cookies seguros, redirect HTTPS,
  `nosniff` e proteção de clickjacking; CSRF em todo formulário.
- **DRY nos templates** — um `base.html` e partials para header, footer e card.
- **Consultas centralizadas** — filtros no QuerySet do modelo, dados globais no
  context processor.
- **Acessibilidade** — HTML semântico, `aria-label`, foco visível, link "pular
  para o conteúdo", contraste AA e respeito a `prefers-reduced-motion`.
- **Responsividade** — `clamp()` na tipografia e no espaçamento, grade com
  `auto-fill`, apenas dois breakpoints.
- **Degradação elegante** — sem JavaScript o conteúdo continua visível.
- **Performance** — estáticos comprimidos com hash, JS com `defer`,
  `IntersectionObserver` em vez de evento de scroll.
- **Código comentado** — cada arquivo explica a decisão, não só o que a linha faz.

---

## Documentação complementar

- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — modelos, fluxo de requisição e decisões técnicas
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — guia detalhado de Render e Vercel
- `/documentacao/` — a mesma documentação, navegável dentro do site

---

## Licença

Código sob licença MIT. O conteúdo (textos, projetos e imagens) é meu.
