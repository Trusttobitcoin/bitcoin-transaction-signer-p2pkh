# File: signandtransfer.py

import hashlib
import ecdsa
import requests
import struct
import base58

def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def to_satoshis(btc):
    return int(btc * 100000000)

def base58_decode(address):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    base58_val = 0
    for char in address:
        base58_val = base58_val * 58 + alphabet.index(char)
    hex_string = f'{base58_val:x}'.zfill(50)
    return bytes.fromhex(hex_string)

class PrivateKey:
    def __init__(self, secret):
        self.secret = secret
        self.public_key = self.get_public_key()

    def get_public_key(self):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.secret), curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        return b'\x02' + vk.to_string()[:32] if vk.pubkey.point.y() % 2 == 0 else b'\x03' + vk.to_string()[:32]

    def sign(self, message):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.secret), curve=ecdsa.SECP256k1)
        return sk.sign_digest(message, sigencode=ecdsa.util.sigencode_der_canonize)

def create_p2pkh_script(address):
    decoded = base58_decode(address)
    pubkey_hash = decoded[1:-4]
    return b'\x76\xa9\x14' + pubkey_hash + b'\x88\xac'

class Transaction:
    def __init__(self, inputs, outputs, from_address):
        self.version = struct.pack('<L', 2)  # Version 2
        self.inputs = inputs
        self.outputs = outputs
        self.locktime = struct.pack('<L', 0)
        self.from_address = from_address

    def serialize(self, for_signature=False, input_index=None):
        serialized = self.version
        serialized += struct.pack('<B', len(self.inputs))
        
        for i, tx_in in enumerate(self.inputs):
            if for_signature and i == input_index:
                serialized += tx_in.serialize(script_override=create_p2pkh_script(self.from_address))
            elif for_signature:
                serialized += tx_in.serialize(script_override=b'')
            else:
                serialized += tx_in.serialize()
        
        serialized += struct.pack('<B', len(self.outputs))
        for tx_out in self.outputs:
            serialized += tx_out.serialize()
        
        serialized += self.locktime
        
        if for_signature:
            serialized += struct.pack('<L', 1)  # SIGHASH_ALL
        
        return serialized

    def get_transaction_digest(self, input_index, script_pubkey):
        return double_sha256(self.serialize(for_signature=True, input_index=input_index))

class TxInput:
    def __init__(self, txid, vout, script_sig=b'', sequence=0xffffffff):
        self.txid = txid
        self.vout = vout
        self.script_sig = script_sig
        self.sequence = sequence

    def serialize(self, script_override=None):
        return (
            bytes.fromhex(self.txid)[::-1] +
            struct.pack('<L', self.vout) +
            struct.pack('<B', len(script_override if script_override is not None else self.script_sig)) +
            (script_override if script_override is not None else self.script_sig) +
            struct.pack('<L', self.sequence)
        )

class TxOutput:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def serialize(self):
        return struct.pack('<Q', self.amount) + struct.pack('<B', len(self.script_pubkey)) + self.script_pubkey

def get_utxos_from_blockcypher(address):
    url = f"https://api.blockcypher.com/v1/btc/test3/addrs/{address}?unspentOnly=true"
    response = requests.get(url)
    data = response.json()
    return data.get('txrefs', [])

def broadcast_transaction(tx_hex):
    url = "https://api.blockcypher.com/v1/btc/test3/txs/push"
    payload = {"tx": tx_hex}
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        tx_data = response.json()
        return tx_data.get('tx', {}).get('hash')
    else:
        error_message = response.json().get('error', 'Unknown error')
        raise Exception(f"Failed to broadcast transaction: {error_message}")

def sign_and_transfer(private_key_hex, from_address, to_address, amount_to_send, fee):
    # Create a private key object
    private_key = PrivateKey(private_key_hex)

    # Get UTXOs from BlockCypher
    utxos = get_utxos_from_blockcypher(from_address)

    if not utxos:
        raise Exception("No UTXOs found for the address.")

    # Select a UTXO to spend (for simplicity, we'll use the first one)
    utxo = utxos[0]
    utxo_txid = utxo['tx_hash']
    utxo_vout = utxo['tx_output_n']
    utxo_amount = utxo['value']

    # Create a transaction input
    tx_in = TxInput(utxo_txid, utxo_vout)

    # Calculate change
    change_amount = utxo_amount - amount_to_send - fee

    if change_amount < 0:
        raise Exception("Insufficient funds for this transaction.")

    # Create transaction outputs
    tx_out1 = TxOutput(amount_to_send, create_p2pkh_script(to_address))
    tx_out2 = TxOutput(change_amount, create_p2pkh_script(from_address))

    # Create the transaction
    tx = Transaction([tx_in], [tx_out1, tx_out2], from_address)

    # Sign the input
    script_pubkey = create_p2pkh_script(from_address)
    tx_digest = tx.get_transaction_digest(0, script_pubkey)
    signature = private_key.sign(tx_digest)

    # Construct the scriptSig
    script_sig = (
        struct.pack('<B', len(signature) + 1) +
        signature +
        b'\x01' +  # SIGHASH_ALL
        struct.pack('<B', len(private_key.public_key)) +
        private_key.public_key
    )

    tx.inputs[0].script_sig = script_sig

    # Serialize the transaction
    signed_tx = tx.serialize()
    signed_tx_hex = signed_tx.hex()

    # Broadcast the transaction
    tx_hash = broadcast_transaction(signed_tx_hex)

    return tx_hash

# Example usage (commented out)
# if __name__ == "__main__":
#     private_key_hex = "YourPrivateKey"
#     from_address = "Youraddress"
#     to_address = "p2pkhaddress"
#     amount_to_send = to_satoshis(0.000001)  # 0.000001 BTC in satoshis
#     fee = to_satoshis(0.000001)  # 0.000001 BTC in satoshis
#
#     try:
#         tx_hash = sign_and_transfer(private_key_hex, from_address, to_address, amount_to_send, fee)
#         print(f"Transaction successfully broadcast! Transaction hash: {tx_hash}")
#         print(f"You can view the transaction at: https://live.blockcypher.com/btc-testnet/tx/{tx_hash}/")
#     except Exception as e:
#         print(f"Error: {str(e)}")
