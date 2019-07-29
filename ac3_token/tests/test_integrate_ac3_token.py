import os

from iconsdk.builder.transaction_builder import (
    DeployTransactionBuilder,
    CallTransactionBuilder,
)
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

from iconsdk.wallet.wallet import KeyWallet

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


non_owner_keystore_path = "./keystore_NonOwner"
non_owner_keystore_pw = "keystore_Test2"

class TestAC3Token(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()
        self.icon_service = None
        # if you want to send request to network, uncomment next line
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        self.initial_supply = 550000000
        self.decimals = 18
        params = {
            '_initialSupply': self.initial_supply,
            '_decimals': self.decimals
        }
        self._score_address = self._deploy_score(params=params)['scoreAddress']

        self.non_owner_wallet = KeyWallet.load(non_owner_keystore_path, non_owner_keystore_pw)

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS, params: dict = None) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(self.SCORE_PROJECT)) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)
        
        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(to=self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_call_name(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("name") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        print('Name:', response)
        self.assertEqual("AC3", response)

    def test_call_symbol(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("symbol") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        print('Symbol:', response)
        self.assertEqual("AC3", response)

    def test_call_decimals(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("decimals") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        # print('Decimals in HEX:', response)
        decimals = int(response, 0)
        print('Decimals in DEC:', decimals)
        self.assertEqual(hex(self.decimals), response)

    def test_call_totalSupply(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("totalSupply") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        # print('Total Supply in HEX:', response)
        totalSupply = int(response, 0)
        totalSupply = int(totalSupply / 10 ** self.decimals)
        print('Total Supply in DEC:', totalSupply)
        self.assertEqual(hex(self.initial_supply * 10 ** self.decimals), response)

    def test_call_balanceOf(self):
        # Make params of balanceOf method
        params = {
            # token owner
            '_owner': self._test1.get_address()
        }
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        # print('Balance Of', self._test1.get_address(), 'in HEX:', response)
        balance = int(response, 0)
        balance = int(balance / 10 ** self.decimals)
        print('Balance Of Owner => ', 'Address:', self._test1.get_address(), 'Balance:', balance)

        self.assertEqual(hex(self.initial_supply * 10 ** self.decimals), response)

    def test_token_transfer(self):
        # Make params of transfer method
        to = self._wallet_array[0].get_address()
        value = 100
        params = {
            '_to': to,
            '_value': value,
        }

        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("transfer") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # Sends the transaction to the network
        print('Transfer Transaction', value, 'From:', self._test1.get_address(), 'To:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        # Make params of balanceOf method
        params = {
            '_owner': to
        }
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        # print('Balance Of Receiver:', to, 'in HEX:', response)
        balance = int(response, 0)
        print('Balance Of Receiver=>', 'Address:', to, 'Balance:', balance)

        # check balance of receiver
        self.assertEqual(hex(value), response)

        # Make params of balanceOf method
        params = {
            '_owner': self._test1.get_address()
        }
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        # print('Balance Of Sender:', self._test1.get_address(), 'in HEX:', response)
        balance = int(response, 0)
        print('Balance Of Sender =>', 'Address:', self._test1.get_address(), 'Balance:', balance)

        # check balance of sender
        self.assertEqual(hex(self.initial_supply * 10 ** self.decimals - value), response)

    def test_add_blacklist_by_owner(self):
        # Make params of add_blacklist method
        print('------ Add Blacklist by owner test start-----')
        to = self.non_owner_wallet.get_address()
        value = 100
        params = {
            'addr': to,
        }

        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("add_blacklist") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # Sends the transaction to the network
        print('Add blacklist by owner', 'From:', self._test1.get_address(), 'Address:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        
        to = self._wallet_array[0].get_address()
        value = 100
        params = {
            '_to': to,
            '_value': value,
        }
        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self.non_owner_wallet.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("transfer") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.non_owner_wallet)

        # Sends the transaction to the network
        print('Transfer Transaction', value, 'From:', self.non_owner_wallet.get_address(), 'To:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertEqual(tx_result['status'], 0)
        self.assertFalse(tx_result['failure'] is None)
        print('\t(Transaction Reverted)', tx_result['failure']['message'])

        print('------ Add Blacklist by owner test end -----')
        
    def test_add_blacklist_by_stranger(self):
        # Make params of add_blacklist method
        print('------ Add Blacklist by stranger start -----')
        to = self._wallet_array[2].get_address()
        value = 100
        params = {
            'addr': to,
        }

        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self.non_owner_wallet.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("add_blacklist") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.non_owner_wallet)
        print('Add blacklist by stranger', 'From:', self._test1.get_address(), 'Address:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertEqual(tx_result['status'], 0)
        self.assertFalse(tx_result['failure'] is None)
        print('\t(Transaction Reverted)', tx_result['failure']['message'])
        print('------ Add Blacklist by stranger end -----')

    def test_remove_blacklist_by_owner(self):
        print('------ Remove Blacklist by owner start -----')
        # Make params of add_blacklist method
        
        to = self.non_owner_wallet.get_address()
        value = 100
        params = {
            'addr': to,
        }

        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("add_blacklist") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # Sends the transaction to the network
        print('Add blacklist by owner', 'From:', self._test1.get_address(), 'Address:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        
        # Checkwhitelist
        params = {
            'addr': to
        }
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("check_blacklist") \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        
        print('BlackList status of ', to, 'Status:', response)

        params = {
            'addr': to,
        }

        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("remove_blacklist") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # Sends the transaction to the network
        print('Remove blacklist by owner', 'From:', self._test1.get_address(), 'Address:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        # Checkwhitelist
        params = {
            'addr': to
        }
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("check_blacklist") \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        print('BlackList status of ', to, 'Status:', response)

        to = self._wallet_array[0].get_address()
        value = 100
        params = {
            '_to': to,
            '_value': value,
        }
        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self.non_owner_wallet.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("transfer") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.non_owner_wallet)

        # Sends the transaction to the network
        print('Transfer Transaction', value, 'From:', self.non_owner_wallet.get_address(), 'To:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertEqual(tx_result['status'], 0)
        self.assertFalse(tx_result['failure'] is None)
        print('\t(Transaction Reverted)', tx_result['failure']['message'])

        print('------ Remove Blacklist by owner  end -----')

    def test_remove_blacklist_by_stranger(self):
        # Make params of add_blacklist method
        to = self._wallet_array[2].get_address()
        value = 100
        params = {
            'addr': to,
        }

        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(self.non_owner_wallet.get_address()) \
            .to(self._score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("remove_blacklist") \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.non_owner_wallet)
        print('Remove blacklist by stranger', 'From:', self._test1.get_address(), 'Address:', to )
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertEqual(tx_result['status'], 0)
        self.assertFalse(tx_result['failure'] is None)
        print('\t(Transaction Reverted)', tx_result['failure']['message'])