"""
Configurações do meu portfólio em Django.

Eu centralizei tudo aqui e deixei o arquivo preparado para rodar em três
lugares diferentes sem eu precisar mudar código:

1. Local (SQLite + DEBUG=True)
2. Render   (Postgres + Gunicorn + WhiteNoise)
3. Vercel   (função serverless usando o WSGI de config/wsgi.py)

A regra que eu sigo: nada de segredo dentro do código. Tudo que muda de
ambiente para ambiente eu leio de variável de ambiente (arquivo .env no
local, painel de variáveis no Render/Vercel).
"""

from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
import os

# BASE_DIR é a raiz do projeto (a pasta onde fica o manage.py).
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrego o .env quando ele existir. Em produção esse arquivo não existe:
# lá as variáveis vêm do próprio painel da plataforma.
load_dotenv(BASE_DIR / ".env")


def env_bool(nome: str, padrao: bool = False) -> bool:
    """Leio um booleano de variável de ambiente de forma tolerante.

    Eu criei esse helper porque variável de ambiente é sempre string:
    "1", "true", "True" e "yes" precisam virar True.
    """
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def env_list(nome: str, padrao: str = "") -> list[str]:
    """Transformo uma variável separada por vírgula em lista limpa."""
    bruto = os.getenv(nome, padrao)
    return [item.strip() for item in bruto.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------

# Em desenvolvimento eu deixo uma chave insegura só para o projeto subir.
# Em produção eu SEMPRE defino SECRET_KEY no painel da plataforma.
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-chave-apenas-para-desenvolvimento-local",
)

# DEBUG começa ligado no local e eu desligo em produção (DEBUG=False).
DEBUG = env_bool("DEBUG", True)

# Hosts liberados. No Render eu uso o domínio que a plataforma gera e na
# Vercel o *.vercel.app — por isso já deixo os dois curingas prontos.
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com,.vercel.app")

# O Django 4+ exige origem confiável explícita para POST via HTTPS.
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.onrender.com,https://*.vercel.app",
)

# Quando estou em produção eu subo o nível de segurança de uma vez.
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 dias
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "SAMEORIGIN"
    # Render e Vercel ficam atrás de proxy: sem isso o Django não sabe
    # que a requisição original era HTTPS e entra em loop de redirect.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ---------------------------------------------------------------------------
# Apps e middlewares
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Meu app: tudo do portfólio (models, views, templates, comandos).
    "portfolio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise entra logo depois do SecurityMiddleware para servir os
    # arquivos estáticos em produção sem eu precisar de Nginx/CDN.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Deixo os templates globais em /templates e os do app dentro dele.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Meu context processor: joga o perfil e o ano atual em
                # todo template, então o rodapé e o menu nunca ficam vazios.
                "portfolio.context_processors.dados_do_site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------

# Se existir DATABASE_URL (caso do Render com Postgres) eu uso ela.
# Se não existir, caio no SQLite local. Assim o mesmo código roda nos dois.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,          # reaproveito conexão por 10 minutos
        conn_health_checks=True,   # o Django testa a conexão antes de usar
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Internacionalização — o site é meu, então tudo em português do Brasil
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Arquivos estáticos e de mídia
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
# Onde eu escrevo meus CSS/JS/imagens.
STATICFILES_DIRS = [BASE_DIR / "static"]
# Onde o collectstatic junta tudo para o WhiteNoise servir.
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Comprime os arquivos e coloca hash no nome (cache eterno no
        # navegador sem risco de servir versão velha). Uso a minha subclasse
        # tolerante para o projeto rodar mesmo antes do collectstatic.
        "BACKEND": "config.storages.EstaticosTolerantes",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Logs — quero ver erro no console da plataforma, não em arquivo
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL") or "INFO"},
}
