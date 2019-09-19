# Lampy - A Lamden Python Client

This library lets you easily interact with the Lamden blockchain. Here is how:

#### Creating Wallets
Wallets are simple wrappers of [libsodium](https://github.com/jedisct1/libsodium) keypairs. The Lamden protocol uses [ED25519](https://ed25519.cr.yp.to/) for cryptographic keys and the [PyNaCl](https://pynacl.readthedocs.io/en/stable/) library for the specific Python bindings of the original C code.

##### A brand new wallet
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
##### A wallet from a previous signing key
```python
from lampy.wallet import Wallet
sk = b'D\x12\x87\x83\xcfN\xa0"\x06Dn\x9d\xb0F\x13\xa3\xb3\xdb\x8f\xb8\x8c\xfa>\x03\xbb\x07OR\x7f\x18`\xce'
wallet = Wallet(seed=sk)

>>> wallet.vk.encode()
b'\x1d#\xc4\xc1W\x1a\xe3\xa5I\xb7\x14\xc0\x90\x80X\xce\xb9\xc3\xa2r\x80\x8e\xc7\x8f\x97\xa2\x93\x12\n\x17\x07='
```
***
##### Signing things
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

##### Verifying things
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
#### Sending Transactions

```python
# Create a new wallet
wallet = Wallet()

client = LamdenClient(ip='127.0.0.1:8000', wallet=wallet)

```