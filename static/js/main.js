/* =========================================================================
   main.js — comportamentos do portfólio
   =========================================================================
   Escrevi tudo em JavaScript puro, sem framework nem biblioteca: o site é
   pequeno e não vale a pena carregar 100 KB para três interações.

   O que tem aqui:
   1. Alternar tema claro/escuro
   2. Menu mobile (abre e fecha)
   3. Animação das barras de habilidade e revelação de seções ao rolar
   4. Marcar no menu a seção que está na tela

   Uso IIFE ("use strict") para não vazar variável para o escopo global.
   ========================================================================= */

(function () {
  "use strict";

  /* -----------------------------------------------------------------------
     1. TEMA CLARO / ESCURO
     -----------------------------------------------------------------------
     Guardo a escolha em variável de memória (e não em localStorage) porque
     em pré-visualizações dentro de iframe o localStorage fica bloqueado e
     estouraria erro. Ao recarregar, volto a respeitar o sistema.
  */

  var botaoTema = document.querySelector("[data-tema-toggle]");
  var raiz = document.documentElement;

  /** Descubro o tema que o sistema operacional do visitante prefere. */
  function temaDoSistema() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  /** Aplico o tema no <html> e atualizo o ícone/rótulo do botão. */
  function aplicarTema(tema) {
    raiz.setAttribute("data-theme", tema);
    if (!botaoTema) return;
    var escuro = tema === "dark";
    botaoTema.setAttribute("aria-label", escuro ? "Ativar tema claro" : "Ativar tema escuro");
    // Uso toggleAttribute (e não a propriedade .hidden) porque SVG não
    // implementa .hidden como o HTML: só o atributo funciona nos dois.
    botaoTema.querySelector("[data-icone-sol]").toggleAttribute("hidden", !escuro);
    botaoTema.querySelector("[data-icone-lua]").toggleAttribute("hidden", escuro);
  }

  aplicarTema(temaDoSistema());

  if (botaoTema) {
    botaoTema.addEventListener("click", function () {
      var atual = raiz.getAttribute("data-theme");
      aplicarTema(atual === "dark" ? "light" : "dark");
    });
  }

  /* -----------------------------------------------------------------------
     2. MENU MOBILE
     -----------------------------------------------------------------------
     Em vez de adicionar/remover classe, eu alterno o atributo data-aberto
     no header. O CSS cuida do resto e o aria-expanded mantém o leitor de
     tela informado.
  */

  var header = document.querySelector("[data-header]");
  var botaoMenu = document.querySelector("[data-menu-toggle]");

  if (header && botaoMenu) {
    botaoMenu.addEventListener("click", function () {
      var aberto = header.getAttribute("data-aberto") === "true";
      header.setAttribute("data-aberto", String(!aberto));
      botaoMenu.setAttribute("aria-expanded", String(!aberto));
    });

    // Ao clicar em um link do menu, fecho a gaveta — senão ela fica
    // cobrindo a seção para onde o visitante acabou de navegar.
    header.querySelectorAll(".nav__link").forEach(function (link) {
      link.addEventListener("click", function () {
        header.setAttribute("data-aberto", "false");
        botaoMenu.setAttribute("aria-expanded", "false");
      });
    });

    // Tecla Esc fecha o menu (padrão que todo mundo espera).
    document.addEventListener("keydown", function (evento) {
      if (evento.key === "Escape") {
        header.setAttribute("data-aberto", "false");
        botaoMenu.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* -----------------------------------------------------------------------
     3. ANIMAÇÕES AO ROLAR
     -----------------------------------------------------------------------
     Uso IntersectionObserver em vez de escutar o evento de scroll: o
     navegador avisa quando o elemento entra na tela, sem eu rodar código
     em cada pixel rolado (muito mais leve).
  */

  var animacaoReduzida = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // 3.1 Barras de habilidade: cresço de 0 até o nível vindo do banco.
  var barras = document.querySelectorAll("[data-nivel]");

  function preencherBarra(barra) {
    barra.style.width = barra.getAttribute("data-nivel") + "%";
  }

  if (animacaoReduzida) {
    // Quem pediu menos movimento vê o valor final direto.
    barras.forEach(preencherBarra);
  } else if ("IntersectionObserver" in window) {
    var observadorBarras = new IntersectionObserver(
      function (entradas, observador) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          preencherBarra(entrada.target);
          observador.unobserve(entrada.target); // anima uma vez só
        });
      },
      { threshold: 0.4 }
    );
    barras.forEach(function (barra) {
      observadorBarras.observe(barra);
    });
  } else {
    barras.forEach(preencherBarra); // navegador antigo: sem animação
  }

  // 3.2 Revelação suave de blocos marcados com a classe .revelar
  var reveláveis = document.querySelectorAll(".revelar");

  if (animacaoReduzida || !("IntersectionObserver" in window)) {
    reveláveis.forEach(function (elemento) {
      elemento.classList.add("visivel");
    });
  } else {
    var observadorRevelar = new IntersectionObserver(
      function (entradas, observador) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          entrada.target.classList.add("visivel");
          observador.unobserve(entrada.target);
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    reveláveis.forEach(function (elemento) {
      observadorRevelar.observe(elemento);
    });
  }

  /* -----------------------------------------------------------------------
     4. LINK ATIVO CONFORME A SEÇÃO NA TELA
     -----------------------------------------------------------------------
     Só vale para os links de âncora da home (#sobre, #stack, ...).
  */

  var linksAncora = Array.prototype.filter.call(
    document.querySelectorAll(".nav__link"),
    function (link) {
      return link.getAttribute("href").indexOf("#") === 0;
    }
  );

  if (linksAncora.length && "IntersectionObserver" in window) {
    var observadorSecoes = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          linksAncora.forEach(function (link) {
            var alvo = link.getAttribute("href") === "#" + entrada.target.id;
            // aria-current serve para o CSS e para a acessibilidade.
            if (alvo) {
              link.setAttribute("aria-current", "page");
            } else {
              link.removeAttribute("aria-current");
            }
          });
        });
      },
      // A seção conta como "ativa" quando está no meio da tela.
      { rootMargin: "-45% 0px -45% 0px" }
    );

    linksAncora.forEach(function (link) {
      var secao = document.querySelector(link.getAttribute("href"));
      if (secao) observadorSecoes.observe(secao);
    });
  }
})();
