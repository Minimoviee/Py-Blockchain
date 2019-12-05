import requests
from flask import jsonify
import json
from flask import request

class UI(object):
    def __init__(self):
        """
        initialize the user interface to allow for the user to easily
        interact with the blockchain
        \tparam NONE
        """
        self.address = str(0)

    def register(self):
        """
        User option to register themselves as a new node
        """
        reg_command = f'http://{self.address}/nodes/register'
        address_with_schema = f'http://{self.address}'
        info = {
            "nodes" : [address_with_schema]
        }

        print(info['nodes'])
        #response = requests.get(reg_command)
        reponse = requests.post(reg_command, data = info)
        print(response)

    def opt1_mine_block(self):
        """
        Option to mine the new block
        param : NONE
        return : NONE
        """
        comm = f'http://{self.address}/mine'
        response = requests.get(comm)
        new_block = response.json()
        print("New Block was mined!")
        print(new_block)

    def opt3_full_chain(self):
        comm = f'http://{self.address}/chain'
        response = requests.get(comm)
        chain = response.json()
        print(chain)

    def menu(self):
        """
        menu options for the user to choose the next action
        \tparam NONE
        \treturn <int> Option number

        """
        print("Welcome to LitCoin - the blockchain for EE460 - Computer Communication Systems")
        print("Created by: Younghwa Min, Jaskaran Singh, Christian Huacon, Matteo Rama and Kelvin Ma")
        print("Please run the blockchain by typing: 'python EE460_blockchain.py -p [desired port number]' before continuing")
        host = str(input("Address: "))
        port = int(input("Port number: "))
        print("Running on ", host+":"+str(port))
        self.address = host+":"+str(port)
        print("Registering ... ")
        self.register()
        print("Successfully registered!")
        print("\nOptions:")
        print("1 - Mine a new block")
        print("2 - Add a new transaction")
        print("3 - Request the full blockchain")
        print("4 - Verify blockchain (Consensus)")
        print("5 - Continuous mining mode")
        while(True):
            choice = int(input("please enter choice:"))
            if choice == 1:
                self.opt1_mine_block()
            elif choice == 3:
                self.opt3_full_chain()
            if (choice == 5):
                while(True):
                    self.opt1_mine_block()
        #print(test)

test = UI()
test.menu()
