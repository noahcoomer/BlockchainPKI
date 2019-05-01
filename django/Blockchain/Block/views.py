from django.shortcuts import render
import requests
#rom .models import Block
from .forms import BlockForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from os.path import expanduser

from .block import Block

import json
import os
import pickle

# Create your views here.
@csrf_exempt
def index(request):

    block_path = expanduser("~")
    block_path = os.path.join(block_path, ".BlockchainPKI/chain/")

    blx = []

    for filename in os.listdir(block_path):
        if filename.endswith(".blk"):
            f = open(block_path + filename, 'rb')
            blx.append(pickle.load(f))

    print(blx)

    if request.method == 'POST':

        print("Hit the post method")
        form = BlockForm(request.POST)
        form.save()

    form = BlockForm()

    blocks = []

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
        form = BlockForm(request.POST)
        form.save()
        block = request.POST.get("block")
        hashVal = request.POST.get("hash")
        context = {"Block" : "{0},{1}".format(block,hashVal)}

    return render(request, 'Block_Templates/block.html', context)

def TransactionView(request):
    return JsonResponse(context)

    '''block_list = []
    for block in range(0,10):

        myBlock = {

        }
        block_list.append(myBlock)
    context = {'Blocks': block_list}'''
