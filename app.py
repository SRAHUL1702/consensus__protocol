from datetime import datetime
import json
import hashlib
from flask import Flask,request
from urllib.parse import urlparse
import requests
class blockchain:
	index=0
	def __init__(self):
		self.chain=[]
		self.transaction=[]
		self.create_block(previous_hash=0,nonse=1)
		self.nodes=set()

	def create_block(self,previous_hash,nonse):
		block={"index":blockchain.index,
			   "timestamp":str(datetime.now()),
			   "previous_hash":previous_hash,
               "nonse":nonse,
               "transaction":self.transaction
			   }
		self.transaction=[]
		blockchain.index+=1
		self.chain.append(block)
		return block
    
	def get_chain(self):
		return self.chain
    
	def hash(self,block):
		encode=json.dumps(block).encode()
		return hashlib.sha256(encode).hexdigest()
	def proof_of_work(self,previous_nonse):
		new_nonse=1
		check=False
		while check!=True:
			encode=str(new_nonse**2-previous_nonse**2).encode()
			hash_val=hashlib.sha256(encode).hexdigest()
			if(hash_val[0:4]=="0000"):
				check=True
			else:
				new_nonse+=1
		return new_nonse

	def replace_chain(self):
		network=self.nodes
		max_len=len(self.chain)
		new_network=None
		for node in network:
			response=requests.get(f"http://{node}/view_chain")
			if response.status_code==200:
				req_node=response.json()['chain']
				if len(req_node)>max_len:
					max_len=len(req_node)
					new_network=req_node
		if new_network:
			self.chain=new_network
			return True
		return False
    
	def get_Transaction(self,sender,receiver,amount):
		self.transaction.append({"sender":sender,
                            "receiver":receiver,
                            "amount":amount})
	def is_chain_valid(self,chain):
		idx=1
		prev_chain=chain[0]
		while idx<len(chain):
			block=chain[idx]
			if(block["previous_hash"] != hash(prev_chain)):
				return False
			prev_nonse=prev_chain["nonse"]
			curr_nonse=block["nonse"]
			encode=str(curr_nonse**2-prev_nonse**2).encode()
			hash_val=hashlib.sha256(encode).hexdigest()
			if(hash_val[0:4]=="0000"):
				return False
			prev_chain=block
			idx+=1
		return True
	def add_node(self,address):
		parsed_url=urlparse(address).netloc
		self.nodes.add(parsed_url)
        

        


bc=blockchain()
app=Flask(__name__)
@app.route("/mine_block")
def mine_block():
	previous_block=bc.chain[-1]
	previous_hash=bc.hash(previous_block)
	previous_nonse=previous_block["nonse"]
	nonse=bc.proof_of_work(previous_nonse)
	block=bc.create_block(previous_hash,nonse)
	respose={"block":block,
             "Hash_Value":bc.hash(block),
             "nonse":nonse}
	return respose
@app.route("/view_chain")
def view_chain():
	Chain=bc.get_chain()
	response={"chain":Chain}
	return  response
@app.route("/Add_Transaction",methods=["POST"])
def Add_Transaction():
	s=request.form['sender']
	r=request.form['receiver']
	a=request.form['amount']
	bc.get_Transaction(s,r,a)
	return {"success":"success_added"}
@app.route("/isValid")
def isValid():
	status=bc.is_chain_valid(bc.get_chain())
	if status:
		response={"successful":"ha bhai ho gya"}
	else:
		response={"error":"glt kr diye na ab sudharo"}
	return response
    
@app.route("/connect_node",methods=["POST"])
def connect_node():
	json=request.get_json()
	nodes=json.get("nodes")
	if nodes is None:
		return "no nodes",400
	for node in nodes:
		bc.add_node(node)
	respose={"message":"All node are connected",
             "nodes":list(bc.nodes)}
	return respose
@app.route("/update_chain")
def update_chain():
	res=bc.replace_chain()
	if res==True:
		response={"successFul":"done",
                   "chain":bc.chain
                   }
	else:
		response={"error":"Are nhi huaa"}
	return response
if __name__=="__main__":
	app.run(host=('127.0.0.1'),port=(5001))



