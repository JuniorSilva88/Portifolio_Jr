"""
Entrada serverless da Vercel.

A Vercel procura uma variável chamada `app` (ou `handler`) neste arquivo e
usa ela como função. Eu só reaproveito o WSGI que o Django já gerou em
config/wsgi.py — nenhuma lógica duplicada aqui.
"""

import os
import sys
from pathlib import Path

# A função roda a partir de /api, então eu coloco a raiz do projeto no
# sys.path para o import de `config` funcionar.
RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application  # noqa: E402  (precisa vir após o setdefault)

# Nome que a Vercel espera encontrar.
app = application
