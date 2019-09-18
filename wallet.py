import nacl
import nacl.encoding
import nacl.exceptions
import nacl.signing
import secrets


def raw_sign(signing_key: bytes, message: bytes):
    sk = nacl.signing.SigningKey(seed=signing_key)
    sig = sk.sign(message)
    return sig.signature


def raw_verify(verifying_key: bytes, message: bytes, signature: bytes):
    vk = nacl.signing.VerifyKey(key=verifying_key)
    try:
        vk.verify(message, signature)
    except nacl.exceptions.BadSignatureError:
        return False
    return True


class Wallet:
    def __init__(self, seed=None):
        if seed is None:
            seed = secrets.token_bytes(32)

        self.sk = nacl.signing.SigningKey(seed=seed)
        self.vk = self.sk.verify_key

    def sign(self, msg: bytes):
        sig = self.sk.sign(msg)
        return sig.signature

    def verify(self, msg: bytes, signature: bytes):
        try:
            self.vk.verify(msg, signature)
        except nacl.exceptions.BadSignatureError:
            return False
        return True

