"""
Views do portfólio.

Eu uso Class-Based Views porque elas já resolvem paginação, contexto e
busca de objeto por slug. Onde preciso de algo meu, sobrescrevo só o
método necessário (get_queryset / get_context_data).
"""

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import ContatoForm
from .models import Habilidade, Projeto


class HomeView(TemplateView):
    """Página inicial: hero + sobre + stack + projetos em destaque + contato."""

    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        # Projetos em destaque. Se eu ainda não marquei nenhum como
        # destaque, mostro os 6 primeiros publicados — a home nunca fica vazia.
        destaques = Projeto.objects.destaques()[:6]
        contexto["projetos"] = destaques or Projeto.objects.publicados()[:6]

        # Agrupo as habilidades por categoria para o template só iterar.
        # Faço isso em Python (a lista é pequena) e economizo uma query
        # por categoria no banco.
        habilidades = Habilidade.objects.publicados()
        grupos: dict[str, list[Habilidade]] = {}
        for item in habilidades:
            grupos.setdefault(item.get_categoria_display(), []).append(item)
        contexto["grupos_habilidades"] = grupos

        contexto["total_projetos"] = Projeto.objects.publicados().count()
        contexto["form"] = ContatoForm()  # formulário de contato da home
        return contexto


class ProjetoListView(ListView):
    """Lista todos os projetos, com busca por texto e filtro por linguagem."""

    model = Projeto
    template_name = "portfolio/projetos.html"
    context_object_name = "projetos"
    paginate_by = 9  # 3 colunas x 3 linhas no desktop

    def get_queryset(self):
        queryset = Projeto.objects.publicados()

        # Busca livre: título, resumo e tecnologias. Uso Q para fazer OR
        # em uma única consulta ao banco.
        busca = self.request.GET.get("q", "").strip()
        if busca:
            queryset = queryset.filter(
                Q(titulo__icontains=busca)
                | Q(resumo__icontains=busca)
                | Q(tecnologias__icontains=busca)
            )

        # Filtro por linguagem (os botões acima da grade).
        linguagem = self.request.GET.get("linguagem", "").strip()
        if linguagem:
            queryset = queryset.filter(linguagem__iexact=linguagem)

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Monto a lista de linguagens direto do banco (distinct) para os
        # filtros nunca ficarem desatualizados quando eu adicionar projeto.
        contexto["linguagens"] = (
            Projeto.objects.publicados()
            .exclude(linguagem="")
            .values_list("linguagem", flat=True)
            .distinct()
            .order_by("linguagem")
        )
        contexto["busca"] = self.request.GET.get("q", "")
        contexto["linguagem_ativa"] = self.request.GET.get("linguagem", "")
        return contexto


class ProjetoDetailView(DetailView):
    """Página de detalhe de um projeto, buscado pelo slug da URL."""

    model = Projeto
    template_name = "portfolio/projeto_detalhe.html"
    context_object_name = "projeto"

    def get_queryset(self):
        # Importante: filtro por publicados aqui também, senão um rascunho
        # ficaria acessível para quem descobrisse a URL.
        return Projeto.objects.publicados()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Sugiro outros projetos, de preferência da mesma linguagem.
        relacionados = Projeto.objects.publicados().exclude(pk=self.object.pk)
        if self.object.linguagem:
            mesma_linguagem = relacionados.filter(linguagem=self.object.linguagem)
            relacionados = mesma_linguagem or relacionados
        contexto["relacionados"] = relacionados[:3]
        return contexto


class ContatoView(FormView):
    """Recebe o formulário de contato e salva a mensagem no banco."""

    template_name = "portfolio/contato.html"
    form_class = ContatoForm
    success_url = reverse_lazy("portfolio:contato")

    def form_valid(self, form):
        # Se o honeypot foi preenchido, finjo sucesso e não salvo nada.
        if form.eh_robo():
            return redirect(self.get_success_url())

        form.save()
        # Uso o framework de messages para o aviso sobreviver ao redirect
        # (padrão POST/redirect/GET, evita reenvio ao atualizar a página).
        messages.success(
            self.request, "Mensagem enviada com sucesso. Eu respondo em breve."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Confira os campos destacados e tente novamente.")
        return super().form_invalid(form)


class DocumentacaoView(TemplateView):
    """Página de documentação técnica do próprio projeto.

    Eu deixo a documentação dentro do site (e não só no README) porque
    ela também é parte do que quero mostrar: como o projeto foi construído.
    """

    template_name = "portfolio/documentacao.html"


# ---------------------------------------------------------------------------
# Páginas de erro personalizadas
# ---------------------------------------------------------------------------
# O Django chama estas funções quando DEBUG=False. Elas precisam ter essa
# assinatura exata (request, exception) para o 404.


def erro_404(request, exception):  # pragma: no cover - handler do Django
    """Minha página de 404 com a mesma identidade visual do site."""
    from django.shortcuts import render

    return render(request, "404.html", status=404)


def erro_500(request):  # pragma: no cover - handler do Django
    """Minha página de 500."""
    from django.shortcuts import render

    return render(request, "500.html", status=500)
