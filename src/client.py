from node import Node
from validator import Validator
from blockchain import Blockchain
from transaction import Transaction

from Crypto import Random
from Crypto.PublicKey import RSA
from os.path import expanduser

import os
import ssl
import json
import time
import errno
import socket
import base64
import pickle


class Client(Node):
    def __init__(self, hostname=None, addr="0.0.0.0", port=4848, capath="~/.BlockchainPKI/validators/"):
        super().__init__(hostname=hostname, addr=addr, port=port, bind=True, capath=capath)

        self.blockchain = None
        self.connections = list()

    def create_connections(self):
        '''
            Create the connection objects from the validators info file and store them as a triple
            arr[0] = hostname, arr[1] = ip, int(arr[2]) = port
        '''
        f = open('../validators.txt', 'r')
        for line in f:
            arr = line.split(' ')
            if self.hostname == arr[0] and self.address == (arr[1], int(arr[2])):
                continue
            else:
                v = Validator(
                    name=arr[0], addr=arr[1], port=int(arr[2]), bind=False)
                self.connections.append(v)
        f.close()

    def broadcast_transaction(self, tx):
        '''
            Broadcast the creation of a transaction to the network
        '''
        for i in self.connections:
            self.message(i, tx)

    def message(self, v, tx):
        '''
            Sends a Transaction to a Validator

            :param Validator v: The validator to send to
            :param Transaction tx: The transaction to send
        '''
        if type(v) != Validator:
            raise TypeError("v must be of type Validator, not %s" % type(v))
        elif type(tx) != Transaction:
            raise TypeError(
                "tx must be of type Transaction, not %s" % type(tx))
       if self.net:
            address = v.address
            txn = pickle.dumps(tx)  # Serialize the transaction

            print("Attempting to send to %s:%s" % v.address)
            secure_conn = self.context.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=v.hostname)
            try:
                secure_conn.connect(address)  # Connect to the validator
                secure_conn.sendall(txn)  # Send the transaction
            except OSError as e:
                if e.errno == errno.ECONNREFUSED:
                    print(e)
            except socket.error as e:
                print(e)
            finally:
                secure_conn.close()
        else:
            raise Exception("Net must be initialized before calling message")

    def update_blockchain(self):
        '''
            Update blockchain to be current
        '''
        chain = Blockchain()
        return chain

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

        inputs = {"REGISTER": {name: pub}}

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
            outputs = {"REGISTER": {"success": True}}
        else:
            outputs = {"REGISTER":
                       {"success": False, "message": "This name is already registered."}}

        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)

        # send the transaction and return it for std.out
        tx = Transaction(
            transaction_type="Standard", tx_generator_address=gen, inputs=inputs, outputs=outputs)
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
                for key in inputs.keys():  # should only be 1 top level key - still O(1)
                    try:
                        if name == inputs[key]["name"]:
                            public_key = inputs[key]["public_key"]
                    except:
                        continue
                if public_key:
                    break
            if public_key:
                break

        inputs = {"QUERY": {"name": name}}
        outputs = dict()
        if public_key:
            outputs = {"QUERY": {"success": True, "public_key": public_key}}
        else:
            outputs = {"QUERY": {"success": False,
                                 "message": "Name not found."}}

        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)
        tx = Transaction(transaction_type="Standard", tx_generator_address=gen,
                                     inputs=inputs, outputs=outputs)
        return tx

    def pki_validate(self, generator_public_key, name, public_key):
        '''
            Checks whether the name and public key are valid
            Returns true if it is valid and false if it is not valid
        '''
        flag = False
        gen = self.verify_public_key(generator_public_key)
        if not gen:
            print("The generator public key is incorrectly formatted. Please try again.")
            return - 1

        pub = self.verify_public_key(public_key)
        if not pub:
            print("The register public key is incorrectly formatted. Please try again.")
            return -1

        if len(name) < 1 or len(name) > 255:
            print("The name value must be between 1-255 characters.")
            return -1
        flag = True

        inputs = {"VALIDATE": {"name": name,
                               "generator_public_key": gen, "public_key": pub}}

        outputs = dict()

        if flag == True:
            outputs = {"VALIDATE": {"success": True,
                                    "Validated": True, "name": name, "public_key": pub}}
        else:
            outputs = {"VALIDATE": {"success": False,
                                    "message": "cannot validate name and public key"}}

        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)
        tx = Transaction(
            transaction_type='standard', tx_generator_address=gen, inputs=inputs, outputs=outputs)
        return tx

    def pki_update(self, generator_public_key, name, old_public_key, new_public_key):
        '''
            Updates the public key with the new public key
            Returns the transaction with the new public key
        '''

        # verify the old_public_key
        old_key = self.verify_public_key(old_public_key)
        if not old_key:
            print('this old public key is not formatted correctly')
            return -1
        # verify the new_public_key
        new_key = self.verify_public_key(new_public_key)
        if not new_key:
            print('This new public key is not formatted correctly')
            return -1

        flag = False
        for block in self.blockchain.chain:
            for tx in block.transactions:
                inputs = json.loads(tx.inputs)
                for key in inputs.keys():
                    try:
                        if name == inputs[key]['name'] and old_public_key == inputs[key]['public_key']:
                            flag = True
                    except:
                        continue
                if flag == True:
                    break
            if flag == True:
                break

        # Create the input for the update, for the input we have the name, old_public_key and the new_public_key
        inputs = {"UPDATE": {"name": name,
                             "old_public_key": old_key, "new_public_key": new_key}}

        # Create the output for the update
        outputs = dict()
        if flag == True:
            outputs = {"UPDATE": {"success": True,
                                  "update": True, "new_public_key": new_key}}
        else:
            outputs = {"UPDATE": {"success": False,
                                  "message": "cannot find the name and old public key"}}

        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)
        tx = Transaction(
            transaction_type='standard', inputs=inputs, outputs=outputs)
        return tx

    def pki_revoke(self, generator_public_key, public_key):
        '''
            Revoke a public key
        '''
        # input verification
        gen = self.verify_public_key(generator_public_key)
        if not gen:
            print("The generator public key is incorrectly formatted. Please try again.")
            return -1

        pub = self.verify_public_key(public_key)
        if not pub:
            print("The entered public key is incorrectly formatted. Please try again.")
            return -1

        inputs = {"REVOKE": {"public_key": pub}}

        # Query blockchain, break if we find our public key
        flag = False
        for block in reversed(self.blockchain.chain):
            for tx in block.transactions:
                inputs = json.loads(tx.inputs)
                for key in inputs.keys():  # should only be 1 top level key - still O(1)
                    try:
                        if public_key == inputs[key]["public_key"]:
                            flag = True
                            break
                    except:
                        continue
                if flag == True:
                    break
            if flag == True:
                break

        outputs = dict()
        if flag == True:
            outputs = {"REVOKE": {"success": True}}
        else:
            outputs = {"REVOKE": {"success": False,
                                  "message": "Public key not found."}}

        inputs = json.dumps(inputs)
        outputs = json.dumps(outputs)
        tx = Transaction(transaction_type="Standard", tx_generator_address=gen,
                                     inputs=inputs, outputs=outputs)
        return tx

    def command_loop(self):
        # Ensure that the auxillary data folder is set up
        home_path = expanduser("~")
        home_path = os.path.join(home_path, ".BlockchainPKI/")
        if not os.path.exists(home_path):
            os.mkdir(home_path)

        # Finished set up, enter command loop
        print("PKChain Client successfully set up. Type 'help' for a list of commands")
        while True:
            command = input(">>> ").split(" ")
            if command[0] == 'help':
                print("Transactional Functions:\n\n ")
                print(
                    "register                         -Register a name and public key on the blockchain.")
                print(
                    "query                            -Query for a public key given a name.\n\n")
                print(
                    "validate                         -verifies whether a pair of (name, public key) is valid or not")
                print("update                           -Update a user's public key")
                print("Local Functions:\n\n")
                print(
                    "generate                         -Generate a public and private key pair.")
                print(
                    "encrypt <public_key> <message>   -Encrypt a message with a public key.")
                print(
                    "decrypt <private_key> <message>  -Decrypt a message with a private key.\n\n")
            elif command[0] == 'exit':
                self.close()
                break
            elif command[0] == 'register':
                client_pub_key_path = input(
                    "Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                name = input(
                    "Enter the name you would like to register to a public key: ")
                reg_pub_key_path = input(
                    "Enter the path of the public key you would like to register: ")
                reg_pub_key = open(reg_pub_key_path, 'r')
                tx = self.pki_register(client_pub_key, name, reg_pub_key)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'query':
                client_pub_key_path = input(
                    "Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                name = input("Enter the name you would like to query for: ")
                tx = self.pki_query(client_pub_key, name)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'validate':
                client_pub_key_path = input(
                    "Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                name = input("Enter the name you would like to validate: ")
                val_pub_key_path = input(
                    "Enter the path of the public key you would like to validate: ")
                val_pub_key = open(val_pub_key_path, 'r')
                tx = self.pki_validate(client_pub_key, name, val_pub_key)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
            elif command[0] == 'update':
                client_pub_key_path = input(
                    "Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                name = input(
                    "Enter the name you would like to associate with your updated key: ")
                old_pub_key_path = input(
                    "Enter the path of your old public key: ")
                old_pub_key = open(old_pub_key_path, 'r')
                new_pub_key_path = input(
                    "Enter the path of your new public key: ")
                new_pub_key = open(new_pub_key_path, 'r')
                tx = self.pki_update(client_pub_key, name,
                                     old_pub_key, new_pub_key)
                tx_2 = self.pki_revoke(client_pub_key, old_pub_key)
                print("Generated two transactions: ")
                print("\nUPDATE:")
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx_2.outputs))
                print("\nREVOKE:")
                print("\nInputs: ", json.loads(tx_2.inputs))
                print("\nOutputs: ", json.loads(tx_2.outputs))
            elif command[0] == 'revoke':
                client_pub_key_path = input(
                    "Enter the path of your public key (generator address): ")
                client_pub_key = open(client_pub_key_path, 'r')
                old_pub_key_path = input(
                    "Enter the path of the public key you would like to revoke: ")
                old_pub_key = open(old_pub_key_path, 'r')
                tx = self.pki_revoke(client_pub_key, old_pub_key)
                print("\nInputs: ", json.loads(tx.inputs))
                print("\nOutputs: ", json.loads(tx.outputs))
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

    @staticmethod
    def generate_keys():
        '''
            Generate public and private keys using RSA key generation
        '''
        # Specify the IP size of the key modulus
        modulus_length = 256 * 8
        # Using a Random Number Generator and the modulus length as parameters
        # For the RSA key generation, create your private key
        private_key = RSA.generate(modulus_length, Random.new().read)

        # create the key dir if not created
        home_path = expanduser("~")
        key_path = os.path.join(home_path, ".BlockchainPKI", "keys")
        if not os.path.exists(key_path):
            print("Directory %s does not exist" % key_path)
            cont = input("Would you like to create %s? (y/n): " % key_path)
            if cont.strip() == 'y':
                os.mkdir(key_path)
                print("Created %s" % key_path)

        # write out the private key
        file_out = open(os.path.join(key_path, "private.pem"), 'wb')
        file_out.write(private_key.export_key())
        print(
            "Sucessfully wrote out new private RSA key to ~/.BlockchainPKI/keys/private.pem")

        # write out the public key
        file_out = open(os.path.join(key_path, "public.pem"), 'wb')
        file_out.write(private_key.publickey().export_key())
        print(
            "Successfully wrote out new public RSA key to ~/.BlockchainPKI/keys/public.pem")

        # Generate a public key from the private key we just created
        public_key = private_key.publickey()
        return private_key, public_key

    @staticmethod
    def verify_public_key(public_key):
        '''
            Verify a public key is correctly formatted by making an RSA key object
            :params: public_key - a file object of the public key to be verified
                    passphrase - if the key requires a passphrase use it, otherwise passphrase should be None
        '''
        try:
            key = RSA.import_key(public_key.read())
            key = key.publickey().export_key()
            return key.decode()
        except ValueError:
            return None

    def receive(self):
        '''
            Receive incoming connections
        '''
        pass
