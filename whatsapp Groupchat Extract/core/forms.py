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



class LocationChoiceField(forms.Form):

    locations = forms.ModelChoiceField(
        queryset=Film.objects.values_list("checkstatus", flat=True).distinct(),
        #empty_label=None
    )


class LabelChoiceField(forms.Form):

    label = forms.ModelChoiceField(
        queryset=Film.objects.values_list("dropdownlist", flat=True).distinct(),
        #empty_label=None
    )