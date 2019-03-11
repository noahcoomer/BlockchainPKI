from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
# pip install pycryptodome #pip install pycrypto


class Client(object):
    def __init__(self):
        pass

    #Method to generate public and private keys using RSA key generation
    @staticmethod
    def generate_keys():
        #Specify the IP size of the key modulus
        modulus_lenght = 256 * 4
        #Using a Random Number Generator and the modulus length as parameters
        #For the RSA key generation, create your private key
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        #Generate a public key from the private key we just created
        public_key = private_key.publickey()
        return private_key, public_key

    #Method to encrpyt and sign a message
    @staticmethod
    def encrypt_message(a_message, public_key):
        #Set your public key as an encrpytor that will be using the PKCS1_OAEP cipher
        encryptor = PKCS1_OAEP.new(public_key)
        #Encrypt a message using your encryptor
        encrypted_msg = encryptor.encrypt(a_message)
        #Encode your message using Base64 Encodings
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
        return encoded_encrypted_msg

    #Method to decrpyt and verify a message
    @staticmethod
    def decrypt_message(encoded_encrypted_msg, private_key):
        #Set your public key as a decrpytor that will be using the PKCS1_OAEP cipher
        decryptor = PKCS1_OAEP.new(private_key)
        #Decrypt a message using your decryptor
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        #Decode your message using Base64 Encodings
        decoded_decrypted_msg = decryptor.decrypt(decoded_encrypted_msg)
        return decoded_decrypted_msg

#Generates private and public key
private_key, public_key = Client.generate_keys()
print(private_key,public_key)

message = b'This will be my test message'
#Encrypt a message using the public key
encoded = Client.encrypt_message(message, public_key)
print(encoded)
#Decrypt a message using the private key
decoded = Client.decrypt_message(encoded, private_key)
print(decoded)
