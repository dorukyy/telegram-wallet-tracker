import requests


class BscWalletTracker:
    def __init__(self, token):
        self.token = token

    def get_price(self):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data['binancecoin']['usd']
        return price

    def get_wallet_transactions(self, wallet_address):
        url = f"https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&apikey={self.token}"
        response = requests.get(url)
        data = response.json()
        transactions = data['result']
        return transactions
