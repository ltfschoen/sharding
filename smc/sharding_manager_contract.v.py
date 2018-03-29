# https://ethresear.ch/t/sharding-phase-1-spec/1407

# Modified from 
# https://github.com/ethereum/py-evm/blob/sharding/evm/vm/forks/sharding/contracts/validator_manager.v.py
# to comply with the above spec. WIP, some content hasn't been modified.

# Events
CollationHeaderAdded: event({
    shard_id: uint256,
    parent_hash: bytes32,
    chunk_root: bytes32,
    period: int128,
    height: int128,
    proposer_address: address,
    proposer_bid: uint256,
    proposer_signature: bytes <= 8192 # 1024*8 for general signature schemes
})

Register_collator: event({
    pool_index: int128,
    collator_address: indexed(address),
    collator_deposit: wei_value,
})

Deregister_collator: event({
    pool_index: int128, 
    collator_address: indexed(address),
    collator_deposit: wei_value,
})

# Parameters
#-----------

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

collator_pool: public({
    # array of active collator addresses
    collator_pool_arr: address[int128],
    # size of the collator pool
    collator_pool_len: int128,
    # Stack of empty collator slot indices caused by the function
    # degister_collator().
    empty_slots_stack: int128[int128],
    # The top index of the stack in empty_slots_stack.
    empty_slots_stack_top: int128,
})

# Collation headers
collation_headers: public({
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
})#[bytes32][int128])



# from VMC: TODO: determine the signature of the above logs 
# `Register_collator` and `Deregister_collator`

collator_registry: public ({
    deregistered: int128,
    # deregistered is 0 for not yet deregistered collators.
    pool_index: int128,
}[address])

proposer_registry: public ({
    deregistered: int128,
    balances: wei_value[uint256],
}[address])

collation_trees_struct: public ({
    # The collation tree of a shard maps collation hashes to previous collation
    # hashes truncated to 24 bytes packed into a bytes32 with the collation
    # height in the last 8 bytes.
    collation_trees: bytes32[bytes32][uint256],
    # This contains the period of the last update for each shard.
    last_update_periods: int128[uint256],
})

availability_challenges_struct: public ({
    # availability_challenges:
    # availability challenges counter
    availability_challenges_len: int128,
})

@public
def __init__():
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
    assert not self.collator_registry[self.collator_address].pool_index == 0
    # Find the empty slot index in the collator pool.
    if not self.is_stack_empty():
        self.pool_index_temp = self.stack_pop()	
    else:
        self.pool_index_temp = self.collator_pool.collator_pool_len 
        # collator_pool_arr indices are from 0 to collator_pool_len - 1. ;)
    self.collator_registry[self.collator_address].deregistered = 0 
    self.collator_registry[self.collator_address].pool_index = self.pool_index_temp#= {
    #self.collator_registry[self.collator_address] = {
    #    deregistered = 0,
    #    pool_index = self.pool_index_temp,
    #}
    self.collator_pool.collator_pool_len +=1
    self.collator_pool.collator_pool_arr[self.pool_index_temp] = \
        self.collator_address

    (log.Register_collator(self.pool_index_temp, self.collator_address,
        self.collator_deposit))

    return True
