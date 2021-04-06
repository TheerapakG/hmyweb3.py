import json
from pathlib import Path

from demo.mochi.mochi import MOCHI_CHEF_ADDR, mochi_chef_call, w3

address = YOUR_ADDRESS_AS_HEXSTR

block_number = w3.hmy.block_number
multiplier = mochi_chef_call.getMultiplier(block_number, block_number+1)
reward_per_block = mochi_chef_call.mochiPerBlock()
rewards_per_week = ((reward_per_block/10**18)*multiplier*604800)/2

pool_count = int(mochi_chef_call.poolLength())
total_alloc_points = mochi_chef_call.totalAllocPoint()

print(f'Found {pool_count} pools.')
print('Showing incentivized pools only.')

with open(Path(__file__).parent/'hrc20_abi.json') as f:
    HRC20_ABI = json.load(f)

with open(Path(__file__).parent/'uni_abi.json') as f:
    UNI_ABI = json.load(f)

def get_hmy_uni_pool(pool, pooladdress, stakingaddress):
    reserves = pool.caller().getReserves()
    q0 = reserves[0]
    q1 = reserves[1]
    decimals = pool.caller().decimals()
    token0 = pool.caller().token0()
    token1 = pool.caller().token1()
    return { 
        'name': pool.caller().name(),
        'symbol': pool.caller().symbol(),
        'address': pooladdress,
        'token0': token0,
        'q0': q0,
        'token1': token1,
        'q1': q1,
        'stakingAddress': stakingaddress,
        'staked': pool.caller().balanceOf(stakingaddress)/(10**decimals),
        'decimals': decimals,
        'unstaked': pool.caller().balanceOf(address)/(10**decimals),
        'contract': pool,
        'tokens': [token0, token1]
    }

def gethrc20(token, address, stakingAddress):
    if (address == "0x0000000000000000000000000000000000000000"):
        return {
            'address': address,
            'name': "Harmony",
            'symbol': "Harmony",
            'decimals': 18,
            'staked': 0,
            'unstaked': 0,
            'contract': None,
            'tokens':[address]
        }

    decimals = token.caller().decimals()
    return {
        'address': address,
        'name': token.caller().name(),
        'symbol': token.caller().symbol(),
        'decimals': decimals,
        'staked':  token.caller().balanceOf(stakingAddress)/(10**decimals),
        'unstaked': token.caller().balanceOf(address)/(10**decimals),
        'contract': token,
        'tokens': [address]
    }

def get_hmy_token(tokenaddress, stakingaddress):
    if (address == "0x0000000000000000000000000000000000000000"):
        return gethrc20(None, tokenaddress, "")
    try:
        pool = w3.hmy.contract(address=tokenaddress, abi=UNI_ABI)
        uni_pool = get_hmy_uni_pool(pool, tokenaddress, stakingaddress)
        return uni_pool
    except Exception as e:
        try:
            hrc20 = w3.hmy.contract(address=tokenaddress, abi=HRC20_ABI)
            hrc20tok = gethrc20(hrc20, tokenaddress, stakingaddress)
            return hrc20tok
        except Exception as e:
            print(e)
            print(f"Couldn't match {tokenaddress} to any known token type.")

def get_pool_info(index):
    pool_info =  mochi_chef_call.poolInfo(index)
    if (pool_info.allocPoint == 0):
        return {
            'address': pool_info.lpToken,
            'allocPoints': 0,
            'poolToken': None,
            'userStaked': 0,
            'pendingRewardTokens': 0,
        }
        
    poolToken = get_hmy_token(pool_info.lpToken, MOCHI_CHEF_ADDR)
    userInfo = mochi_chef_call.userInfo(index, address)
    pendingRewardTokens = mochi_chef_call.pendingMochi(index, address)
    staked = userInfo.amount / 10 ** poolToken['decimals']
    return {
        'address': pool_info.lpToken,
        'allocPoints': pool_info.allocPoint,
        'poolToken': poolToken,
        'userStaked': staked,
        'pendingRewardTokens': pendingRewardTokens/(10**18),
    }

reward_token_address = mochi_chef_call.mochi()
pool_infos = [get_pool_info(i) for i in range(pool_count)]

token_addresses = {token for pool_info in pool_infos if pool_info['poolToken'] for token in pool_info['poolToken']['tokens']}
tokens = {token_address: get_hmy_token(token_address, MOCHI_CHEF_ADDR) for token_address in token_addresses}

print("Finished reading smart contracts.")

for pool_info in pool_infos:
    pool_token = pool_info['poolToken']
    if pool_token:
        print()
        token0_sym = tokens[pool_token['token0']]['symbol']
        token1_sym = tokens[pool_token['token1']]['symbol']
        pool_lp_name = ' '.join((token0_sym, '<=>', token1_sym, pool_token['symbol']))
        print(pool_lp_name)
        pool_staked = pool_token['staked']
        user_staked = pool_info['userStaked']
        print('Staked:', f'{pool_staked:.4f}', pool_token['symbol'])
        pool_ratio = pool_info['userStaked']/pool_token['staked']
        print('You are staking', f'{user_staked:.4f}', pool_lp_name, f'({pool_ratio*100:.2f}% of the pool)')
        q0_ratio = pool_token['q0']*pool_ratio/(10**tokens[pool_token['token0']]['decimals'])
        q1_ratio = pool_token['q1']*pool_ratio/(10**tokens[pool_token['token1']]['decimals'])
        print('Your LP tokens comprise of', f'{q0_ratio:.4f}', token0_sym, '+', f'{q1_ratio:.4f}', token1_sym)
