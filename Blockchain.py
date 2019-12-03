import hashlib
import json
import datetime
from urllib.parse import urlparse
import requests


class Blockchain(object):
    def __init__(self):
        """
        Initializes the blockchain. Creates the genesis block.
        params : none

        --- Contents of a block ---
        \tblock <dict> {
        \t    index : -- index of block
        \t    timestamp :  -- time of last block creation (GMT time zone)
        \t    transactions : -- list of transactions (sender, recipient, amount)
        \t    proof : -- proof of work and validity
        \t    previous_hash : -- hash of previous block
        \t}
        """
        self.chain = []
        self.current_transactions = [] # list of transactions
        self.nodes = set() # empty set of nodes

        self.difficulty = 5

        self.new_block(proof = 100, previous_hash = 1)

    def register_node(self, address):
        """
        This adds a new node (miner or transactor) to thd blockchain

        \t:param address <str> : address of the node (http://IP:PORT)
        \t:return: None
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
        print("Added address: ", parsed_url, " - Corresponding to: ", address)

    def new_block(self, proof, previous_hash = None):
        """
        The new_block method creates a new block and adds it to the end
        of the current chain.

        \tparam proof <int> : Proof from PoW (Proof of Work) algorithm
        \tparam previous_hash (optional) <str> : Hash or previous block

        \treturn <dict> : the newly generated block
        """

        # the new block to be generated
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : str(datetime.datetime.now()),
            'transactions' : self.current_transactions,
            'proof': proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        The new_transaction method creates a new transactions and adds it
        to the end of the list of current transactions

        \tparam sender <str> : Address of the transaction sender
        \tparam recipient <str> : Address of transaction recipient
        \tparam amount <double or int> : transaction amount - default = 0

        \treturn <int> : index of the block containing this transaction
        """
        transaction = {
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount,
        }
        self.current_transactions.append(transaction)

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        Modeled after bitcoin's "hashcash" proof of work algorithm
        Goal: Find a number, proof, such that the hash of last_proof + proof
        \t is leader by 'self.difficulty' number of zeros
        \t self.difficulty is 3 by default.

        \tparam last_proof <int> : previous proof
        \treturn proof <int> : correct proof
        """

        # TODO: Add furthur methods to proof of work
        # currently, only linear brute force is supported
        proof = 0
        while (self.validate_proof(last_proof, proof, self.difficulty) is False):
            proof += 1

        return proof

    def valid_chain(self, chain):
        """
        This method is to check if the chain is valid.
        For a chain to be valid, the current block has to point at the previous
        block via it's hash. Another criteria is that the proof contained in the
        block MUST be valid.

        \tparam chain <list> : A Blockchain
        \tReturn <bool> : True if chain is valid, False if it is not
        """
        prev_block = chain[0]
        for index in range(1,len(chain)):
            block = chain[index]
            print(f'{prev_block}')
            print(f'{block}')
            print("\n---------------------\n")
            if block['previous_hash'] != self.hash(prev_block):
                return False

            if not self.valid_proof(prev_block['proof'], block['proof']):
                return False

            prev_block = block

        return True

    def resolve_conflicts(self):
        """
        The consensus algorithm - resolves any conflifts by simply replacing the
        blockchain with the longest blockchain within the network.

        \tReturn <bool> : True if the blockchain was resolved, False if not
        """
        neighbors = self.nodes
        new_chain = None

        max_length_chain = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            if (response.status_code == 200):
                length = response.json()['length']
                chain = ressponse.json()['chain']

                if (length > max_length_chain and self.valid_chain(chain)):
                    max_length_chain = length
                    new_chain = chain

        if new_chain != None :
            self.chain = new_chain
            return True
        return False

    @staticmethod
    def hash(block, hash_algorithm = 'SHA-256'):
        """
        hashes the contents of the block

        \tparam block <dict> : block to be hashed
        \tparam hash_algorithm (optional) <str> : Algorithm to be used
        \t\tSupported algorithms: SHA-256 (default), SHA-512, SHA-1, MD5
        \treturn <str> : hash of the block
        """

        # convert the block into string, and make sure the dictionary is ordered
        block_as_string = json.dumps(block, sort_keys = True).encode()

        # hash the block
        if (hash_algorithm == 'SHA-256'):
            hash = hashlib.sha256(block_as_string).hexdigest()
        elif(hash_algorithm == 'SHA-512'):
            hash = hashlib.sha512(block_as_string).hexdigest()
        elif(hash_algorithm == 'SHA-1'):
            hash = hashlib.sha512(block_as_string).hexdigest()
        elif(hash_algorithm == 'MD5'):
            hash = hashlib.md5(block_as_string).hexdigest()
        else:
            print('Unsupported hashing algorithm')
            hash = 'Unsupported algorithm'
        return hash

    @staticmethod
    def validate_proof(last_proof, proof, difficulty, hash_algorithm = 'SHA-256'):
        """
        Validates the proof - checks that the hash of last_proof + proof has
        'difficulty' number of zeros.

        \tparam last_proof <int> : previous proof (fixed number)
        \tparam proof <int> : proof (the current guess)
        \tparam difficulty <int> : level of difficulty
        \tparam hash_algorithm (optional) <str> : Algorithm to be used
        \t\tSupported algorithms: SHA-256 (default), SHA-512, SHA-1, MD5

        \treturn <bool> : True if correct, false if incorrect
        """
        guess = f'{last_proof}{proof}'.encode()
        if (hash_algorithm == 'SHA-256'):
            hashed_guess = hashlib.sha256(guess).hexdigest()
        elif(hash_algorithm == 'SHA-512'):
            hashed_guess = hashlib.sha512(guess).hexdigest()
        elif(hash_algorithm == 'SHA-1'):
            hashed_guess = hashlib.sha512(guess).hexdigest()
        elif(hash_algorithm == 'MD5'):
            hashed_guess = hashlib.md5(guess).hexdigest()
        else:
            print('Unsupported hashing algorithm')
            hash = 'Unsupported algorithm'
            return False

        correct_hash = '0' * difficulty
        if (hashed_guess[:difficulty] == correct_hash):
            return True
        else:
            return False

    @property
    def last_block(self):
        """
        @property of blockchain - returns the last block contained in the
        blockchain
        """
        return self.chain[-1]
