import json
from pathlib import Path
from typing import NamedTuple

from eth_typing.evm import HexAddress

from hmyweb3.bootstrap import w3

with open(Path(__file__).parent/'mochi_abi.json') as f:
    MOCHI_CHEF_ABI = json.load(f)

class PoolInfo(NamedTuple):
    lpToken: HexAddress
    allocPoint: int
    lastRewardBlock: int
    accCakePerShare: int

class UserInfo(NamedTuple):
    amount: int
    name: int

MOCHI_CHEF_ADDR = "0x55E805E0fc64E1F3f771F9afaADb325F48dfadfA"

mochi_chef_contract = w3.hmy.contract(address=MOCHI_CHEF_ADDR, abi=MOCHI_CHEF_ABI)
mochi_chef_call = mochi_chef_contract.caller()

mochi_chef_call.poolInfo, mochi_chef_call._poolInfo = (lambda *args, **kwargs: PoolInfo(*mochi_chef_call._poolInfo(*args, **kwargs))), mochi_chef_call.poolInfo
mochi_chef_call.userInfo, mochi_chef_call._userInfo = (lambda *args, **kwargs: UserInfo(*mochi_chef_call._userInfo(*args, **kwargs))), mochi_chef_call.userInfo
