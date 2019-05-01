from django.forms import ModelForm, TextInput
from .models import Block

class BlockForm(ModelForm):
    class Meta:
        model = Block
        fields = ['height','hashValue']
        widgets = {'height':TextInput(attrs={'class': 'input','placeholder': 'Block'}),
                   'hashValue':TextInput(attrs={'class': 'input','placeholder': 'Hash'})}
