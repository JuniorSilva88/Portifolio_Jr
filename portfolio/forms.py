"""
Formulários do portfólio.

Só tenho um: o de contato. Eu uso ModelForm porque a validação de e-mail,
tamanho de campo e mensagens de erro já vêm do modelo — menos código meu
para manter e menos chance de eu esquecer uma validação.
"""

from django import forms

from .models import Mensagem


class ContatoForm(forms.ModelForm):
    """Formulário de contato com honeypot simples contra robô."""

    # Campo invisível para humano. Robô costuma preencher tudo que acha;
    # se vier com conteúdo, eu descarto a mensagem sem dar pista.
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Mensagem
        fields = ["nome", "email", "assunto", "conteudo"]
        widgets = {
            # Coloco placeholder e classe CSS aqui para o template ficar
            # limpo, só com {{ campo }}.
            "nome": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Seu nome", "autocomplete": "name"}
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "campo",
                    "placeholder": "seu@email.com",
                    "autocomplete": "email",
                }
            ),
            "assunto": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Sobre o que quer falar?"}
            ),
            "conteudo": forms.Textarea(
                attrs={"class": "campo", "rows": 5, "placeholder": "Escreva sua mensagem..."}
            ),
        }
        labels = {"conteudo": "Mensagem"}

    def clean_conteudo(self) -> str:
        """Evito mensagem vazia de 3 letras só para testar o formulário."""
        conteudo = self.cleaned_data["conteudo"].strip()
        if len(conteudo) < 10:
            raise forms.ValidationError("Escreva um pouco mais (mínimo 10 caracteres).")
        return conteudo

    def eh_robo(self) -> bool:
        """True quando o honeypot foi preenchido — aí eu ignoro o envio."""
        return bool(self.cleaned_data.get("website"))
