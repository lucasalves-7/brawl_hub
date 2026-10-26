"""
Configurações do projeto Brawl Hub.

A chave da API da Supercell é lida de variáveis de ambiente e nunca deve
ser exposta no HTML, no JavaScript enviado ao navegador nem em um repositório
público. Ver seção 9.3 do plano do projeto.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do .env (arquivo local, fora do controle de versão).
# python-dotenv é opcional: se não estiver instalado, usamos o ambiente do SO.
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# ---------------------------------------------------------------- Segurança --
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-key-troque-em-producao")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# ------------------------------------------------------------ Aplicativos ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps do Brawl Hub
    "apps.core",
    "apps.players",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------------------- Bancos ----
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------------------------------------- Validação senha ----
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------------------------------- Geral ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------- Estáticos ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------------------------------------------- Cache ----
# Usado por services/cache.py para evitar novas consultas a cada interação.
# A duração (TTL) varia por tipo de dado (ver services/cache.py).
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "brawl-hub",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------- Integração Supercell (fase 4) -------
# A chave é carregada do ambiente. Nunca colocar o valor literal aqui.
SUPERCELL_API_KEY = os.environ.get("SUPERCELL_API_KEY", "")
SUPERCELL_API_BASE = os.environ.get(
    "SUPERCELL_API_BASE", "https://api.brawlstars.com/v1"
)
SUPERCELL_REQUEST_TIMEOUT = int(os.environ.get("SUPERCELL_REQUEST_TIMEOUT", "10"))
