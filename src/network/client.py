
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20
import base64
#pip install pycryptodome

class Client(object):
    def __init__(self):
        pass

    def generate_keys():
        modulus_lenght = 256 * 4
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        public_key = private_key.publickey()
        return private_key, public_key


private_key, public_key = Client.generate_keys()
print(private_key,public_key)
