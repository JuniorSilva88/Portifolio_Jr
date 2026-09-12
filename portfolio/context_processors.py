"""
Context processor do site.

Registrei ele no settings (TEMPLATES > context_processors) para o Perfil e
o ano atual estarem disponíveis em QUALQUER template, sem eu repetir a
mesma consulta em toda view.
"""

from django.utils import timezone

from .models import Perfil


def dados_do_site(request):
    """Injeto perfil e ano em todo template renderizado."""
    # .first() em vez de .get(): se o banco ainda estiver vazio o site
    # continua abrindo, só sem os dados pessoais.
    return {
        "perfil": Perfil.objects.first(),
        "ano_atual": timezone.now().year,
    }
