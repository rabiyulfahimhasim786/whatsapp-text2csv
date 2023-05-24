from django import forms

from . models import whatsapp,Film
# import django_filters

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


class DateChoiceField(forms.Form):

    datesdata = forms.ModelChoiceField(
        queryset=Film.objects.values_list("title", flat=True).distinct(),
        #empty_label=None
    )


# class EventFilterForm(forms.Form):
#     # date = forms.DateField()

#     def filter_events(self):
#         filtered_date = self.cleaned_data['title']
#         events = Film.objects.filter(date=filtered_date)
#         return events