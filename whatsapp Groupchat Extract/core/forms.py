from django import forms

from . models import whatsapp


class WhatsappForm(forms.ModelForm):
    class Meta:
        model = whatsapp
        fields = ('chat',)