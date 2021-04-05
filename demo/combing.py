from eth_account import Account
from hmyweb3.bootstrap import w3

total_txs = 0
total_one = 0

for privkey in range(0x0000000000000000000000000000000000000000000000000000000000000001, 0x00000000000000000000000000000000000000000000000000000000FFFFFFFF):
    strprivkey = f'0x{privkey:0>64x}'
    account = Account.from_key(strprivkey)
    txs = w3.hmy.get_transaction_count(account.address)
    balance = w3.hmy.get_balance(account.address)/(10^18)
    total_one += balance
    print('searched', privkey, 'key. found', total_one, 'ONE. and', total_txs, 'transactions.')
    if balance > 1e18:
        print('FOUND', privkey, balance, 'WITH', txs, 'TRANSACTIONS')
