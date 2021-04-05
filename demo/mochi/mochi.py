import json
from pathlib import Path

from hmyweb3.bootstrap import w3

with open(Path(__file__).parent/'mochi_abi.json') as f:
    MOCHI_CHEF_ABI = json.load(f)

MOCHI_CHEF_ADDR = "0x55E805E0fc64E1F3f771F9afaADb325F48dfadfA"

mochi_chef_contract = w3.hmy.contract(address=MOCHI_CHEF_ADDR, abi=MOCHI_CHEF_ABI)
mochi_chef_call = mochi_chef_contract.caller()
