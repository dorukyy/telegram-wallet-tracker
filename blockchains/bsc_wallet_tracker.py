from datetime import datetime
import requests
import yaml
from future.moves import configparser

from db_handler import DBHandler


class BSCWalletTracker:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.db = DBHandler()
        self.api_key = config.get("BSC", "token")
        with open("messages.yaml", "r") as file:
            self.messages = yaml.safe_load(file)

    def get_price(self):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data['binancecoin']['usd']
        return price

    def get_wallet_transactions(self, wallet_address):
        url = f"https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&sort=desc&apikey={self.api_key}"
        response = requests.get(url)
        data = response.json()
        transactions = data['result']
        return transactions

    def getNewTransactions(self):
        wallets = self.db.load_wallets_by_blockchain("bsc")
        new_transactions = []

        for chat_id, wallet_list in wallets.items():
            for wallet_data in wallet_list:
                wallet_address, last_check = list(wallet_data.items())[0]
                transactions = self.get_wallet_transactions(wallet_address)
                for transaction in transactions:
                    transaction_date = int(transaction['timeStamp'])

                    if transaction_date is not None and transaction_date > last_check:
                        try:
                            from_address = transaction['from']
                            to_address = transaction['to']
                            value = float(transaction['value']) / 1e18
                            transaction_type = "Unknown"

                            if wallet_address.lower() == to_address.lower():
                                transaction_type = "Incoming"
                            elif wallet_address.lower() == from_address.lower():
                                transaction_type = "Outgoing"

                            data = {
                                "type": transaction_type,
                                "chat_id": chat_id,
                                "from": from_address,
                                "to": to_address,
                                "value": value
                            }

                            message = self.bsc_message_parser(data)
                            data["message"] = message

                            new_transactions.append(data)
                            self.db.update_last_check("bsc", chat_id, wallet_address, transaction_date)
                        except KeyError:
                            print("Unexpected data type")

        return new_transactions

    def bsc_message_parser(self, message_input):
        if message_input['type'] == "Incoming":
            title = self.messages['incoming_transaction_title']
        elif message_input['type'] == "Outgoing":
            title = self.messages['outgoing_transaction_title']
        else:
            title = self.messages['unknown_transaction_title']

        message = f"{title} \n" \
                  f"From: {message_input['from']} \n" \
                  f"To: {message_input['to']} \n" \
                  f"Value: {message_input['value']} BNB \n"
        return message
