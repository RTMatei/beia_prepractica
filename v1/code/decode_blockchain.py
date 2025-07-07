from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

receiver_address = web3.eth.accounts[1].lower()

latest_block = web3.eth.block_number
print(f"Latest block: {latest_block}")

start_block = max(latest_block - 10, 0)

for block_num in range(start_block, latest_block + 1):
    block = web3.eth.get_block(block_num, full_transactions=True)
    print(f"\nBlock {block_num} ({len(block.transactions)} txs)")

    for tx in block.transactions:
        if tx.to and tx.to.lower() == receiver_address:
            print(f"Tx Hash: {tx.hash.hex()}")
            print(f"From: {tx['from']}")
            print(f"To: {tx.to}")
            print(f"Input (hex): {tx.input}")

            print("-" * 40)
