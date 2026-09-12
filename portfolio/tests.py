"""
Testes automatizados do portfólio.

Eu não testo tudo: testo o que quebraria o site na cara do visitante —
páginas abrindo, filtro funcionando, projeto despublicado escondido e
formulário validando. Rodo com:

    python manage.py test
"""

from django.test import TestCase
from django.urls import reverse

from .forms import ContatoForm
from .models import Habilidade, Mensagem, Perfil, Projeto


class ModeloProjetoTest(TestCase):
    """Comportamento do modelo Projeto."""

    def test_slug_gerado_automaticamente(self):
        """Se eu não informo o slug, o save() cria a partir do título."""
        projeto = Projeto.objects.create(
            titulo="Meu Projeto de Teste", resumo="Resumo", descricao="Descrição"
        )
        self.assertEqual(projeto.slug, "meu-projeto-de-teste")

    def test_lista_tecnologias_quebra_por_virgula(self):
        """A string do banco vira lista limpa para o template."""
        projeto = Projeto.objects.create(
            titulo="Com stack",
            resumo="r",
            descricao="d",
            tecnologias="Django, PostgreSQL ,  HTML",
        )
        self.assertEqual(projeto.lista_tecnologias, ["Django", "PostgreSQL", "HTML"])

    def test_queryset_publicados_e_destaques(self):
        """Os atalhos do meu QuerySet filtram o que eu espero."""
        Projeto.objects.create(titulo="A", resumo="r", descricao="d", publicado=True, destaque=True)
        Projeto.objects.create(titulo="B", resumo="r", descricao="d", publicado=True)
        Projeto.objects.create(titulo="C", resumo="r", descricao="d", publicado=False)

        self.assertEqual(Projeto.objects.publicados().count(), 2)
        self.assertEqual(Projeto.objects.destaques().count(), 1)


class ModeloPerfilTest(TestCase):
    """Properties do Perfil."""

    def setUp(self):
        self.perfil = Perfil.objects.create(
            nome="Junior Alexandre da Silva",
            titulo="Dev",
            resumo="Resumo",
            bio="Primeiro parágrafo.\n\nSegundo parágrafo.",
        )

    def test_paragrafos_bio_ignora_linhas_vazias(self):
        self.assertEqual(len(self.perfil.paragrafos_bio), 2)

    def test_iniciais(self):
        self.assertEqual(self.perfil.iniciais, "JS")


class PaginasTest(TestCase):
    """As páginas públicas precisam abrir com status 200."""

    @classmethod
    def setUpTestData(cls):
        # setUpTestData roda uma vez para a classe inteira: mais rápido
        # que criar os mesmos dados em cada teste.
        Perfil.objects.create(nome="Junior Silva", titulo="Dev", resumo="R", bio="Bio")
        Habilidade.objects.create(nome="Python", categoria="backend", nivel=80)
        cls.projeto = Projeto.objects.create(
            titulo="Projeto Publicado",
            resumo="Resumo",
            descricao="Descrição",
            linguagem="Python",
            publicado=True,
            destaque=True,
        )
        cls.oculto = Projeto.objects.create(
            titulo="Rascunho", resumo="r", descricao="d", publicado=False
        )

    def test_home_abre(self):
        resposta = self.client.get(reverse("portfolio:home"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Projeto Publicado")

    def test_lista_de_projetos_esconde_nao_publicado(self):
        resposta = self.client.get(reverse("portfolio:projetos"))
        self.assertContains(resposta, "Projeto Publicado")
        self.assertNotContains(resposta, "Rascunho")

    def test_busca_filtra_resultados(self):
        resposta = self.client.get(reverse("portfolio:projetos"), {"q": "inexistente"})
        self.assertEqual(len(resposta.context["projetos"]), 0)

    def test_filtro_por_linguagem(self):
        resposta = self.client.get(reverse("portfolio:projetos"), {"linguagem": "Python"})
        self.assertEqual(len(resposta.context["projetos"]), 1)

    def test_detalhe_do_projeto(self):
        resposta = self.client.get(self.projeto.get_absolute_url())
        self.assertEqual(resposta.status_code, 200)

    def test_projeto_nao_publicado_da_404(self):
        """Rascunho não pode ficar acessível nem por URL direta."""
        resposta = self.client.get(self.oculto.get_absolute_url())
        self.assertEqual(resposta.status_code, 404)

    def test_documentacao_abre(self):
        self.assertEqual(self.client.get(reverse("portfolio:documentacao")).status_code, 200)

    def test_health_check(self):
        resposta = self.client.get("/healthz/")
        self.assertEqual(resposta.json()["status"], "ok")


class ContatoTest(TestCase):
    """Formulário de contato: validação, gravação e anti-robô."""

    def test_mensagem_curta_e_invalida(self):
        form = ContatoForm(data={"nome": "Ana", "email": "a@a.com", "conteudo": "oi"})
        self.assertFalse(form.is_valid())
        self.assertIn("conteudo", form.errors)

    def test_envio_valido_grava_no_banco(self):
        resposta = self.client.post(
            reverse("portfolio:contato"),
            {
                "nome": "Ana",
                "email": "ana@exemplo.com",
                "assunto": "Proposta",
                "conteudo": "Tenho um projeto para conversar com você.",
            },
        )
        self.assertEqual(resposta.status_code, 302)  # redirect após sucesso
        self.assertEqual(Mensagem.objects.count(), 1)

    def test_honeypot_descarta_robo(self):
        """Se o campo escondido veio preenchido, eu não gravo nada."""
        self.client.post(
            reverse("portfolio:contato"),
            {
                "nome": "Robo",
                "email": "robo@spam.com",
                "conteudo": "Mensagem automática de spam qualquer.",
                "website": "http://spam.com",
            },
        )
        self.assertEqual(Mensagem.objects.count(), 0)
