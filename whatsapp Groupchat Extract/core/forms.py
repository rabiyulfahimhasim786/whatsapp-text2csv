from django import forms

from . models import whatsapp,Film


class WhatsappForm(forms.ModelForm):
    class Meta:
        model = whatsapp
        fields = ('chat',)


class FilmForm(forms.ModelForm):
    class Meta:
        model=Film
        fields="__all__"