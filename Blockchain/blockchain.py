from flask import Flask, request, jsonify,render_template
from time import time
from flask_cors import CORS
from collections import OrderedDict
import binascii
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA
from uuid import uuid4
#import json
import hashlib
import requests
from urllib.parse import urlparse
from clear_all import *

MINING_SENDER = "The Blockchain"
MINING_REWARD = 1
MINING_DIFFICULTY = 2

global ruta
ruta=""
temperatura=0
humedad=0
diccionario={}
archivo="config.txt"

def config(diccionario_string,archivo="config.txt"):
    f=open(archivo,"+w")
    f.write(diccionario_string)
    f.close()

def leer_dic(archivo="config.txt"):
    f = open(archivo, "r")
    dic=f.read()
    f.close()
    dic=json.loads(dic)
    return dic

class Blockchain:

    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-', '')
        # Create the genesis block
        self.create_block(0, '00')

    def register_node(self, node_url):
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
    def create_block(self, nonce, previous_hash):
        """
        Add a block of transactions to the blockchain
        """
        block = {'block_number': len(self.chain) + 1,
                 'timestamp': time(),
                 'transactions': self.transactions,
                 'nonce': nonce,
                 'previous_hash': previous_hash}

        # Reset the current list of transactions
        self.transactions = []
        self.chain.append(block)
        return block

    def verify_transaction_signature(self, sender_public_key, signature, transaction):
        public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        try:
            verifier.verify(h, binascii.unhexlify(signature))
            return True
        except ValueError:
            return False

    @staticmethod
    def valid_proof(transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode('utf8')
        h = hashlib.new('sha256')
        h.update(guess)
        guess_hash = h.hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)
        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

    @staticmethod
    def hash(block):
        # We must to ensure that the Dictionary is ordered, otherwise we'll get inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode('utf8')
        h = hashlib.new('sha256')
        h.update(block_string)
        return h.hexdigest()

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get('http://' + node + '/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            transactions = block['transactions'][:-1]
            transaction_elements = ['sender_public_key', 'recipient_public_key', 'amount']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in
                            transactions]

            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False

            last_block = block
            current_index += 1

        return True

    def submit_transaction(self, sender_public_key, recipient_public_key, signature, amount):
        transaction = OrderedDict({
            'sender_public_key': sender_public_key,
            'recipient_public_key': recipient_public_key,
            'amount': amount
        })

        # Reward for mining a block
        if sender_public_key == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            # Transaction from wallet to another wallet
            signature_verification = self.verify_transaction_signature(sender_public_key, signature, transaction)
            if signature_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False


# Instantiate the Blockchain
blockchain = Blockchain()
#blockchain.register_node("http:192.168.100.206:5002")
blockchain.register_node("http:192.168.100.206:5001")
# Instantiate the Node
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/configure')
def configure():
    return render_template('./configure.html')



@app.route('/transactions/get', methods=['GET'])

def get_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    if(len(response["transactions"])!=0):
        diccionario=response['transactions'][0]["amount"]
        #diccionario=json.loads(diccionario)
        config(diccionario)
        #print(diccionario["ruta"])
    return jsonify(response), 200

#[OrderedDict([('sender_public_key', '30819f300d06092a864886f70d010101050003818d00308189028181009cac82fbb96359d1d1e13201495a50ea3218ee116b36f62f0a1c78b5ddc8102341a64d883c908c689608fc0683ec89e2a171809427d3e37629b03bd5c260088374c2a76316be7fd4eb0f496a8c5dcaaae2ba8da59f4106529855428958ed39c87cbb82e937921380b0696a030399a0a9f709f008fa63d6b4dd7e88315546651f0203010001'), ('recipient_public_key', '30819f300d06092a864886f70d010101050003818d0030818902818100abb9ed16d9a8ff8019707c6c3f360497e1742f52779b9febd93ce8c05e0ea12d90cc548fa5a4693c1d731c93663f6ec2cf118f2ce2a2355288c3fef00eb67a1a585ca5843c507f56b07605ef8aa0334e0a1251b1e102ddada2baef32d2934782436e6720a91caf33577b7c824c007dbcd3802108232dcc0c15a130c92a241ae10203010001'), ('amount', '458')])]


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm
    nonce = blockchain.proof_of_work()

    blockchain.submit_transaction(sender_public_key=MINING_SENDER,
                                  recipient_public_key=blockchain.node_id,
                                  signature='',
                                  amount=MINING_REWARD)

    last_block = blockchain.chain[-1]
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': 'New block created',
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    required = ['confirmation_sender_public_key', 'confirmation_recipient_public_key', 'transaction_signature',
                'confirmation_amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction_results = blockchain.submit_transaction(values['confirmation_sender_public_key'],
                                                        values['confirmation_recipient_public_key'],
                                                        values['transaction_signature'],
                                                        values['confirmation_amount'])
    if transaction_results == False:
        response = {'message': 'Invalid transaction/signature'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to the Block ' + str(transaction_results)}
        return jsonify(response), 201


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200

from timeit import default_timer as timer
start_time=timer()
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    f =open('hola.txt','+w')
    hola=timer()-start_time
    print(hola)
    f.write(hola)
    f.close()
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.form
    # 127.0.0.1:5002,127.0.0.1:5003, 127.0.0.1:5004
    nodes = values.get('nodes').replace(' ', '').split(',')

    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Nodes have been added',
        'total_nodes': [node for node in blockchain.nodes]
    }
    return jsonify(response), 200
@app.route('/temperatura')
def index2(chartID='container',chart_type="area",chart_height=500, chart_width=900):
    subtitleText='test'


    dataset=[[date_to_utc(2020,12,1),17],[date_to_utc(2020,12,2),20],[date_to_utc(2020,12,3),23],[date_to_utc(2020,12,4),21],[date_to_utc(2020,12,5),25]]
    pageType='graph'
    chart={'renderTo': chartID,'type':chart_type,'height':chart_height, 'width':chart_width, 'backgroundColor':'rgba(0.1, 0.1, 0.1, 0.1)',
        'borderColor':'#000',
           'borderRadius': 15,
          'borderWidth': 4,
      }
    series=[{'name':'Temperatura del empaque perteneciente al producto #7856','data':dataset,'lineColor':'#008000','color': '#9fff80'}]
    graphtitle={'text':'Temperatura vs Fecha'}
    xAxis={'type':'datetime', 'lineColor':'#000', 'dateTimeLabelFormats':{'month':'%e. %b','year':'%b'}}
    yAxis={'title':{'text':'Temperatura °C'},'labels': {'style':{'color':'#000'}},'gridLineColor':'#000'}
    return render_template('index2.html', chartID=chartID, chart=chart, series=series, title=graphtitle, xAxis=xAxis, yAxis=yAxis,pageType=pageType, subtitleText=subtitleText)


@app.route('/humedad')
def humedad(chartID='container',chart_type="area",chart_height=500, chart_width=900):
    subtitleText='test'


    dataset=[[date_to_utc(2020,12,1),17],[date_to_utc(2020,12,2),20],[date_to_utc(2020,12,3),23],[date_to_utc(2020,12,4),21],[date_to_utc(2020,12,5),25]]
    pageType='graph'
    chart={'renderTo': chartID,'type':chart_type,'height':chart_height, 'width':chart_width, 'backgroundColor':'rgba(0.1, 0.1, 0.1, 0.1)',
        'borderColor':'#000',
           'borderRadius': 15,
          'borderWidth': 4,

      }
    series=[{'name':'Humedad del empaque perteneciente al producto #7856','data':dataset,'lineColor':'#008000','color': '#f5973d'}]
    graphtitle={'text':'Humedad vs Fecha', 'lineColor':'#008000'}
    xAxis={'type':'datetime', 'lineColor':'#000', 'dateTimeLabelFormats':{'month':'%e. %b','year':'%b'}}
    yAxis={'title':{'text':'% Humedad'},'labels': {'style':{'color':'#000'}},'gridLineColor':'#000'}
    return render_template('index2.html', chartID=chartID, chart=chart, series=series, title=graphtitle, xAxis=xAxis, yAxis=yAxis,pageType=pageType, subtitleText=subtitleText)


@app.route('/mapa')
def mapa():
    di={
    "ruta1":"pruebar2.html",
    "ruta2":"pruebar3.html",
    "ruta3":"pruebar4.html",
    "ruta4":"pruebar5.html"}
    diccionario=leer_dic()
    print(diccionario)

    if len(diccionario)!=0:
        #print(diccionario["ruta"])
        ruta=diccionario["ruta"]
        return render_template(di[ruta])
        # return render_template("pruebar2.html")
    else:
        print(diccionario)
        return render_template("pruebar2.html")



@app.route('/inicio')
def inicio():


    return render_template('./templated-phaseshift/inicio.html')

@app.route('/homepage')
def homepage():


    return render_template('./templated-phaseshift/index.html')

@app.route('/productos')
def productos():


    return render_template('./Table_Responsive_v1/Table_Responsive_v1/index.html')

if __name__=='__main__':
    from argparse import ArgumentParser
    parser=ArgumentParser()
    parser.add_argument('-p','--port',default=5001,type=int,help="port to listen to")
    args=parser.parse_args()
    port=args.port
    app.run(host='192.168.100.206',port=port,debug=True)


