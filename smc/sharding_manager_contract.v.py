# https://ethresear.ch/t/sharding-phase-1-spec/1407

# Modified from https://github.com/ethereum/py-evm/blob/sharding/evm/vm/forks/sharding/contracts/validator_manager.v.py to comply with the above spec. WIP, some content hasn't been modified.

# Parameters
#-----------

## Shards
#--------

# Sharding manager contract address on the main net. TBD
smc_address: address

# The most significant byte of the shard ID, with most significant bit 0 for mainnet and 1 for testnet. Provisionally NETWORK_ID := 0b1000_0001 for the phase 1 testnet.
network_ID: bytes

# Number of shards
shard_count: int128

# Number of blocks in one period
period_length: int128

# The lookahead time, denominated in periods, for eligible collators to perform windback and select proposals. Provisionally LOOKAHEAD_LENGTH := 4, approximately 5 minutes.
# Number of periods ahead of current period, which the contract
# is able to return the collator of that period
lookahead_periods: int128

windback_length: int128

## Collations
#------------
collation_size: bytes
chunk_size: bytes32[32]
collator_subsidy: decimal
collator_address: address
# num_collators: int128
# empty_slots_stack_top: int128

## Registries
#------------
collator_deposit: wei_value
proposer_deposit: wei_value
min_proposer_balance: decimal
collator_lockup_length: int128
proposer_lockup_length: int128

collator_pool: public({
    # array of active collator addresses
    collator_pool_arr: address[int128]
    # size of the collator pool
    collator_pool_len: int128
    # Stack of empty collator slot indices caused by the function
    # degister_collator().
    empty_slots_stack: int128[int128]
    # The top index of the stack in empty_slots_stack.
    empty_slots_stack_top: int128
})

# Collation headers
collation_headers: public({
# Sharding participants have light-client access to collation headers via the HeaderAdded logs produced by the addHeader method. The header fields are:
    shard_id: uint256,  # pointer to shard
    parent_hash: bytes32,  # pointer to parent header
    chunk_root: bytes32, # pointer to collation body
    period: int128,
    height: int128,
    proposer_address: address,
    proposer_bid: uint256,
    proposer_signature: bytes,
    #score: int128,
}#[bytes32][int128])

# Events
CollationHeaderAdded: __log__({
    shard_id,
    parent_hash,
    chunk_root: bytes32,
    period,
    height,
    proposer_address,
    proposer_bid,
    proposer_signature,
})

Register_collator: (__log__([collator_pool.pool_index: int128,
    collator_address: address, collator_deposit: wei_value}))
Deregister_collator: (__log__([collator_pool.pool_index: int128, 
    collator_address: address, collator_deposit: wei_value}))

# from VMC: TODO: determine the signature of the above logs 
# `Register_collator` and `Deregister_collator`

collator_registry: public ({
    degistered: int128,
    # deregistered is 0 for not yet deregistered collators.
    pool_index: int128,
}[collator_address])

proposer_registry: public ({
    degistered: int128,
    balances: wei_value[uint256],
}[proposer_address])

collation_trees_struct: public ({
    # The collation tree of a shard maps collation hashes to previous collation
    # hashes truncated to 24 bytes packed into a bytes32 with the collation
    # height in the last 8 bytes.
    collation_trees: bytes32[bytes32][uint256]
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
    # Shards
    #self.smc_address = 
    self.network_ID: bytes[8] = 0x10000001
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
    
@internal
def is_stack_empty() -> bool:
    return (self.collator_pool.empty_slots_stack_top == 0)

# Pushes one num to empty_slots_stack
@internal
def stack_push(index: int128):
    self.collator_pool.empty_slots_stack[self.collator_pool.empty_slots_stack_top] = index
    self.collator_pool.empty_slots_stack_top += 1

# Pops one num out of empty_slots_stack
@internal
def stack_pop() -> int128:
    if self.is_stack_empty():
        return -1
    # empty_slots_stack_top_temp = self.empty_slots_stack_top 
    self.collator_pool.empty_slots_stack_top -= 1
    return self.collator_pool.empty_slots_stack.pop(self.collator_pool.empty_slots_stack_top)
    #return self.collator_pool.empty_slots_stack[self.collator_pool.empty_slots_stack_top]
    # https://docs.python.org/3.6/library/array.html?highlight=pop%20array#array.array.pop	

# Register a collator. Adds an entry to collator_registry, updates the
# collator pool (collator_pool, collator_pool_len, etc.), locks a deposit
# of size COLLATOR_DEPOSIT, and returns True on success. Checks:

#    Deposit size: msg.value >= COLLATOR_DEPOSIT
#    Uniqueness: collator_registry[msg.sender] does not exist

# Checks if empty_slots_stack_top is empty
@public
@payable
def register_collator() -> bool:
	collator_address = msg.sender
	assert msg.value >= collator_deposit
	assert self.collator_registry[collator_address].pool_index = None
	# Find the empty slot index in the collator pool.
    if not self.is_stack_empty():
    	index = self.stack_pop()	
	else:
        index = self.collator_pool.collator_pool_len 
			# collator_pool_arr indices are from 0 to collator_pool_len -1. ;)
	self.collator_registry[collator_address] = {
        deregistered: 0,
        pool_index: index,
    }
	self.collator_pool.collator_pool_len +=1
	self.collator_pool.collator_pool_arr[index] = collator_address
	
	log.Register_collator(index, collator_address, collator_deposit)
	
    return True
    
# TODO: move this bookmark as the content below it is modified from the original.

# Returns the current maximum index for validators mapping
@internal
def get_validators_max_index() -> int128:
    zero_addr = 0x0000000000000000000000000000000000000000
    activate_validator_num = 0
    all_validator_slots_num = self.num_validators + self.empty_slots_stack_top

    # TODO: any better way to iterate the mapping?
    for i in range(1024):
        if i >= all_validator_slots_num:
            break
        if self.validators[i].addr != zero_addr:
            activate_validator_num += 1
    return activate_validator_num + self.empty_slots_stack_top


# Verifies that `msg.sender == validators[validator_index].addr`. if it is removes the validator
# from the validator set and refunds the deposited ETH.
@public
@payable
def withdraw(validator_index: int128) -> bool:
    validator_addr = self.validators[validator_index].addr
    validator_deposit = self.validators[validator_index].deposit
    assert msg.sender == validator_addr
    self.is_validator_deposited[validator_addr] = False
    self.validators[validator_index] = {
        deposit: 0,
        addr: None,
    }
    self.stack_push(validator_index)
    self.num_validators -= 1

    send(validator_addr, validator_deposit)

    log.Withdraw(validator_index, validator_addr, validator_deposit)

    return True


# Uses a block hash as a seed to pseudorandomly select a signer from the validator set.
# [TODO] Chance of being selected should be proportional to the validator's deposit.
# Should be able to return a value for the current period or any future period up to.
@public
@constant
def get_eligible_proposer(shard_id: int128, period: int128) -> address:
    assert period >= self.lookahead_periods
    assert (period - self.lookahead_periods) * self.period_length < block.number
    assert self.num_validators > 0
    return self.validators[
        as_num128(
            num256_mod(
                as_uint256(
                    sha3(
                        concat(
                            # TODO: should check further if this can be further optimized or not
                            #       e.g. be able to get the proposer of one period earlier
                            blockhash((period - self.lookahead_periods) * self.period_length),
                            as_bytes32(shard_id),
                        )
                    )
                ),
                as_uint256(self.get_validators_max_index()),
            )
        )
    ].addr


# Attempts to process a collation header, returns True on success, reverts on failure.
@public
def add_header(
        shard_id: num,
        expected_period_number: int128,
        period_start_prevhash: bytes32,
        parent_hash: bytes32,
        transaction_root: bytes32,
        collation_coinbase: address,  # TODO: cannot be named `coinbase` since it is reserved
        state_root: bytes32,
        receipt_root: bytes32,
        collation_number: int128) -> bool:  # TODO: cannot be named `number` since it is reserved
    zero_addr = 0x0000000000000000000000000000000000000000

    # Check if the header is valid
    assert (shard_id >= 0) and (shard_id < self.shard_count)
    assert block.number >= self.period_length
    assert expected_period_number == floor(decimal(block.number / self.period_length))
    assert period_start_prevhash == blockhash(expected_period_number * self.period_length - 1)

    # Check if this header already exists
    header_bytes = concat(
        as_bytes32(shard_id),
        as_bytes32(expected_period_number),
        period_start_prevhash,
        parent_hash,
        transaction_root,
        as_bytes32(collation_coinbase),
        state_root,
        receipt_root,
        as_bytes32(collation_number),
    )
    entire_header_hash = sha3(header_bytes)
    assert self.collation_headers[shard_id][entire_header_hash].score == 0
    # Check whether the parent exists.
    # if (parent_hash == 0), i.e., is the genesis,
    # then there is no need to check.
    if parent_hash != as_bytes32(0):
        assert self.collation_headers[shard_id][parent_hash].score > 0
    # Check if only one collation in one period perd shard
    assert self.period_head[shard_id] < expected_period_number

    # Check the signature with validation_code_addr
    validator_addr = self.get_eligible_proposer(shard_id, block.number / self.period_length)
    assert validator_addr != zero_addr
    assert msg.sender == validator_addr

    # Check score == collation_number
    _score = self.collation_headers[shard_id][parent_hash].score + 1
    assert collation_number == _score

    # Add the header
    self.collation_headers[shard_id][entire_header_hash] = {
        parent_hash: parent_hash,
        score: _score,
    }

    # Update the latest period number
    self.period_head[shard_id] = expected_period_number

    # Determine the head
    is_new_head = False
    if _score > self.collation_headers[shard_id][self.shard_head[shard_id]].score:
        self.shard_head[shard_id] = entire_header_hash
        is_new_head = True

    # Emit log
    log.CollationAdded(
        shard_id,
        expected_period_number,
        period_start_prevhash,
        parent_hash,
        transaction_root,
        collation_coinbase,
        state_root,
        receipt_root,
        collation_number,
        is_new_head,
        _score,
    )

    return True


# Returns the gas limit that collations can currently have (by default make
# this function always answer 10 million).
@public
@constant
def get_collation_gas_limit() -> int128:
    return 10000000


# Records a request to deposit msg.value ETH to address to in shard shard_id
# during a future collation. Saves a `receipt ID` for this request,
# also saving `msg.sender`, `msg.value`, `to`, `shard_id`, `startgas`,
# `gasprice`, and `data`.
@public
@payable
def tx_to_shard(
        to: address,
        shard_id: int128,
        tx_startgas: int128,
        tx_gasprice: int128,
        data: bytes <= 4096) -> int128:
    self.receipts[self.num_receipts] = {
        shard_id: shard_id,
        tx_startgas: tx_startgas,
        tx_gasprice: tx_gasprice,
        value: msg.value,
        sender: msg.sender,
        to: to,
        data: data,
    }
    receipt_id = self.num_receipts
    self.num_receipts += 1

    # TODO: determine the signature of the log TxToShard
    raw_log(
        [
            sha3("tx_to_shard(address,int128,int128,int128,bytes4096)"),
            as_bytes32(to),
            as_bytes32(shard_id),
        ],
        concat('', as_bytes32(receipt_id)),
    )

    return receipt_id


# Updates the tx_gasprice in receipt receipt_id, and returns True on success.
@public
@payable
def update_gasprice(receipt_id: int128, tx_gasprice: int128) -> bool:
    assert self.receipts[receipt_id].sender == msg.sender
    self.receipts[receipt_id].tx_gasprice = tx_gasprice
    return True

