"""Custom Forms"""

from django import forms


class CustomForm(forms.ModelForm):
    """Sample Custom form"""
    bar = forms.CharField(
        max_length=17, widget=forms.TextInput)
