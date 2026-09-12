# Arquitetura

Documento onde eu registro **como** o projeto está montado e **por que** cada
decisão foi tomada. Serve para eu me lembrar daqui a seis meses e para quem for
avaliar o código entender o raciocínio.

---

## 1. Visão geral

```
Navegador
   │  HTTP
   ▼
WhiteNoise ──► arquivo estático existe? ──► devolve CSS/JS/imagem
   │ não
   ▼
Django (config/urls.py)
   │
   ├── /admin/         → Django admin
   ├── /healthz/       → JsonResponse simples
   └── / …             → portfolio/urls.py
                            │
                            ▼
                    View (Class-Based View)
                            │
                    QuerySet do modelo (publicados/destaques)
                            │
                            ▼
                    Template (base.html + página)
                            │
                            ▼
                        HTML pronto
```

Padrão do Django: **MTV** (Model – Template – View). O que eu acrescentei foi
um QuerySet próprio para os filtros e um context processor para os dados que
aparecem em todas as páginas.

---

## 2. Separação de responsabilidades

| Pasta / arquivo             | Responsabilidade                                        |
| --------------------------- | ------------------------------------------------------- |
| `config/`                   | Configuração e rotas raiz. Não conhece regra de negócio.|
| `portfolio/models.py`       | Dados e regras que pertencem ao dado (slug, listas).    |
| `portfolio/views.py`        | Orquestra: pega dados, escolhe template.                |
| `portfolio/forms.py`        | Validação da entrada do usuário.                        |
| `templates/`                | Apresentação. Sem lógica de negócio.                    |
| `static/`                   | Estilo e comportamento no cliente.                      |
| `portfolio/management/`     | Tarefas de linha de comando (carga de conteúdo).        |

A regra que eu sigo: **se a lógica pertence ao dado, ela mora no modelo**. Por
isso `slug`, `lista_tecnologias`, `paragrafos_bio` e os filtros
(`publicados()`, `destaques()`) estão em `models.py` e não espalhados pelas
views.

---

## 3. Modelos

### Perfil

Tabela de uma linha só, com meus dados pessoais. O admin bloqueia a criação de
um segundo registro (`has_add_permission`). Properties:

- `paragrafos_bio` — quebra a bio em parágrafos para o template só iterar.
- `iniciais` — monograma do nome.

### Habilidade

Tecnologia com `categoria` (TextChoices: back-end, front-end, dados,
ferramentas), `nivel` de 0 a 100 e `ordem` manual de exibição. A view agrupa
por categoria em Python — a lista é pequena, então agrupar na aplicação sai
mais barato que uma consulta por categoria.

### Projeto

O centro do portfólio. Destaques do modelo:

- `slug` único, gerado automaticamente no `save()` se eu deixar em branco.
- `get_absolute_url()` — assim o template e o admin nunca montam URL na mão.
- `tecnologias` como string separada por vírgula, convertida em lista pela
  property `lista_tecnologias`. Escolhi isso em vez de uma tabela de tags
  porque não preciso filtrar por tag no banco — seria complexidade sem uso.
- Flags `publicado` e `destaque`, com índice composto pensado exatamente na
  consulta que a home faz.

### Mensagem

O que chega pelo formulário de contato. Gravo no banco em vez de disparar
e-mail: não depende de SMTP configurado e nada se perde. No admin é somente
leitura.

---

## 4. QuerySet reaproveitável

```python
class Publicado(models.QuerySet):
    def publicados(self):
        return self.filter(publicado=True)

    def destaques(self):
        return self.publicados().filter(destaque=True)


class Projeto(models.Model):
    objects = Publicado.as_manager()
```

Vantagem prática: o filtro de visibilidade existe em **um** lugar. Se eu mudar
a regra (por exemplo, incluir data de publicação), não preciso caçar `filter()`
espalhado por cinco views — e não corro o risco de esquecer um e vazar
rascunho.

---

## 5. Views

| View                | Base           | O que eu sobrescrevi                                  |
| ------------------- | -------------- | ----------------------------------------------------- |
| `HomeView`          | `TemplateView` | `get_context_data` (destaques, stack agrupada, form)  |
| `ProjetoListView`   | `ListView`     | `get_queryset` (busca + filtro), `get_context_data`   |
| `ProjetoDetailView` | `DetailView`   | `get_queryset` (só publicados), relacionados          |
| `ContatoView`       | `FormView`     | `form_valid` (honeypot + mensagem de sucesso)         |
| `DocumentacaoView`  | `TemplateView` | nada — é conteúdo estático                            |

Usei Class-Based Views porque paginação, busca de objeto por slug e tratamento
de formulário já vêm resolvidos. Eu escrevo só a diferença.

Detalhe de robustez na home: se eu ainda não marquei nenhum projeto como
destaque, ela mostra os primeiros publicados. A seção nunca aparece vazia.

Fluxo do formulário: **POST → redirect → GET** (com `django.contrib.messages`).
Assim, atualizar a página depois de enviar não reenvia a mensagem.

---

## 6. Templates

```
base.html                      ← fontes, metatags, header, rodapé, blocos
 ├── portfolio/home.html
 ├── portfolio/projetos.html   ← inclui partials/card_projeto.html
 ├── portfolio/projeto_detalhe.html
 ├── portfolio/contato.html
 ├── portfolio/documentacao.html
 ├── 404.html
 └── 500.html
```

- Um único `base.html`: mudar o header muda o site todo.
- `partials/card_projeto.html` é o **mesmo** card na home e na listagem.
- Nada de URL escrita na mão: sempre `{% url 'portfolio:...' %}`.
- Comentários multilinha usam `{% comment %}` (o `{# #}` do Django vale só para
  uma linha — aprendi na prática).

---

## 7. Front-end

### CSS (`static/css/main.css`)

Organizado em sete blocos comentados: tokens, reset, layout, componentes,
páginas, responsivo, acessibilidade.

- Toda cor e todo espaçamento saem de variáveis CSS. Trocar a paleta é mexer
  em um bloco.
- Tema escuro redefine só os papéis semânticos (`--fundo`, `--texto`,
  `--destaque`); nenhum componente precisa saber que o tema mudou.
- Tipografia e espaçamento com `clamp()` — responsivo sem media query.
- Grades com `repeat(auto-fill, minmax(min(100%, 300px), 1fr))`: o navegador
  decide o número de colunas.
- Só dois breakpoints (900px e 720px), porque o resto o layout fluido resolve.

### JavaScript (`static/js/main.js`)

JavaScript puro, dentro de uma IIFE com `"use strict"`, dividido em quatro
blocos: tema, menu mobile, animações e link ativo.

Decisões que valem registro:

- **Ganchos são `data-*`**, nunca classe de CSS. Renomear uma classe por estilo
  não quebra o script.
- **`IntersectionObserver`** em vez de escutar `scroll`: o navegador avisa
  quando o elemento entra na tela, sem rodar código a cada pixel.
- **Sem JavaScript o site continua legível**: o script inline adiciona a classe
  `js` ao `<html>` e só então o CSS esconde os blocos animados.
- **`toggleAttribute`** para alternar os ícones de sol/lua — SVG não implementa
  a propriedade `.hidden` do HTML, só o atributo funciona nos dois casos.
- **Tema em memória**, não em `localStorage`: em pré-visualização dentro de
  iframe o `localStorage` é bloqueado e estouraria erro. Ao recarregar, volto a
  respeitar a preferência do sistema.

---

## 8. Estáticos

`WhiteNoise` serve os arquivos pela própria aplicação, com compressão e hash no
nome do arquivo (cache eterno sem risco de servir versão velha).

Criei `config/storages.py` com `manifest_strict = False`: sem isso, rodar os
testes ou o servidor antes do `collectstatic` derruba a página com
"Missing staticfiles manifest entry".

---

## 9. Segurança

- `SECRET_KEY`, `DEBUG` e hosts vindos do ambiente; `.env` fora do Git.
- Com `DEBUG=False`: HSTS (30 dias), `SECURE_SSL_REDIRECT`, cookies de sessão e
  CSRF apenas por HTTPS, `nosniff`, `X_FRAME_OPTIONS=SAMEORIGIN`.
- `SECURE_PROXY_SSL_HEADER` configurado — Render e Vercel ficam atrás de proxy;
  sem isso o Django entra em loop de redirect.
- `CSRF_TRUSTED_ORIGINS` com os domínios das duas plataformas.
- Honeypot no formulário e validação de tamanho mínimo da mensagem.
- Rascunho (`publicado=False`) retorna 404 mesmo por URL direta — tem teste
  cobrindo isso.

---

## 10. Decisões que eu tomei de propósito

| Decisão                                | Por que                                                                 |
| -------------------------------------- | ----------------------------------------------------------------------- |
| Sem framework de front-end             | O site é pequeno; React/Vue seria peso sem ganho.                       |
| Sem Tailwind                           | Quis mostrar domínio de CSS puro e design system em variáveis.          |
| `tecnologias` como texto, não tabela   | Não preciso consultar por tag no banco; simplicidade ganha.             |
| Mensagem no banco, não e-mail          | Não depende de SMTP e nada se perde.                                    |
| Conteúdo no banco, não no template     | Atualizo pelo admin, sem novo deploy.                                   |
| Duas plataformas de deploy             | Render como ambiente completo; Vercel como vitrine rápida.              |
| Comentário explicando o "porquê"       | Comentário que só repete o código não ajuda ninguém.                    |

---

## 11. O que eu faria em uma próxima versão

- Blog em Markdown como segundo app.
- Cache de página com Redis, se o tráfego crescer.
- API REST com Django REST Framework para consumir o portfólio de outros lugares.
- GitHub Actions rodando `test` e `check --deploy` em cada push.
- Sitemap e feed RSS usando os apps que já vêm no Django.
