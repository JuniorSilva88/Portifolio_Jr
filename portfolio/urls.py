"""
Rotas do app portfolio.

Uso app_name para ter namespace ("portfolio:home"): se um dia eu plugar
outro app com rota "home", nada colide.
"""

from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("projetos/", views.ProjetoListView.as_view(), name="projetos"),
    # Slug em vez de id: URL legível e melhor para busca.
    path("projetos/<slug:slug>/", views.ProjetoDetailView.as_view(), name="projeto_detalhe"),
    path("contato/", views.ContatoView.as_view(), name="contato"),
    path("documentacao/", views.DocumentacaoView.as_view(), name="documentacao"),
]
