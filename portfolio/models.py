"""
Modelos do portfólio.

Eu modelei o site em quatro peças que refletem exatamente as seções da
página inicial:

- Perfil       -> quem eu sou (hero + sobre + links)
- Habilidade   -> minha stack, agrupada por categoria
- Projeto      -> os repositórios/trabalhos que quero mostrar
- Mensagem     -> o que chega pelo formulário de contato

Tudo é editável pelo /admin, então eu atualizo o portfólio sem tocar em
código nem fazer novo deploy.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Publicado(models.QuerySet):
    """QuerySet reaproveitável para eu não repetir filtro em toda view."""

    def publicados(self):
        """Só o que eu marquei como visível no site."""
        return self.filter(publicado=True)

    def destaques(self):
        """Os itens que eu quero em cima, na vitrine da home."""
        return self.publicados().filter(destaque=True)


class Perfil(models.Model):
    """Meus dados pessoais.

    É uma tabela de uma linha só (um perfil por site). Eu prefiro isso a
    deixar texto solto no template: assim eu edito pelo admin.
    """

    nome = models.CharField("nome completo", max_length=120)
    titulo = models.CharField(
        "título profissional",
        max_length=140,
        help_text="Ex.: Desenvolvedor Full Stack | Analista e Desenvolvedor de Sistemas",
    )
    resumo = models.TextField(
        "resumo curto",
        help_text="Frase de impacto que aparece no topo da página (hero).",
    )
    bio = models.TextField(
        "biografia",
        help_text="Texto da seção 'Sobre mim'. Cada linha em branco vira um parágrafo.",
    )
    cidade = models.CharField("cidade", max_length=80, blank=True)
    email = models.EmailField("e-mail de contato", blank=True)
    telefone = models.CharField("telefone/WhatsApp", max_length=40, blank=True)
    github = models.URLField("GitHub", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    curriculo = models.URLField("link do currículo", blank=True)
    disponivel = models.BooleanField(
        "disponível para novos projetos",
        default=True,
        help_text="Controla o selo verde de disponibilidade no topo do site.",
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfil"

    def __str__(self) -> str:
        return self.nome

    @property
    def paragrafos_bio(self) -> list[str]:
        """Quebro a bio em parágrafos para o template só iterar."""
        return [p.strip() for p in self.bio.split("\n") if p.strip()]

    @property
    def iniciais(self) -> str:
        """Iniciais do meu nome — uso no avatar/monograma."""
        partes = [p for p in self.nome.split() if p]
        if not partes:
            return "?"
        return (partes[0][0] + partes[-1][0]).upper()


class Habilidade(models.Model):
    """Uma tecnologia da minha stack, com nível e categoria."""

    class Categoria(models.TextChoices):
        # Uso TextChoices em vez de string solta para o admin já mostrar
        # o select certinho e eu não errar digitação.
        BACKEND = "backend", "Back-end"
        FRONTEND = "frontend", "Front-end"
        DADOS = "dados", "Dados e banco"
        FERRAMENTAS = "ferramentas", "Ferramentas e DevOps"

    nome = models.CharField("nome", max_length=60)
    categoria = models.CharField(
        "categoria", max_length=20, choices=Categoria.choices, default=Categoria.BACKEND
    )
    nivel = models.PositiveSmallIntegerField(
        "nível (0 a 100)",
        default=60,
        help_text="Uso esse número para desenhar a barra de progresso.",
    )
    descricao = models.CharField("descrição curta", max_length=160, blank=True)
    ordem = models.PositiveSmallIntegerField("ordem de exibição", default=0)
    publicado = models.BooleanField("publicado", default=True)
    destaque = models.BooleanField("destaque", default=False)

    objects = Publicado.as_manager()

    class Meta:
        verbose_name = "habilidade"
        verbose_name_plural = "habilidades"
        # Ordeno primeiro pelo campo manual e depois alfabético: assim eu
        # controlo a vitrine sem precisar renumerar tudo.
        ordering = ["ordem", "nome"]

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_categoria_display()})"


class Projeto(models.Model):
    """Um projeto meu — normalmente um repositório do meu GitHub."""

    titulo = models.CharField("título", max_length=140)
    slug = models.SlugField(
        "slug",
        max_length=160,
        unique=True,
        blank=True,
        help_text="Gerado automaticamente a partir do título se eu deixar em branco.",
    )
    resumo = models.CharField(
        "resumo", max_length=220, help_text="Uma linha, aparece no card."
    )
    descricao = models.TextField(
        "descrição completa", help_text="Texto da página de detalhe do projeto."
    )
    linguagem = models.CharField("linguagem principal", max_length=40, blank=True)
    tecnologias = models.CharField(
        "tecnologias",
        max_length=200,
        blank=True,
        help_text="Separadas por vírgula. Ex.: Django, PostgreSQL, HTML",
    )
    repositorio = models.URLField("link do repositório", blank=True)
    demo = models.URLField("link do site publicado", blank=True)
    ano = models.PositiveSmallIntegerField("ano", null=True, blank=True)
    ordem = models.PositiveSmallIntegerField("ordem de exibição", default=0)
    publicado = models.BooleanField("publicado", default=True)
    destaque = models.BooleanField(
        "destaque", default=False, help_text="Aparece na vitrine da página inicial."
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    objects = Publicado.as_manager()

    class Meta:
        verbose_name = "projeto"
        verbose_name_plural = "projetos"
        ordering = ["ordem", "-ano", "titulo"]
        indexes = [
            # Índice pensado nas consultas que eu realmente faço:
            # "projetos publicados em destaque".
            models.Index(fields=["publicado", "destaque"]),
        ]

    def __str__(self) -> str:
        return self.titulo

    def save(self, *args, **kwargs):
        """Se eu esquecer o slug, o próprio modelo resolve para mim."""
        if not self.slug:
            self.slug = slugify(self.titulo)[:160]
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """URL canônica do projeto (uso nos templates e no admin)."""
        return reverse("portfolio:projeto_detalhe", kwargs={"slug": self.slug})

    @property
    def lista_tecnologias(self) -> list[str]:
        """Converto a string de tecnologias em lista para virar chips."""
        return [t.strip() for t in self.tecnologias.split(",") if t.strip()]


class Mensagem(models.Model):
    """Mensagem recebida pelo formulário de contato.

    Eu guardo no banco em vez de mandar e-mail direto: não depende de
    servidor SMTP configurado e nada se perde se o envio falhar.
    """

    nome = models.CharField("nome", max_length=120)
    email = models.EmailField("e-mail")
    assunto = models.CharField("assunto", max_length=140, blank=True)
    conteudo = models.TextField("mensagem")
    lida = models.BooleanField("lida", default=False)
    enviada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"
        ordering = ["-enviada_em"]

    def __str__(self) -> str:
        return f"{self.nome} — {self.assunto or 'sem assunto'}"
