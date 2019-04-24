import requests
import json
from django.views.decorators.csrf import csrf_exempt

#@csrf_exempt is required for making post requests
@csrf_exempt
def addBlock():
    blockInput = input("Enter block ID: \n")
    hashInput = input("Enter hash:  \n")
    p = {
        "block":"{0}".format(blockInput),
        "hash":"{0}".format(hashInput),
         }
    r = requests.post("http://127.0.0.1:8000/block", data=p)
    data = r.json()
    print(data)

    return

addBlock()
