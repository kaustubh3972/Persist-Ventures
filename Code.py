import requests
import time
from web3 import Web3

# Constants
HERO_TOKEN_ADDRESS = "0x..."  # Change it
SOLANA_ADDRESS = "0x..."  # Change it
MONITOR_INTERVAL = 60  # in seconds
TIMEOUT = 7200  # in seconds
INFURA_PROJECT_ID = "YOUR_INFURA_PROJECT_ID"
ETHERSCAN_API_KEY = "YOUR_ETHERSCAN_API_KEY"
PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # Change it
WALLET_ADDRESS = "YOUR_WALLET_ADDRESS"  # Change it

# Initializing Web3
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"))

# Transaction history of a wallet
def get_transaction_history(wallet_address):
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={wallet_address}&sort=asc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching transactions: {response.status_code}")
        return []
    
    data = response.json()
    if data["status"] != "1":
        print(f"API Error: {data['message']}")
        print(f"Full API Response: {data}")
        return []
    
    transactions = data.get("result", [])
    return transactions

# Fetch all token transfers involving the Hero token
def get_all_hero_token_transfers():
    transfers = []
    page = 1
    
    while True:
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={HERO_TOKEN_ADDRESS}&page={page}&offset=100&sort=asc&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching token transfers: {response.status_code}")
            break
        
        data = response.json()
        if data["status"] != "1":
            print(f"API Error: {data['message']}")
            print(f"Full API Response: {data}")
            break
        
        result = data.get("result", [])
        if not result:
            break
        
        transfers.extend(result)
        page += 1
        time.sleep(1)  

    return transfers

# Identifying wallets that only trade the Hero token
def identify_wallets():
    # Getting all transfers involving the Hero token
    transfers = get_all_hero_token_transfers()
    
    # Extractinng unique wallet addresses from these transactions
    wallet_addresses = set()
    for tx in transfers:
        from_address = tx['from']
        to_address = tx['to']
        wallet_addresses.add(from_address)
        wallet_addresses.add(to_address)
    
    hero_only_wallets = []
    for wallet in wallet_addresses:
        transactions = get_transaction_history(wallet)
        if all(tx['contractAddress'].lower() == HERO_TOKEN_ADDRESS.lower() for tx in transactions):
            hero_only_wallets.append(wallet)
    
    return hero_only_wallets

# Monitoring transactions
def monitor_transactions(wallet_address):
    while True:
        transactions = get_transaction_history(wallet_address)
        for tx in transactions:
            print(f"Transaction: {tx}")
            if isinstance(tx, dict) and tx.get('to') == SOLANA_ADDRESS:
                buy_hero_token(wallet_address)
                wait_and_sell(wallet_address)
        time.sleep(MONITOR_INTERVAL)

# Buying Hero token
def buy_hero_token(wallet_address):
    # Pseudo code
    nonce = web3.eth.getTransactionCount(wallet_address)
    transaction = {
        'to': HERO_TOKEN_ADDRESS,
        'value': web3.toWei(1, 'ether'),  
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
        'chainId': 1  
    }
    signed_txn = web3.eth.account.signTransaction(transaction, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Buying Hero token for wallet: {wallet_address}, transaction hash: {web3.toHex(tx_hash)}")

# Waiting and selling Hero token
def wait_and_sell(wallet_address):
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        if has_bought_hero_token(wallet_address):
            sell_hero_token(wallet_address)
            return
        time.sleep(MONITOR_INTERVAL)
    sell_hero_token(wallet_address)

# Checking if user bought Hero token
def has_bought_hero_token(wallet_address):
    transactions = get_transaction_history(wallet_address)
    for tx in transactions:
        if tx['to'] == HERO_TOKEN_ADDRESS:
            return True
    return False

# Selling Hero token
def sell_hero_token(wallet_address):
    # Pseudo code
    nonce = web3.eth.getTransactionCount(wallet_address)
    transaction = {
        'to': HERO_TOKEN_ADDRESS,
        'value': web3.toWei(1, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
        'chainId': 1  
    }
    signed_txn = web3.eth.account.signTransaction(transaction, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Selling Hero token for wallet: {wallet_address}, transaction hash: {web3.toHex(tx_hash)}")

# Main function
def main():
    wallets = identify_wallets()
    for wallet in wallets:
        monitor_transactions(wallet)

if __name__ == "__main__":
    main()
