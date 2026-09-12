"""
Rotas raiz do projeto.

Aqui eu só faço o roteamento de alto nível: o admin, um endpoint de
health check (o Render usa para saber se a aplicação está viva) e o
include das rotas do meu app.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    """Endpoint leve de monitoramento. Não toca no banco de propósito."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", health, name="health"),
    path("", include("portfolio.urls")),
]

# Handlers de erro personalizados (só entram em ação com DEBUG=False).
handler404 = "portfolio.views.erro_404"
handler500 = "portfolio.views.erro_500"
