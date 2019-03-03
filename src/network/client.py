
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20

import base64


class Client(object):
    def __init__(self):
        pass

    def generate_keys(self):
        modulus_lenght = 256 * 4
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        public_key = private_key.publickey()
        return private_key, public_key

    def encrypt_private_key(self, a_message, private_key):
        encryptor = Salsa20.new(private_key)
        encrypted_msg = encryptor.encrypt(a_message)
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
        return encoded_encrypted_msg

    def decrypt_public_key(self, encoded_encrypted_msg, public_key):
        encryptor = Salsa20.new(public_key)
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
        return decoded_decrypted_msg


if __name__ == "__main__":
    client = Client()

    private_key, public_key = client.generate_keys()
    print(private_key, public_key)
    message = b'This will be my test message'

    encoded = client.encrypt_private_key(message, private_key)
    decoded = client.decrypt_public_key(encoded, public_key)
    print(decoded)
