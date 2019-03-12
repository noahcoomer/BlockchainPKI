# PKChain Client

import socket
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20


class Client(object):
    blockchain = []
    sock = None
    port = 1234
    host = 'localhost'

    
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
            elif command[0] == 'exit':
                break
            elif command[0] == 'generate':
                private_key, public_key = self.generate_keys()
                print()
                print("Your public key is:\n\n", public_key.export_key().decode(), "\n\n")
                print("Your private key is:\n\n", private_key.export_key().decode(), "\n\n")
            elif command[0] == 'encrypt':
                print("Implementation coming soon.")
            elif command == 'decrypt':
                print("Implementation coming soon.")
            else:
                print("\nCommand not understood. Type 'help' for a list of commands.\n")

        self.sock.close()       
        
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


    # Method to generate public and private keys using RSA key generation
    @staticmethod
    def generate_keys():
        # Specify the IP size of the key modulus
        modulus_lenght = 256 * 4
        # Using a Random Number Generator and the modulus length as parameters
        # For the RSA key generation, create your private key
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        # Generate a public key from the private key we just created
        public_key = private_key.publickey()
        return private_key, public_key


    # Method to encrpyt and sign a message
    @staticmethod
    def encrypt_message(a_message, public_key):
        # Set your public key as an encrpytor that will be using the PKCS1_OAEP cipher
        encryptor = PKCS1_OAEP.new(public_key)
        # Encrypt a message using your encryptor
        encrypted_msg = encryptor.encrypt(a_message)
        # Encode your message using Base64 Encodings
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
        return encoded_encrypted_msg


    # Method to decrpyt and verify a message
    @staticmethod
    def decrypt_message(encoded_encrypted_msg, private_key):
        # Set your public key as a decrpytor that will be using the PKCS1_OAEP cipher
        decryptor = PKCS1_OAEP.new(private_key)
        # Decrypt a message using your decryptor
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        # Decode your message using Base64 Encodings
        decoded_decrypted_msg = decryptor.decrypt(decoded_encrypted_msg)
        return decoded_decrypted_msg


if __name__ == "__main__":
##    # Generates private and public key
##    private_key, public_key = Client.generate_keys()
##    print(private_key, public_key)
##
##    message = b'This will be my test message'
##    # Encrypt a message using the public key
##    encoded = Client.encrypt_message(message, public_key)
##    print(encoded)
##    # Decrypt a message using the private key
##    decoded = Client.decrypt_message(encoded, private_key)
##    print(decoded)

    example = Client()

