import os
import capnp
import capnp_schema
import requests
from decimal import Decimal
import time
from wallet import Wallet
from pow import SHA3POWBytes

transaction_capnp = capnp.load(os.path.dirname(capnp_schema.__file__) + '/transaction.capnp')


NUMERIC_TYPES = {int, Decimal}
VALUE_TYPE_MAP = {
    str: 'text',
    bytes: 'data',
    bool: 'bool'
}


# IP should be http://XXX.XXX.XXX:XXXX format, use regex?
def get_processor_and_nonce_from_masternode(vk: bytes, ip: str):
    nonce_req = requests.get('{}/nonce/{}'.format(ip, vk.hex()))
    processor = bytes.fromhex(nonce_req.json()['processor'])
    nonce = nonce_req.json()['nonce']
    return processor, nonce


def build_transaction(wallet: Wallet, contract: str, function: str, kwargs: dict, stamps: int, processor: bytes, nonce: int):
    struct = transaction_capnp.Transaction.new_message()
    payload = transaction_capnp.TransactionPayload.new_message()

    payload.sender = wallet.vk.encode()
    payload.processor = processor
    payload.stampsSupplied = stamps
    payload.contractName = contract
    payload.functionName = function
    payload.nonce = nonce

    payload.kwargs.init('entries', len(kwargs))

    # Enumerate through the Python dictionary and make sure to type cast when needed for Capnproto
    for i, key in enumerate(kwargs):
        payload.kwargs.entries[i].key = key
        value, t = kwargs[key], type(kwargs[key])

        # Represent numeric types as strings so we do not lose any precision due to floating point
        if t in NUMERIC_TYPES:
            payload.kwargs.entries[i].value.fixedPoint = str(value)

        # This should be streamlined with explicit encodings for different types
        # For example, 32 byte strings -> UInt32
        else:
            assert t is not float, "Float types not allowed in kwargs. Used python's decimal.Decimal class instead"
            assert t in VALUE_TYPE_MAP, "value type {} with value {} not recognized in " \
                                        "types {}".format(t, kwargs[key], list(VALUE_TYPE_MAP.keys()))
            setattr(payload.kwargs.entries[i].value, VALUE_TYPE_MAP[t], value)

    payload_bytes = payload.to_bytes_packed()

    struct.metadata.proof = SHA3POWBytes.find(payload_bytes)
    struct.metadata.signature = wallet.sign(payload_bytes)
    struct.metadata.timestamp = int(time.time())

    struct.payload = payload

    return struct.to_bytes_packed()


def submit_transaction(tx: bytes, ip: str):
    return requests.post(ip, data=tx, verify=False)



