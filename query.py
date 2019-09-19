import requests
from wallet import Wallet
import tx as transaction


class Connection:
    def __init__(self, ip: str):
        self.ip = ip
        self._vk = None

        # Attempt to ping the server. Raise an error if it is offline.
        self.ping()

    def ping(self):
        # /ping
        return requests.get('{}/ping'.format(self.ip)).json()

    @property
    def vk(self):
        if self._vk is None:
            r = requests.get('{}/id'.format(self.ip))
            vk = r.json()['verifying_key']
            raw_vk = bytes.fromhex(vk)
            self._vk = raw_vk
        return self._vk

    def get_nonce(self, vk: bytes):
        # Returns just the nonce. The VK is provided into this method,
        # and the processor VK can be accessed via vk property. This is more explicit.
        r = requests.get('{}/nonce/{}'.format(self.ip, vk.hex()))
        nonce = r.json()['nonce']
        return nonce

    def get_contracts(self):
        r = requests.get('{}/contracts'.format(self.ip))
        return r.json()['contracts']

    def get_contract_code(self, contract: str):
        r = requests.get('{}/contracts/{}'.format(self.ip, contract))
        return r.json()['code']

    def get_variable(self):
        pass

    def get_methods(self, contract: str):
        r = requests.get('{}/contracts/{}/methods'.format(self.ip, contract))
        return r.json()['methods']

    def get_latest_block_hash(self):
        r = requests.get('{}/latest_block'.format(self.ip))
        return r.json()['hash']


class LamdenClient(Connection):
    def __init__(self, ip: str, wallet: Wallet):
        super().__init__(ip=ip)
        self.wallet = wallet

    def submit_transaction(self, contract: str, function: str, kwargs: dict, stamps: int):

        processor = self.vk
        nonce = self.get_nonce(self.wallet.vk)

        tx_bytes = transaction.build_transaction(wallet=self.wallet,
                                                 contract=contract,
                                                 function=function,
                                                 kwargs=kwargs,
                                                 stamps=stamps,
                                                 processor=processor,
                                                 nonce=nonce)

        r = requests.post('{}/'.format(self.ip), data=tx_bytes)
        return r.json()
