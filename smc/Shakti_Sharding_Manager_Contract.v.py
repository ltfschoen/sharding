# Developed from the draft phase 1 spec: https://ethresear.ch/t/sharding-phase-1-spec/1407
# As well as the validator_manager_contract:
# https://github.com/ethereum/py-evm/blob/sharding/evm/vm/forks/sharding/contracts/validator_manager.v.py

# I've named it Shakti for a shorter name, that means the primordial cosmic energy
# that upholds the phenomenal cosmos, which seems appropriate, given that the SMC
# is managing "universes" of shards. For unambiguity where necessary it can be called
# the Shakti contract or SMC.
# https://en.wikipedia.org/wiki/Shakti

# Copyright: Unlicense, no rights reserved. Author: James Ray

# Doesn't work: invalid top-level statement
# import requests, json

# FYI: see https://github.com/ethereum/vyper/blob/master/docs/logging.rst
# Events
CollationHeaderAdded: event({
    shard_id: uint256,
    parent_hash: bytes32,
    chunk_root: bytes32,
    period: int128,
    height: int128,
    proposer_address: address,
    proposer_bid: uint256,
    proposer_signature: bytes <= 8192, # 1024*8 for general signature schemes
})

Register_collator: event({
    pool_index: int128,
    collator_address: indexed(address),
    deregistered: indexed(int128),
    collation_deposit: indexed(wei_value)
})

Deregister_collator: event({
    pool_index: int128, 
    collator_address: indexed(address),
    deregistered: indexed(int128)
})

Release_collator: event({
    pool_index: int128, 
    collator_address: indexed(address),
    deregistered: indexed(int128)
})

Register_proposer: event({
    proposer_address: address,
    deregistered: indexed(int128),
    proposer_deposit: indexed(wei_value)
})

Deregister_proposer: event({
    proposer_address: address,
    deregistered: indexed(int128)
})

Release_proposer: event({
    proposer_address: address,
    deregistered: indexed(int128),
    proposer_balance: indexed(wei_value)
})


# Parameters
#-----------

# latest_block_number: uint256

## Shards
#--------

# Sharding manager contract address on the main net. TBD
smc_address: address

# The most significant byte of the shard ID, with most significant bit 0 for 
# mainnet and 1 for testnet. Provisionally NETWORK_ID := 0b1000_0001 for the 
# phase 1 testnet.
network_ID: bytes <= 8

# Number of shards
shard_count: int128

# Number of blocks in one period
period_length: int128
period_length_as_uint256: uint256

# The lookahead time, denominated in periods, for eligible collators to perform 
# windback and select proposals. Provisionally LOOKAHEAD_LENGTH := 4, 
# approximately 5 minutes.
# Number of periods ahead of current period, which the contract
# is able to return the collator of that period
lookahead_length: int128

windback_length: int128

## Collations
#------------
collation_size: int128
chunk_size: int128
collator_subsidy: decimal
collator_address: address

## Registries
#------------
collator_deposit: wei_value
proposer_deposit: wei_value
min_proposer_balance: decimal
collator_lockup_length: int128
proposer_lockup_length: int128
pool_index_temp: int128
proposer_address: address

collator_pool: public({
    # array of active collator addresses
    collator_pool_arr: address[int128],
    # size of the collator pool
    collator_pool_len: int128,
    # Stack of empty collator slot indices caused by the function
    # degister_collator().
    empty_slots_stack: int128[int128],
    # The top index of the stack in empty_slots_stack.
    empty_slots_stack_top: int128
})

# Collation headers
collation_header: public({
# Sharding participants have light-client access to collation headers via the 
# HeaderAdded logs produced by the addHeader method. The header fields are:
    shard_id: uint256,  # pointer to shard
    parent_hash: bytes32,  # pointer to parent header
    chunk_root: bytes32, # pointer to collation body
    period: int128,
    height: int128,
    proposer_address: address,
    proposer_bid: uint256,
    proposer_signature: bytes32,
    collation_number: uint256,
})#[bytes32][int128])

# from VMC: TODO: determine the signature of the above logs 
# `Register_collator` and `Deregister_collator`

collator_registry: public ({
    deregistered: int128,
    # deregistered is 0 for not yet deregistered collators.
    pool_index: int128
}[address])

proposer_registry: public ({
    deregistered: int128,
    balances: wei_value
}[address])

collation_trees_struct: public ({
    # The collation tree of a shard maps collation hashes to previous collation
    # hashes truncated to 24 bytes packed into a bytes32 with the collation
    # height in the last 8 bytes.
    collation_trees: bytes32[bytes32][uint256],
    # This contains the period of the last update for each shard.
    last_update_periods: int128[uint256]
})

availability_challenges_struct: public ({
    # availability_challenges:
    # availability challenges counter
    availability_challenges_len: int128
})

@public
def __init__():
    #self.latest_block_number = convert(5353011, 'uint256')
    # Shards
    #self.smc_address = 
    self.network_ID = "10000001"
    self.shard_count = 100			# shards
    self.period_length = 5			# block times
    self.lookahead_length = 4		# periods
    self.windback_length = 25		# collations

    # Collations
    self.collation_size	= 1048576	# 2^20 bytes
    self.chunk_size = 32			# bytes
    self.collator_subsidy = 0.001 	# vETH
    self.collator_pool.collator_pool_len = 0		
    self.collator_pool.empty_slots_stack_top = 0

    # Registries
    self.collator_deposit = 1000000000000000000000 		# 10^21 wei = 1000 ETH
    #collator_subsidy = 1000000000000000				# 10^15 wei = 0.001 ETH
    self.min_proposer_balance = 10000000000000			# 10^17 wei = 0.1 ETH
    self.collator_lockup_length = 16128					# periods
    self.proposer_lockup_length = 48					# periods
    # 10 ** 20 wei = 100 ETH
    #self.deposit_size = 100000000000000000000

#@private
#def get_latest_block_number() -> uint256:
#   Link: https://api.etherscan.io/api?module=proxy&action=eth_blockNumber
#    &apikey='your API key'
#    payload = {'module': 'proxy', 'action': 'eth_blockNumber', \
#        'apikey' : your API key}
#   requests...json() returns a string containing a hexadecimal number, e.g. 
#       "0x51ac9f". Need to convert it to a uint256.
#   There is no support for strings, so working with this result doesn't seem 
#   feasible, e.g. you can't slice the result or convert it to a uint256.
#    latest_block_number = convert(slice(requests.get(\
#        "https://api.etherscan.io/api", params=payload).json()\
#        ["result"]), 'bytes')
#    return latest_block_number

# Try to find out how to use an oracle instead.

# Apparently block.number will suffice, but check.

# Checks if empty_slots_stack_top is empty    
@private
def is_stack_empty() -> bool:
    return (self.collator_pool.empty_slots_stack_top == 0)

# Pushes one num to empty_slots_stack. Why not just use the push method?
@private
def stack_push(index: int128):
    self.collator_pool.empty_slots_stack[self.collator_pool \
        .empty_slots_stack_top] = index
    #(self.collator_pool.empty_slots_stack[
    #TODO: re-add this: self.collator_pool.empty_slots_stack_top] = index)
    self.collator_pool.empty_slots_stack_top += 1
    
# Pops one num out of empty_slots_stack. Why not just use the pop method?
@private
def stack_pop() -> int128:
    if self.is_stack_empty():
        return -1
    self.collator_pool.empty_slots_stack_top -= 1
    return (self.collator_pool.empty_slots_stack[self.collator_pool.
        empty_slots_stack_top])

# What if someone wants to (de)register a collator or a proposer on  
# someone else's behalf, or wants to register with a different  
# address from msg.sender, but that they own? For simplicity and
# security just allow only  msg.sender to (de)register msg.sender.

# Register a collator. Adds an entry to collator_registry, updates the
# collator pool (collator_pool, collator_pool_len, etc.), locks a deposit
# of size COLLATOR_DEPOSIT, and returns True on success. Checks:

#    Deposit size: msg.value >= COLLATOR_DEPOSIT
#    Uniqueness: collator_registry[msg.sender] does not exist

# Checks if empty_slots_stack_top is empty
@public
@payable
def register_collator() -> bool:
    self.collator_address = msg.sender
    assert msg.value >= self.collator_deposit
    # TODO: make sure that it will return 0 if it doesn't exist, not None.
    assert not self.collator_registry[self.collator_address].pool_index == 0
    # Find the empty slot index in the collator pool.
    if not self.is_stack_empty():
        self.pool_index_temp = self.stack_pop()	
    else:
        self.pool_index_temp = self.collator_pool.collator_pool_len 
        # collator_pool_arr indices are from 0 to collator_pool_len - 1. ;)
    self.collator_registry[self.collator_address].deregistered = 0 
    self.collator_registry[self.collator_address].pool_index \
        = self.pool_index_temp

    self.collator_registry[self.collator_address] = {
        deregistered : 0,
        pool_index : self.pool_index_temp
    }

    (log.Register_collator(self.pool_index_temp, self.collator_address,
        self.collator_registry[self.collator_address].deregistered, \
        self.collator_deposit))

    return True
    
    
# Verifies that `msg.sender == collators[collator_index].addr`.  If it is then
# remove the collator rom the collator pool and refund the deposited ETH.
@public
def deregister_collator() -> bool:
    self.collator_address = msg.sender
    assert self.collator_registry[self.collator_address].deregistered == 0
    self.collator_registry[self.collator_address].deregistered \
        = self.collator_lockup_length

    self.stack_push(self.collator_registry[self.collator_address].pool_index)
    self.collator_pool.collator_pool_len -= 1
    
    log.Deregister_collator(self.collator_registry[self.collator_address]\
        .pool_index, self.collator_address, \
        self.collator_registry[self.collator_address].deregistered)

    return True

# Removes an entry from collator_registry, releases the collator deposit, and
# returns True on success. Checks:

#   Authentication: collator_registry[msg.sender] exists
#   Deregistered: collator_registry[msg.sender].deregistered != 0
#   Lockup: floor(collation_header.number / period_length) 
#       > collator_registry[msg.sender].deregistered + collator_lockup_length
    
@public
@payable
def release_collator() -> bool:
    self.collator_address = msg.sender
    assert self.collator_registry[self.collator_address].deregistered != 0
    assert floor(block.number / self.period_length) > self.collator_registry\
        [msg.sender].deregistered + self.collator_lockup_length
        
    send(self.collator_address, self.collator_deposit)
    self.collator_registry[self.collator_address] = {
        deregistered : 0,
        pool_index : 0
    }

    log.Release_collator(self.collator_registry[self.collator_address]\
        .pool_index, self.collator_address, \
        self.collator_registry[self.collator_address].deregistered)
    
    return True
    
# register_proposer() returns bool: Equivalent of register_collator(),
# without the collator pool updates.

@public
@payable
def register_proposer() -> bool:
    self.proposer_address = msg.sender
    # Make sure the proposer doesn't already exist in the registry.
    assert not self.proposer_registry[self.proposer_address].balances != 0
    assert msg.value >= self.proposer_deposit
    # TODO: make sure that it will return 0 if it doesn't exist, not None.

    self.proposer_registry[self.proposer_address] = {
        deregistered : 0,
        balances : msg.value
    }

    log.Register_proposer(self.proposer_address,\
        self.proposer_registry[self.proposer_address].deregistered, msg.value)

    return True

# deregister_proposer() returns bool: Equivalent to  
# deregister_collator(), without the collator pool updates.

@public
def deregister_proposer() -> bool:
    self.proposer_address = msg.sender
    assert self.proposer_registry[self.proposer_address].deregistered != 0
    self.proposer_registry[self.proposer_address].deregistered \
        = self.proposer_lockup_length
    
    log.Deregister_proposer(self.proposer_address, \
        self.proposer_registry[self.proposer_address].deregistered)

    return True

# release_proposer() returns bool: Equivalent of release_collator().
# WARNING: The proposer balances need to be emptied before calling this method.
# Why? Can't they be cleared during the method?

@public
@payable
def release_proposer() -> bool:
    self.proposer_address = msg.sender
    assert self.proposer_registry[self.proposer_address].deregistered != 0
    
    assert floor(block.number / self.period_length) > self.collator_registry\
        [msg.sender].deregistered + self.collator_lockup_length
    send(self.proposer_address, self.proposer_registry\
        [self.proposer_address].balances)
        
    self.proposer_registry[self.proposer_address] = {
        deregistered = 0,
        balances = 0
    }

    log.Release_proposer(self.proposer_address, \
        self.proposer_registry[self.proposer_address].deregistered,\
        self.proposer_registry[self.proposer_address].balances)
    
    return True

# proposer_add_balance(uint256 shard_id) returns bool: Adds msg.value to the
# balance of the proposer on shard_id, and returns True on success. Checks:

#    Shard: shard_id against NETWORK_ID and SHARD_COUNT
#    Authentication: proposer_registry[msg.sender] exists

# proposer_withdraw_balance(uint256 shard_id) returns bool: Withdraws the 
# balance of a proposer on shard_id, and returns True on success. Checks:

#    Shard: shard_id against NETWORK_ID and SHARD_COUNT
#    Authentication: proposer_registry[msg.sender] exists

# Collation trees

# get_eligible_collator(uint256 shard_id, uint256 period) returns address: 
# Uses the blockhash at block number (period - LOOKAHEAD_LENGTH) 
# * PERIOD_LENGTH) and shard_id to pseudo-randomly select an eligible
# collator from the collator pool, and returns the address of the 
# eligible collator. Checks:
#       Shard: shard_id against NETWORK_ID and SHARD_COUNT
#        Period: period == floor(block.number / PERIOD_LENGTH)
#        Non-empty pool: collator_pool_len > 0



# compute_header_hash(uint256 shard_id, bytes32 parent_hash, 
#       bytes32 chunk_root, uint256 period, address proposer_address,
#       uint256 proposer_bid) returns bytes32: Returns the header hash.




# add_header(uint256 shard_id, bytes32 parent_hash, bytes32 chunk_root,
#       uint256 period, address proposer_address, uint256 proposer_bid,
#       bytes proposer_signature) returns bool: 
# Calls compute_header_hash(...), extends the collation tree of shard_id,
# burns the proposer_bid from the proposer’s balance at shard_id, issues
# a HeaderAdded log, and returns True on success. Checks:
#       Shard: shard_id against NETWORK_ID and SHARD_COUNT
#       Collator eligibility: msg.sender == get_eligible_collator(
#            shard_id, period)
#       Parent exists: collation_trees[shard_id]
#           [compute_header_hash(...)] exists
#       Correct period: period == floor(block.number / PERIOD_LENGTH)
#       Unique update: period != last_update_periods[shard_id]
#       Proposer balance: proposer_registry[proposer_address].balances
#           [shard_id] >= max(proposer_bid, MIN_PROPOSER_BALANCE)
#       Proposer signature: proposer_signature matches 
#           compute_header_hash(...) and proposer_address

#Slashing

# proposal_commitment_slashing(uint256 shard_id, bytes32 collation_hash,
#       uint256 height, uint256 left_hash, uint256 right_hash, 
#       bytes signature) returns bool: 
# Slashes a collator that called add_header with a non-committed 
# proposal. Checks:
#        Shard: shard_id against NETWORK_ID and SHARD_COUNT
#        Collation tree: collation_trees[shard_id][collation_hash] exists
#        Height: collation_trees[shard_id][collation_hash] matches height
#        Signature: signature matches height, left_hash and right_hash
#        Slashing condition: left_hash < collation_hash and 
#           collation_hash < right_hash



#    availability_challenge(): TBD
#    availability_response(): TBD
#    availability_slashing(): TBD
