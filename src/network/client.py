# PKChain Client

import socket
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20
import base64

class Client(object):
    blockchain = []
    sock = None
    port = 1234
    host = '10.101.99.92'

    
    def __init__(self):
        # print welcome message and initialize a socket
        print("PKChain Client initialized.")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Poll for node connections and connect to the network
        print("Connecting to the PKChain network...")
        #self.connect_to_network(self.host, self.port)

        # Update the blockchain
        print("Updating blockchain. This may take a while.")
        self.blockchain = self.update_blockchain()
        print("Finished updating blockchain.")

        # Finished set up, enter command loop
        print("PKChain Client successfully set up. Type 'help' for a list of commands")
        while True:
            command = input(">>> ").split(" ")
            if command[0] == 'help':
                print()
                print("generate                           -Generate a public and private key pair.")
                print("encrypt <public_key> <message>     -Encrypt a message with a public key.")
                print("decrypt <private_key> <message>    -Decrypt a message with a private key.\n")
            elif command[0] == 'generate':
                private_key, public_key = self.generate_keys()
                print()
                print("Your public key is: ", public_key, "\n")
                print("Your private key is: ", private_key, "\n")
            elif command[0] == 'encrypt':
                print("Implementation coming soon.")
            elif command == 'decrypt':
                print("Implementation coming soon.")
            else:
                print("\nCommand not understood. Type 'help' for a list of commands.\n")
                
        
    # connect to the p2p network
    def connect_to_network(self, host, port):
        try:
            self.sock.connect((host, port))
            print("Successfully connected to the network")
        except Exception as e:
            print(e)


    # update the blockchain to be current
    def update_blockchain(self):
        return []


    # generate a public/private key pair
    def generate_keys(self):
        modulus_lenght = 256 * 4
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        public_key = private_key.publickey()
        return private_key, public_key


    # encrypt a message with private key
    def encrypt_private_key(self, a_message, private_key):
        encryptor = Salsa20.new(private_key)
        encrypted_msg = encryptor.encrypt(a_message)
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
        return encoded_encrypted_msg


    # decrypt a message
    def decrypt_public_key(self, encoded_encrypted_msg, public_key):
        encryptor = Salsa20.new(public_key)
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
        return decoded_decrypted_msg


#private_key, public_key = Client.generate_keys()
#print(private_key,public_key)
#message = b'This will be my test message'

#encoded = Client.encrypt_private_key(message, private_key)
#decoded = Client.decrypt_public_key(encoded, public_key)
#print(decoded)

example = Client()
