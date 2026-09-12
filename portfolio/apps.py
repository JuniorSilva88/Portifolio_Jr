"""Configuração do app portfolio."""

from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolio"
    # Nome amigável que aparece no menu do /admin.
    verbose_name = "Portfólio"
