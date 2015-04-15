from django import forms


class RabifyForm(forms.Form):
    a = forms.IntegerField(label='a')
    b = forms.IntegerField(label='b')
