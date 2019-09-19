# Lampy - A Lamden Python Client

This library lets you easily interact with the Lamden blockchain. Here is how:

### Creating Wallets
Wallets are simple wrappers of [libsodium](https://github.com/jedisct1/libsodium) keypairs. The Lamden protocol uses [ED25519](https://ed25519.cr.yp.to/) for cryptographic keys and the [PyNaCl](https://pynacl.readthedocs.io/en/stable/) library for the specific Python bindings of the original C code.

#### A brand new wallet
```python
from lampy.wallet import Wallet
wallet = Wallet()

>>> wallet.vk
<nacl.signing.VerifyKey at 0x10a7e82b0>

>>> wallet.vk.encode()
b'\x1d#\xc4\xc1W\x1a\xe3\xa5I\xb7\x14\xc0\x90\x80X\xce\xb9\xc3\xa2r\x80\x8e\xc7\x8f\x97\xa2\x93\x12\n\x17\x07='

>>> wallet.sk
<nacl.signing.SigningKey at 0x10a7e8518>

>>> wallet.sk.encode()
b'D\x12\x87\x83\xcfN\xa0"\x06Dn\x9d\xb0F\x13\xa3\xb3\xdb\x8f\xb8\x8c\xfa>\x03\xbb\x07OR\x7f\x18`\xce'
```
***
#### A wallet from a previous signing key
```python
from lampy.wallet import Wallet
sk = b'D\x12\x87\x83\xcfN\xa0"\x06Dn\x9d\xb0F\x13\xa3\xb3\xdb\x8f\xb8\x8c\xfa>\x03\xbb\x07OR\x7f\x18`\xce'
wallet = Wallet(seed=sk)

>>> wallet.vk.encode()
b'\x1d#\xc4\xc1W\x1a\xe3\xa5I\xb7\x14\xc0\x90\x80X\xce\xb9\xc3\xa2r\x80\x8e\xc7\x8f\x97\xa2\x93\x12\n\x17\x07='
```
***
#### I want a pretty wallet!
```python
from lampy.wallet import Wallet
sk = b'D\x12\x87\x83\xcfN\xa0"\x06Dn\x9d\xb0F\x13\xa3\xb3\xdb\x8f\xb8\x8c\xfa>\x03\xbb\x07OR\x7f\x18`\xce'
wallet = Wallet(seed=sk)

>>> wallet.vk.encode().hex()
'1d23c4c1571ae3a549b714c0908058ceb9c3a272808ec78f97a293120a17073d'
```
***
#### Signing things
You can sign transactions, which is primarily what you use wallet keypairs for, or arbitrary data to prove you are the owner of a wallet.
```python
from lampy.wallet import Wallet
sk = b'D\x12\x87\x83\xcfN\xa0"\x06Dn\x9d\xb0F\x13\xa3\xb3\xdb\x8f\xb8\x8c\xfa>\x03\xbb\x07OR\x7f\x18`\xce'
wallet = Wallet(seed=sk)

msg = b'hello there'
>>> wallet.sign(msg)
b"\x9f0e\rX\xf7\xb4\x04F\xb5\xc5\xd7\xec\xd3\xf8\xd1\x89\x82J\xe0\x1b\x8a\x01*\x8c'Qe\\0?(\x86J>\xee\x93<\x92\x0f\x06\xd4y9\xf0\x0b\xad\x7f0_\xd6\xa3Nb>j\x97%N\xe5\xeb\xb8]\x0f"
```
***

#### Verifying things
If you have a signed message, the original message, and the verifying key of the signer, you can verify if the owner of the keypair did in fact sign the message. This is used to verify transactions have been signed by a wallet's owner.
```python
from lampy.wallet import Wallet, raw_verify
sk = b'D\x12\x87\x83\xcfN\xa0"\x06Dn\x9d\xb0F\x13\xa3\xb3\xdb\x8f\xb8\x8c\xfa>\x03\xbb\x07OR\x7f\x18`\xce'
wallet = Wallet(seed=sk)

public_key = wallet.vk.encode()
signature = wallet.sign(b'hello there')

# Assume data transmission across a network of (public_key, signature, message)

>>> raw_verify(verifying_key=public_key, message=b'hello there', signature=signature)
True

>>> raw_verify(verifying_key=public_key, message=b'hello there', signature=b'bad signature')
False
```
### Sending Transactions
For sending transactions, you need the IP address of a masternode so that Lampy knows where to send the raw transaction. Connections to masternodes are maintained in a class.
```python
# Create a new wallet
wallet = Wallet()

client = LamdenClient(ip='127.0.0.1:8000', wallet=wallet)
client.submit_transaction(contract='currency',
                          function='transfer',
                          kwargs={'to': 'jeff', 'from': 'stu'},
                          stamps=10000)

```
### Querying the Blockchain
If you don't know what you want to do, you can browse the blockchain and the states of smart contracts to investigate how the system works. If you don't want to submit transactions, you can use a `Connection` object instead of a `LamdenClient`. However, a `LamdenClient` has all of the same methods as the `Connection`.
```python
wallet = Wallet()
client_1 = LamdenClient(ip='127.0.0.1:8000', wallet=wallet)
client_2 = Connection(ip='127.0.0.1:8000')

>>> client_1.get_latest_block_hash() == client_2.get_latest_block_hash()
True
```
***
#### Ping
```python
client = Connection(ip='127.0.0.1:8000')

>>> client.ping()
{'status': 'online'}
```
***
#### Get Contracts
```python
>>> client.get_contracts()
['currency', 'election_house', 'swaps']
```
***
#### Get Contract Code
```python
>>> client.get_contract_code('currency')

supply = Variable()
balances = Hash(default_value=0)

@construct
def seed():
    seed_amount = 1_000_000_000
    supply.set(seed_amount)
    balances[ctx.caller] = seed_amount

@export
def transfer(amount, to):
    sender = ctx.caller
    balance = balances[sender]

    assert balance >= amount

    balances[sender] -= amount
    balances[to] += amount

@export
def balance_of(account):
    return balances[account]

@export
def total_supply():
    return supply.get()

@export
def allowance(owner, spender):
    return balances[owner, spender]

@export
def approve(amount, to):
    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]

@export
def transfer_from(amount, to, main_account):
    sender = ctx.caller

    assert balances[main_account, sender] >= amount
    assert balances[main_account] >= amount

    balances[main_account, sender] -= amount
    balances[main_account] -= amount

    balances[to] += amount
```
***
#### Get Variable
```python
>>> client.get_variable(contract='currency', variable='balances', key='stu')
{'value': 1_000_000}

# If I want to get the allowance, which uses a multihash, I need to supply a list of keys.
# balances['stu', 'jeff'] => ['stu', 'jeff']

>>> client.get_variable(contract='currency', variable='balances', key=['stu', 'jeff'])
{'value': 100}
```
***
#### Get Methods
```python
>>> client.get_methods('currency')
[{'name': 'transfer', 'arguments': ['amount', 'to']}
 {'name': 'balance_of', 'arguments': ['account']},
 {'name': 'total_supply', 'arguments': []},
 {'name': 'allowance', 'arguments': ['owner', 'spender']},
 {'name': 'approve', 'arguments': ['amount', 'to']},
 {'name': 'transfer_from', 'arguments': ['amount', 'to', 'main_account']}]
```
***
#### Get Latest Block Hash
```python
>>> client.get_latest_block_hash()
'3bf746ee27fc9154b0792182d55d1ff33a6a52092b8608fb53ae1d6c2fc21166'
```

That's about it! Example project soon.