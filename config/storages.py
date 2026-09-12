"""
Armazenamento dos arquivos estáticos.

O WhiteNoise com manifest é ótimo em produção: cada arquivo ganha um hash no
nome, então o navegador pode cachear para sempre sem risco de servir CSS
velho depois de um deploy.

O problema é que o modo "strict" quebra a página inteira se um arquivo não
estiver no manifesto — o que acontece quando eu rodo os testes ou o servidor
antes do collectstatic. Por isso eu desligo o strict: se faltar entrada no
manifesto, o Django devolve a URL normal em vez de estourar erro.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class EstaticosTolerantes(CompressedManifestStaticFilesStorage):
    """Mesmo comportamento do WhiteNoise, mas sem quebrar sem manifesto."""

    manifest_strict = False
