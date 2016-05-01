"""Custom Forms"""

from django import forms


class CustomForm(forms.ModelForm):
    bar = forms.CharField(
        max_length=6, widget=forms.TextInput)
