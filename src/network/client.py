# PKChain Client

import socket
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20

import pickle as pickle

from net import Net

import base64


class Client(object):
    blockchain = []

    def __init__(self, name, addr="0.0.0.0", port=1234):
        '''
            Initialize a Client object

            :param str name: A canonical name
            :param str addr: The ip address for serving inbound connections
            :param int port: The port for serving inbound connections
        '''
        self.name = name
        self.net = Net(name=name, addr=addr, port=port, bind=True)

        # Poll for node connections and connect to the network
        # print("Connecting to the PKChain network...")
        # self.connect_to_network(self.host, self.port)

        # Update the blockchain
        print("Updating blockchain. This may take a while.")
        self.blockchain = self.update_blockchain()
        print("Finished updating blockchain.")

    def send_transaction(self, t):
        '''
            Send a transaction to the validator network

            :param Transaction t: The transaction to send
        '''
        pass

    def update_blockchain(self):
        '''
            Update blockchain to be current
        '''
        return []

    @staticmethod
    def generate_keys():
        '''
            Generate public and private keys using RSA key generation
        '''
        # Specify the IP size of the key modulus
        modulus_lenght = 256 * 4
        # Using a Random Number Generator and the modulus length as parameters
        # For the RSA key generation, create your private key
        private_key = RSA.generate(modulus_lenght, Random.new().read)
        # Generate a public key from the private key we just created
        public_key = private_key.publickey()
        return private_key, public_key

    @staticmethod
    def encrypt_message(a_message, public_key):
        '''
            Encrypt and sign a message
        '''
        #Serialize message object
        serialized_message = pickle.dump(a_message)
        # Set your public key as an encrpytor that will be using the PKCS1_OAEP cipher
        encryptor = PKCS1_OAEP.new(public_key)
        # Encrypt a message using your encryptor
        encrypted_msg = encryptor.encrypt(serialized_message)
        # Encode your message using Base64 Encodings
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
        return encoded_encrypted_msg

    @staticmethod
    def decrypt_message(encoded_encrypted_msg, private_key):
        '''
            Decrypt and verify a message
        '''

        # Set your public key as a decrpytor that will be using the PKCS1_OAEP cipher
        decryptor = PKCS1_OAEP.new(private_key)
        # Decrypt a message using your decryptor
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        # Decode your message using Base64 Encodings
        decoded_decrypted_msg = decryptor.decrypt(decoded_encrypted_msg)
        #Dserialize message object
        deserialized_message = pickle.dump(decoded_decrypted_msg)
        return deserialized_message

    def close(self):
        '''
            Close the client and its net
        '''
        if self.net:
            self.net.close()


if __name__ == "__main__":
    # Generates private and public key
    ##    private_key, public_key = Client.generate_keys()
    ##    print(private_key, public_key)
    ##
    ##    message = b'This will be my test message'
    # Encrypt a message using the public key
    ##    encoded = Client.encrypt_message(message, public_key)
    # print(encoded)
    # Decrypt a message using the private key
    ##    decoded = Client.decrypt_message(encoded, private_key)
    # print(decoded)

    Client1 = Client(name="Client 1")

    # Finished set up, enter command loop
    print("PKChain Client successfully set up. Type 'help' for a list of commands")
    while True:
        command = input(">>> ").split(" ")
        if command[0] == 'help':
            print()
            print(
                "generate                           -Generate a public and private key pair.")
            print(
                "encrypt <public_key> <message>     -Encrypt a message with a public key.")
            print(
                "decrypt <private_key> <message>    -Decrypt a message with a private key.\n")
        elif command[0] == 'exit':
            Client1.close()
            break
        elif command[0] == 'generate':
            private_key, public_key = Client1.generate_keys()
            print()
            print("Your public key is:\n\n",
                  public_key.export_key().decode(), "\n\n")
            print("Your private key is:\n\n",
                  private_key.export_key().decode(), "\n\n")
        elif command[0] == 'encrypt':
            print("Implementation coming soon.")
        elif command[0] == 'decrypt':
            print("Implementation coming soon.")
        else:
            print("\nCommand not understood. Type 'help' for a list of commands.\n")
