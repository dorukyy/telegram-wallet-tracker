import requests


class WaxWalletTracker:
    def __init__(self):
        self.token = ""

    def get_price(self):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=wax&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data['wax']['usd']
        return price

    def get_wallet_transactions(self, wallet_address):
        url = f"https://api.waxsweden.org:443/v2/history/get_actions?account={wallet_address}&limit=10"
        response = requests.get(url)
        data = response.json()
        print(data)
        transactions = data['actions']
        return transactions
