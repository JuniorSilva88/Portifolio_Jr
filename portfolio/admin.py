"""
Configuração do /admin.

O admin é o meu painel de conteúdo: eu adiciono projeto, mudo texto do
hero e leio mensagens sem precisar de deploy. Por isso configurei listas,
filtros e busca com cuidado.
"""

from django.contrib import admin

from .models import Habilidade, Mensagem, Perfil, Projeto


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nome", "titulo", "cidade", "disponivel", "atualizado_em")
    # Agrupo os campos para a tela de edição não virar um formulário gigante.
    fieldsets = (
        ("Identidade", {"fields": ("nome", "titulo", "resumo", "bio")}),
        ("Contato", {"fields": ("email", "telefone", "cidade")}),
        ("Links", {"fields": ("github", "linkedin", "curriculo")}),
        ("Status", {"fields": ("disponivel",)}),
    )

    def has_add_permission(self, request):
        # O site tem um único perfil: bloqueio a criação de um segundo.
        return not Perfil.objects.exists()


@admin.register(Habilidade)
class HabilidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "nivel", "ordem", "publicado", "destaque")
    list_filter = ("categoria", "publicado", "destaque")
    search_fields = ("nome", "descricao")
    # list_editable deixa eu ajustar ordem/nível direto na listagem.
    list_editable = ("nivel", "ordem", "publicado", "destaque")


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "linguagem", "ano", "ordem", "publicado", "destaque")
    list_filter = ("publicado", "destaque", "linguagem")
    search_fields = ("titulo", "resumo", "descricao", "tecnologias")
    # O slug se preenche sozinho enquanto eu digito o título.
    prepopulated_fields = {"slug": ("titulo",)}
    list_editable = ("ordem", "publicado", "destaque")
    # Ações em lote para eu publicar/despublicar vários de uma vez.
    actions = ["publicar", "despublicar"]

    @admin.action(description="Publicar selecionados")
    def publicar(self, request, queryset):
        atualizados = queryset.update(publicado=True)
        self.message_user(request, f"{atualizados} projeto(s) publicado(s).")

    @admin.action(description="Despublicar selecionados")
    def despublicar(self, request, queryset):
        atualizados = queryset.update(publicado=False)
        self.message_user(request, f"{atualizados} projeto(s) despublicado(s).")


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "assunto", "lida", "enviada_em")
    list_filter = ("lida", "enviada_em")
    search_fields = ("nome", "email", "assunto", "conteudo")
    # Mensagem é registro de quem me escreveu: leitura apenas, sem edição.
    readonly_fields = ("nome", "email", "assunto", "conteudo", "enviada_em")

    def has_add_permission(self, request):
        return False
