import requests


class EthWalletTracker:
    def __init__(self, token):
        self.token = token

    def get_price(self):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data['ethereum']['usd']
        return price

    def get_wallet_transactions(self, wallet_address):
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&apikey={self.token}"
        response = requests.get(url)
        data = response.json()
        transactions = data['result']
        return transactions
