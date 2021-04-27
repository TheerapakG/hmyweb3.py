import json
from pathlib import Path
from typing import NamedTuple

from eth_typing.evm import HexAddress

from hmyweb3.bootstrap import w3

with open(Path(__file__).parent/'viper_abi.json') as f:
    VIPER_CHEF_ABI = json.load(f)

class PoolInfo(NamedTuple):
    lpToken: HexAddress
    allocPoint: int
    lastRewardBlock: int
    accCakePerShare: int

class UserInfo(NamedTuple):
    amount: int
    rewardDebt: int
    rewardDebtAtBlock: int
    lastWithdrawBlock: int
    firstDepositBlock: int
    blockdelta: int
    lastDepositBlock: int

VIPER_CHEF_ADDR = "0x7AbC67c8D4b248A38B0dc5756300630108Cb48b4"

viper_chef_contract = w3.hmy.contract(address=VIPER_CHEF_ADDR, abi=VIPER_CHEF_ABI)
viper_chef_call = viper_chef_contract.caller()

viper_chef_call.poolInfo, viper_chef_call._poolInfo = (lambda *args, **kwargs: PoolInfo(*viper_chef_call._poolInfo(*args, **kwargs))), viper_chef_call.poolInfo
viper_chef_call.userInfo, viper_chef_call._userInfo = (lambda *args, **kwargs: UserInfo(*viper_chef_call._userInfo(*args, **kwargs))), viper_chef_call.userInfo
