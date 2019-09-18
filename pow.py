import hashlib
import secrets


class SHA3POWBytes:
    @staticmethod
    def find(o: bytes):
        while True:
            h = hashlib.sha3_256()
            s = secrets.token_bytes(16)
            h.update(o + s)
            if int(h.digest().hex(), 16) < POW_BYTES_DIFFICULTY:
                return s

    @staticmethod
    def check(o: bytes, proof: bytes):
        if not len(proof) == 16:
            return False
        h = hashlib.sha3_256()
        h.update(o + proof)
        return int(h.digest().hex(), 16) < POW_BYTES_DIFFICULTY
