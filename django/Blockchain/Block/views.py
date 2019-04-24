from django.shortcuts import render
import requests
from .models import Block
from .forms import BlockForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


import json

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

#@csrf_exempt is required for making post requests
@csrf_exempt
def BlockView(request):
    block = ""
    hashVal = ""
    context = {"Block" : "Test"}

    if request.method == 'POST':
        block = request.POST.get("block")
        hashVal = request.POST.get("hash")
        context = {"Block" : "{0},{1}".format(block,hashVal)}
    return JsonResponse(context)

def TransactionView(request):
    return JsonResponse(context)

    '''block_list = []
    for block in range(0,10):

        myBlock = {

        }
        block_list.append(myBlock)
    context = {'Blocks': block_list}'''
