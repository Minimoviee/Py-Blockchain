from Blockchain import Blockchain
from uuid import uuid4
from textwrap import dedent
from flask import Flask, jsonify, request
from argparse import ArgumentParser

# instantiate the node
app = Flask(__name__)

# generate the uuid (universally unique identifier) for the node
node_identifier = str(uuid4())
node_identifier = node_identifier.replace('-','')
print(node_identifier)
# Blockchain object
blockchain = Blockchain()

# method to register a new node
@app.route('/nodes/register', methods = ['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods = ['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message' : 'Our chain was replaced.',
            'New chain' : blockchain.chain
        }
    else:
        reponse = {
            'message' : 'Our chain was authoritative. Nothing was replaced.',
            'chain' : blockchain.chain
        }

    return jsonify(response), 200

# method to mine
@app.route('/mine', methods = ['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #rewrad for successfully mining a block
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message' : "New block was mined.",
        'index' : block['index'],
        'transactions' : block['transactions'],
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash']
    }
    # return ok status (http 200)
    return jsonify(response), 200


@app.route('/transactions/new', methods = ['POST'])
def new_transaction():
    received_transaction = request.get_json()

    required = ['sender', 'recipient', 'amount']
    # 400 is the http status for Bad Request
    if (not all(k in received_transaction for k in required)):
        return 'transactions must contain a sender, recipient and amount', 400

    # at this point, our transction is valid and we can add it to the blockchain
    sender = received_transaction['sender']
    recipient = received_transaction['recipient']
    amount = received_transaction['amount']
    block_index = blockchain.new_transaction(sender, recipient, amount)

    response = {
        'message' : f'The transaction successfully added. Block index #{block_index}'
    }
    # 201 is the http status for Successful Creation
    return jsonify(response), 201

@app.route('/chain', methods = ['GET'])
def get_full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    # 200 is the http status for OK
    return jsonify(response), 200


    #app.run(host = '0.0.0.0', port = 5000)
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='192.168.56.1', port=port)
