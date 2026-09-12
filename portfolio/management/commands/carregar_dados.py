"""
Comando: python manage.py carregar_dados

Eu criei esse comando para popular o banco com o meu conteúdo real (perfil,
stack e projetos do meu GitHub). Uso ele depois do migrate, tanto no meu
computador quanto no primeiro deploy — o build do Render chama ele.

Duas formas de usar:

    python manage.py carregar_dados              # usa a lista curada abaixo
    python manage.py carregar_dados --github     # busca ao vivo na API do GitHub
    python manage.py carregar_dados --limpar     # apaga e recria o conteúdo

Detalhe importante: eu uso update_or_create em tudo. Assim rodar o comando
duas vezes não duplica nada (é idempotente).
"""

import json
import urllib.request

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from portfolio.models import Habilidade, Perfil, Projeto

# Meu usuário no GitHub — usado no modo --github.
GITHUB_USER = "JuniorSilva88"

# ---------------------------------------------------------------------------
# Conteúdo curado (o que eu quero que apareça por padrão)
# ---------------------------------------------------------------------------

PERFIL = {
    "nome": "Junior Alexandre da Silva",
    "titulo": "Tecnólogo em Análise e Desenvolvimento de Sistemas",
    "resumo": (
        "Construo aplicações web com Python, Django e front-end moderno. "
        "Sempre evoluindo, sempre entregando."
    ),
    "bio": (
        "Sou Tecnólogo em Análise e Desenvolvimento de Sistemas, de Curitiba (PR), "
        "completamente apaixonado pelo mundo da programação e em busca do meu "
        "espaço na área.\n"
        "Comecei pelo front-end, construindo sites e landing pages com HTML, CSS e "
        "JavaScript para negócios reais, e hoje concentro meus estudos e projetos em "
        "Python e Django — models, views, templates, banco de dados e deploy.\n"
        "Gosto de código organizado, comentado e documentado: se outra pessoa (ou eu "
        "mesmo daqui a seis meses) abrir o projeto, precisa entender rápido o que "
        "cada parte faz."
    ),
    "cidade": "Curitiba, Paraná — Brasil",
    "email": "cwbalexandresilva@gmail.com",
    "github": "https://github.com/JuniorSilva88",
    "disponivel": True,
}

HABILIDADES = [
    # (nome, categoria, nível, descrição, ordem)
    ("Python", "backend", 80, "Linguagem principal dos meus projetos back-end", 1),
    ("Django", "backend", 75, "Models, views, templates, admin e deploy", 2),
    ("Django ORM", "dados", 70, "Consultas, relacionamentos e migrações", 3),
    ("PostgreSQL", "dados", 60, "Banco relacional usado em produção", 4),
    ("SQLite", "dados", 75, "Banco do ambiente de desenvolvimento", 5),
    ("HTML5", "frontend", 90, "Marcação semântica e acessível", 6),
    ("CSS3", "frontend", 85, "Flexbox, Grid e layout responsivo", 7),
    ("JavaScript", "frontend", 70, "Interatividade, consumo de APIs, DOM", 8),
    ("Git e GitHub", "ferramentas", 80, "Versionamento e trabalho com branches", 9),
    ("Render e Vercel", "ferramentas", 65, "Deploy e publicação das aplicações", 10),
    ("Linux e Shell", "ferramentas", 60, "Terminal, scripts e automações simples", 11),
    ("APIs REST", "backend", 65, "Integração e consumo de serviços externos", 12),
]

PROJETOS = [
    {
        "titulo": "Controle Financeiro Familiar",
        "resumo": "Aplicação para registrar e acompanhar as despesas da família.",
        "descricao": (
            "Projeto que nasceu de uma necessidade real da minha casa: saber para onde "
            "o dinheiro está indo. A aplicação registra despesas por categoria e mostra "
            "o acumulado do período, com interface simples o suficiente para qualquer "
            "pessoa da família usar no celular.\n"
            "Foi aqui que eu praticei organização de estado, validação de entrada de "
            "dados e formatação de valores em moeda."
        ),
        "linguagem": "JavaScript",
        "tecnologias": "JavaScript, HTML5, CSS3",
        "repositorio": "https://github.com/JuniorSilva88/controle-financeiro-familiar",
        "ano": 2025,
        "destaque": True,
        "ordem": 1,
    },
    {
        "titulo": "Luxyberry",
        "resumo": "Site oficial de um negócio artesanal australiano de morangos com chocolate.",
        "descricao": (
            "Site institucional para a _luxyberry, marca australiana especializada em "
            "caixas personalizadas de morangos cobertos com chocolate.\n"
            "Trabalhei a identidade visual da marca no layout, a vitrine de produtos e o "
            "caminho até o contato/pedido. Projeto com cliente real, o que me obrigou a "
            "pensar em prazo, revisão e conteúdo de verdade — não só código."
        ),
        "linguagem": "JavaScript",
        "tecnologias": "JavaScript, HTML5, CSS3, Responsivo",
        "repositorio": "https://github.com/JuniorSilva88/luxyberry",
        "ano": 2025,
        "destaque": True,
        "ordem": 2,
    },
    {
        "titulo": "Rio Sul Refrigeração",
        "resumo": "Site comercial para empresa de refrigeração e câmara fria.",
        "descricao": (
            "Site para a Rio Sul Refrigeração apresentar serviços, área de atuação e "
            "canais de contato. Estruturei as seções pensando em quem chega pelo "
            "celular procurando assistência urgente: serviço, prova social e botão de "
            "contato sempre à mão."
        ),
        "linguagem": "HTML",
        "tecnologias": "HTML5, CSS3, JavaScript",
        "repositorio": "https://github.com/JuniorSilva88/Rio-Sul-Refrigeracao-2025",
        "ano": 2025,
        "destaque": True,
        "ordem": 3,
    },
    {
        "titulo": "Previsão do Tempo",
        "resumo": "Aplicação que consome a API do OpenWeather e mostra a previsão por cidade.",
        "descricao": (
            "Aplicação front-end que consulta a API do OpenWeather e exibe temperatura, "
            "condição do tempo e detalhes da cidade pesquisada.\n"
            "Meu primeiro contato mais sério com consumo de API: requisição assíncrona, "
            "tratamento de erro (cidade não encontrada, falha de rede) e estado de "
            "carregamento na interface."
        ),
        "linguagem": "CSS",
        "tecnologias": "JavaScript, API OpenWeather, HTML5, CSS3",
        "repositorio": "https://github.com/JuniorSilva88/previsao-do-tempo",
        "ano": 2024,
        "destaque": True,
        "ordem": 4,
    },
    {
        "titulo": "Nei do Vôlei — Pré-candidato",
        "resumo": "Site de campanha para pré-candidato a vereador de Curitiba.",
        "descricao": (
            "Página de campanha com proposta, trajetória e canais de contato do "
            "pré-candidato. O desafio foi comunicar muita informação de forma clara e "
            "com carregamento rápido, já que a maior parte dos acessos vinha de link "
            "compartilhado no WhatsApp, em rede móvel."
        ),
        "linguagem": "HTML",
        "tecnologias": "HTML5, CSS3, JavaScript",
        "repositorio": "https://github.com/JuniorSilva88/Nei-Do-Volei",
        "ano": 2024,
        "destaque": True,
        "ordem": 5,
    },
    {
        "titulo": "Ação entre Amigos",
        "resumo": "Landing page de ação beneficente, com versão de teste em Python.",
        "descricao": (
            "Landing page criada para divulgar uma ação beneficente: causa, prêmios, "
            "regras e como participar. Depois eu montei uma versão de teste em Python "
            "para experimentar a mesma ideia com lógica no servidor, gerando e "
            "controlando os números da ação."
        ),
        "linguagem": "Python",
        "tecnologias": "Python, HTML5, CSS3",
        "repositorio": "https://github.com/JuniorSilva88/Acao-Entre-Amigos",
        "ano": 2024,
        "ordem": 6,
    },
    {
        "titulo": "Extrator de Áudio v2",
        "resumo": "Script de linha de comando para extrair áudio de arquivos de vídeo.",
        "descricao": (
            "Segunda versão do meu extrator de áudio, escrito em Shell. Recebe arquivos "
            "de vídeo e devolve o áudio pronto, em lote.\n"
            "Projeto que me ensinou muito sobre terminal: argumentos, tratamento de "
            "caminhos com espaço, verificação de dependências antes de executar e "
            "mensagens de erro úteis."
        ),
        "linguagem": "Shell",
        "tecnologias": "Shell Script, FFmpeg, Linux",
        "repositorio": "https://github.com/JuniorSilva88/audio-extractor-v2",
        "ano": 2025,
        "ordem": 7,
    },
    {
        "titulo": "Segurança de Dados em Sistemas Financeiros com GenAI",
        "resumo": "Caderno temático do desafio DIO/Bradesco usando NotebookLM.",
        "descricao": (
            "Projeto desenvolvido para o desafio da DIO na trilha 'Dados e "
            "Cibersegurança GenAI' (Bradesco), usando o NotebookLM como ferramenta de "
            "aprendizagem ativa.\n"
            "Organizei fontes, resumos e mapas do tema segurança de dados em sistemas "
            "financeiros. Reforçou algo que eu levo para o código: documentar bem é "
            "parte do trabalho técnico."
        ),
        "linguagem": "Documentação",
        "tecnologias": "GenAI, NotebookLM, Segurança de Dados, Markdown",
        "repositorio": (
            "https://github.com/JuniorSilva88/"
            "Caderno-Tem-tico-NotebookLM-Seguran-a-de-Dados-em-Sistemas-Financeiros-com-GenAI"
        ),
        "ano": 2025,
        "ordem": 8,
    },
    {
        "titulo": "Relâmpago Marquinhos Carros",
        "resumo": "Catálogo de veículos para loja de carros.",
        "descricao": (
            "Catálogo em grade com foto, modelo, ano e detalhes de cada veículo, mais o "
            "contato direto com a loja. Aqui eu treinei bastante CSS Grid e cards "
            "reutilizáveis, mantendo o mesmo componente para todos os carros."
        ),
        "linguagem": "HTML",
        "tecnologias": "HTML5, CSS3, CSS Grid",
        "repositorio": "https://github.com/JuniorSilva88/Relampago-Marquinhos-Carros",
        "ano": 2024,
        "ordem": 9,
    },
    {
        "titulo": "Calculadora de Partidas Rankeadas",
        "resumo": "Desafio de lógica em JavaScript proposto na DIO.",
        "descricao": (
            "Programa que recebe vitórias e derrotas, calcula o saldo e devolve o nível "
            "do jogador. Simples no resultado, mas foi ótimo para eu treinar condicionais "
            "encadeadas, funções puras e testar cada faixa de nível."
        ),
        "linguagem": "JavaScript",
        "tecnologias": "JavaScript, Lógica de Programação",
        "repositorio": "https://github.com/JuniorSilva88/Calculadora-de-Partidas-Rankeadas",
        "ano": 2024,
        "ordem": 10,
    },
    {
        "titulo": "Notícias CWB",
        "resumo": "Portal de notícias com layout editorial em HTML e CSS.",
        "descricao": (
            "Portal de notícias fictício de Curitiba, montado para eu praticar "
            "hierarquia editorial: manchete principal, chamadas secundárias, colunas "
            "laterais e leitura confortável em telas pequenas."
        ),
        "linguagem": "HTML",
        "tecnologias": "HTML5, CSS3, Layout Editorial",
        "repositorio": "https://github.com/JuniorSilva88/Noticias-CWB",
        "ano": 2023,
        "ordem": 11,
    },
    {
        "titulo": "Museu Nacional",
        "resumo": "Site institucional criado com HTML5 e CSS3.",
        "descricao": (
            "Site sobre o Museu Nacional, um dos meus primeiros projetos maiores de "
            "front-end. Estruturei história, acervo e visitação em seções semânticas — "
            "foi onde a diferença entre 'div para tudo' e HTML semântico ficou clara "
            "para mim."
        ),
        "linguagem": "HTML",
        "tecnologias": "HTML5, CSS3",
        "repositorio": "https://github.com/JuniorSilva88/Museu-Nacional",
        "ano": 2023,
        "ordem": 12,
    },
]


class Command(BaseCommand):
    """Popula o banco com o conteúdo do portfólio."""

    help = "Carrega perfil, habilidades e projetos do portfólio no banco de dados."

    def add_arguments(self, parser):
        """Declaro as opções da linha de comando."""
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga habilidades e projetos antes de carregar novamente.",
        )
        parser.add_argument(
            "--github",
            action="store_true",
            help="Busca os repositórios ao vivo na API pública do GitHub.",
        )

    def handle(self, *args, **opcoes):
        """Ponto de entrada do comando."""
        if opcoes["limpar"]:
            Projeto.objects.all().delete()
            Habilidade.objects.all().delete()
            self.stdout.write(self.style.WARNING("Conteúdo anterior apagado."))

        self._carregar_perfil()
        self._carregar_habilidades()

        if opcoes["github"]:
            self._carregar_projetos_do_github()
        else:
            self._carregar_projetos_curados()

        self.stdout.write(self.style.SUCCESS("Conteúdo do portfólio carregado."))

    # -- passos individuais -------------------------------------------------

    def _carregar_perfil(self):
        """Crio ou atualizo o perfil único do site."""
        perfil = Perfil.objects.first()
        if perfil:
            for campo, valor in PERFIL.items():
                setattr(perfil, campo, valor)
            perfil.save()
        else:
            Perfil.objects.create(**PERFIL)
        self.stdout.write("Perfil atualizado.")

    def _carregar_habilidades(self):
        """Gravo a stack. A chave é o nome, então não duplica."""
        for nome, categoria, nivel, descricao, ordem in HABILIDADES:
            Habilidade.objects.update_or_create(
                nome=nome,
                defaults={
                    "categoria": categoria,
                    "nivel": nivel,
                    "descricao": descricao,
                    "ordem": ordem,
                    "publicado": True,
                },
            )
        self.stdout.write(f"{len(HABILIDADES)} habilidades gravadas.")

    def _carregar_projetos_curados(self):
        """Gravo a lista que eu escrevi à mão (com descrição de verdade)."""
        for dados in PROJETOS:
            slug = slugify(dados["titulo"])[:160]
            Projeto.objects.update_or_create(slug=slug, defaults={**dados, "slug": slug})
        self.stdout.write(f"{len(PROJETOS)} projetos gravados.")

    def _carregar_projetos_do_github(self):
        """Importo meus repositórios direto da API pública do GitHub.

        Uso só a biblioteca padrão (urllib) para não adicionar dependência
        por causa de um comando que roda uma vez.
        """
        url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated"
        requisicao = urllib.request.Request(
            url, headers={"Accept": "application/vnd.github+json", "User-Agent": "portfolio"}
        )

        try:
            with urllib.request.urlopen(requisicao, timeout=20) as resposta:
                repositorios = json.loads(resposta.read().decode("utf-8"))
        except Exception as erro:  # rede é instável: falho com aviso, não com stacktrace
            self.stderr.write(self.style.ERROR(f"Não consegui falar com o GitHub: {erro}"))
            self.stdout.write("Caindo para a lista curada.")
            return self._carregar_projetos_curados()

        importados = 0
        for repo in repositorios:
            if repo.get("fork") or repo.get("archived"):
                continue  # não mostro fork nem repositório arquivado

            titulo = repo["name"].replace("-", " ").strip()
            slug = slugify(repo["name"])[:160]
            descricao = repo.get("description") or "Projeto pessoal de estudo e prática."

            Projeto.objects.update_or_create(
                slug=slug,
                defaults={
                    "titulo": titulo,
                    "slug": slug,
                    "resumo": descricao[:220],
                    "descricao": descricao,
                    "linguagem": repo.get("language") or "",
                    "tecnologias": ", ".join(repo.get("topics", [])),
                    "repositorio": repo["html_url"],
                    "demo": repo.get("homepage") or "",
                    "ano": int(repo["updated_at"][:4]),
                    "publicado": True,
                },
            )
            importados += 1

        self.stdout.write(f"{importados} repositórios importados do GitHub.")
