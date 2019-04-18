from django.shortcuts import render
import requests
from .models import Block
from .forms import BlockForm

# Create your views here.
def index(request):

    if request.method == 'POST':
        form = BlockForm(request.POST)
        form.save()

    form = BlockForm()

    blocks = Block.objects.all()

    context = {
        'blocks' : blocks,
        'form' : form
        }

    return render(request, 'Block_Templates/block.html', context)
