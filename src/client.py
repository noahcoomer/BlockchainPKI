# PKChain Client

import socket
import base64
import json
import time
import pickle

from threading import Thread

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import Salsa20

import validator
import transaction
from net import Net


class Client(object):
    blockchain = None

    def __init__(self, name, addr="0.0.0.0", port=1234):
        '''
            Initialize a Client object

            :param str name: A canonical name
            :param str addr: The ip address for serving inbound connections
            :param int port: The port for serving inbound connections
        '''
        self.name = name
        # Create socket connection
        self.net = Net(name=name, addr=addr, port=port, bind=True)
        
        # Update the blockchain
        print("Updating blockchain. This may take a while.")
        self.blockchain = self.update_blockchain()
        print("Finished updating blockchain.")
        self.command_loop()

    def send_transaction(self, validator, tx):
        '''
            Send a transaction to the validator network

            :param Transaction tx: The transaction to send
        '''
        #
        if self.net and self != validator:
            # Connect to validators's inbound net using client's outbound net
            address = validator.address
            # Serialize the transaction as a bytes object
            txn = pickle.dumps(tx)
            # Create a new socket (the outbound net)
            print("Attempting to send to %s:%s" % validator.address)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setblocking(True)
                try:
                    # Connect to the validator
                    s.connect(address)
                    # Send the entirety of the message
                    s.sendall(txn)
                except OSError as e:
                    # Except cases for if the send fails
                    if e.errno == errno.ECONNREFUSED:
                        print(e)
                        # return -1, e
                except socket.error as e:
                    print(e)
        else:
            raise Exception(
                "The validator must be initialized and listening for connections")
        pass

    def update_blockchain(self):
        '''
            Update blockchain to be current
        '''
        return None


    def pki_register(self, generator_public_key, name, public_key):
        '''
            Creates a register transaction
            :params: name - name to be associated with public key
                     public_key - the public key to be added
            :return: tx - the transaction that was just generated
        '''

        # input verification
        if len(name) < 1 or len(name) > 255:
            print("The name value must be between 1-255 characters.")
            return -1

        # public key verification
        gen = self.verify_public_key(generator_public_key)
        if not gen:
            print("The generator public key is incorrectly formatted. Please try again.")
            return -1

        pub = self.verify_public_key(public_key)
        if not pub:
            print("The register public key is incorrectly formatted. Please try again.")
            return -1

        inputs = { "REGISTER" : { name : public_key } }

        # Validate that the name is not already in the blockchain, break if found
        flag = False
        for block in reversed(self.blockchain.chain):
            for tx in block.transactions:
                inp = json.loads(tx.inputs)
                for key in inp.keys():
                    try:
                        if name == inp[key]["name"]:
                            flag = True
                            break
                    except:
                        continue
                if flag == True:
                    break
            if flag == True:
                break

        outputs = dict()
        if flag == False:
            outputs = { "REGISTER" : { "success" : True } }
        else:
            outputs = { "REGISTER" :
                            {
                                "success" : False,
                                "message": "This name is already registered."
                            }
                      }

        # dump to JSON
        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)

        # send the transaction and return it for std.out
        tx = transaction.Transaction(transaction_type="Standard", tx_generator_address=generator_public_key, inputs=inputs, outputs=outputs)
        # Create an entry point to the validator network that the client can connect to

        ############## UNCOMMENT BEFORE GOING LIVE #################
        #validator = validator.Validator(Alice = name="Validator", addr="10.228.112.126", port=4321)
        #self.send_transaction(validator, tx)

        return tx


    def pki_query(self, generator_public_key, name):
        '''
            Query the blockchain for a public key given a name
        '''

        # input verification
        gen = self.verify_public_key(generator_public_key)
        if not gen:
            print("The generator public key is incorrectly formatted. Please try again.")
            return -1

        # Query blockchain, break if we find our public key
        public_key = None
        for block in reversed(self.blockchain.chain):
            for tx in block.transactions:
                inputs = json.loads(tx.inputs)
                for key in inputs.keys(): # should only be 1 top level key - still O(1)
                    try:
                        if name == inputs[key]["name"]:
                            public_key = inputs[key]["public_key"]
                    except:
                        continue
                if public_key:
                    break
            if public_key:
                break

        inputs = { "QUERY" : { "name" : name } }
        outputs = dict()
        if public_key:
            outputs = { "QUERY" : { "success": True, "query" : True, "public_key" : public_key } }
        else:
            outputs = { "QUERY" :
                            {
                                "success" : False,
                                "message" : "Name not found."
                            }
                      }

        # dump to JSON
        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)

        tx = transaction.Transaction(transaction_type="Standard", tx_generator_address=generator_public_key,
                                    inputs=inputs, outputs=outputs)

        ####### UNCOMMENT BEFORE PRODUCTION ########
        #self.send_transaction(tx)

        return tx


    def pki_validate(self, generator_public_key, name, public_key):
        '''

        '''
        tx = transaction.Transaction()

        self.send_transaction(tx)
        return tx


    def pki_update(self, name, old_public_key, new_public_key):
        '''

        '''
        tx = transaction.Transaction()

        self.send_transaction(tx)
        return tx


    def pki_revoke(self, public_key, private_key):
        '''

        '''
        tx = transaction.Transaction()

        self.send_transaction(tx)
        return tx


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
        # Set your public key as an encrpytor that will be using the PKCS1_OAEP cipher
        encryptor = PKCS1_OAEP.new(public_key)
        # Encrypt a message using your encryptor
        encrypted_msg = encryptor.encrypt(a_message)
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
        return decoded_decrypted_msg


    @staticmethod
    def verify_public_key(public_key):
        '''
            Verify a public key is correctly formatted by making an RSA key object
            :params: public_key - a string or byte string of the public key to imported
                    passphrase - if the key requires a passphrase use it, otherwise passphrase should be None
        '''
        try:
            key = RSA.import_key(public_key)
            return key
        except ValueError:
            return None


    def close(self):
        '''
            Close the client and its net
        '''
        if self.net:
            self.net.close()


    def command_loop(self):
        # Finished set up, enter command loop
        print("PKChain Client successfully set up. Type 'help' for a list of commands")
        while True:
            command = input(">>> ").split(" ")
            if command[0] == 'help':
                print("Transactional Functions:\n\n ")
                print("register                         -Register a name and public key on the blockchain.")
                print("query                            -Query for a public key given a name.\n\n")
                print("Local Functions:\n\n")
                print("generate                         -Generate a public and private key pair.")
                print("encrypt <public_key> <message>   -Encrypt a message with a public key.")
                print("decrypt <private_key> <message>  -Decrypt a message with a private key.\n\n")
            elif command[0] == 'exit':
                self.close()
                break
            elif command[0] == 'register':
                client_pub_key = input("Enter your public key (generator address):\n")
                name = input("Enter the name you would like to register to a public key: ")
                reg_pub_key = input("Enter the public key you would like to register:\n")
                tx = self.pki_register(client_pub_key, name, reg_pub_key)
                print("Inputs: ", json.loads(tx.inputs))
                print("Outputs: ", json.loads(tx.outputs))
            elif command[0] == 'query':
                client_pub_key = input("Enter your public key (generator address):\n")
                name = input("Enter the name you would like to query for: ")
                tx = self.pki_query(client_pub_key, name)
                print("Inputs: ", json.loads(tx.inputs))
                print("Outputs: ", json.loads(tx.outputs))
            elif command[0] == 'validate':
                pass
            elif command[0] == 'update':
                pass
            elif command[0] == 'revoke':
                pass
            elif command[0] == 'generate':
                private_key, public_key = self.generate_keys()
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
