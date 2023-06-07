from datetime import datetime
import requests
import yaml

from db_handler import DBHandler


class WaxWalletTracker:
    def __init__(self):
        self.db = DBHandler()
        with open("messages.yaml", "r") as file:
            self.messages = yaml.safe_load(file)

    def getCurrentTime(self):
        url = f"https://api.waxsweden.org:443/v1/chain/get_info"
        response = requests.post(url)
        data = response.json()
        head_block_time = data['head_block_time']
        time_stamp = self.convert_to_timestamp(head_block_time)

        return time_stamp

    def get_price(self):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=wax&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data['wax']['usd']
        return price

    def get_wallet_transactions(self, wallet_address):
        url = f"https://wax.greymass.com/v1/history/get_actions?account_name={wallet_address}&limit=100"
        response = requests.get(url)
        data = response.json()
        transactions = data['actions']
        return transactions

    def convert_to_timestamp(self, timestamp):
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        timestamp = int(dt.timestamp())
        return timestamp

    def getNewTransactions(self):
        wallets = self.db.load_wallets_by_blockchain("wax")
        new_transactions = []

        for chat_id, wallet_list in wallets.items():
            for wallet_data in wallet_list:
                wallet_address, last_check = list(wallet_data.items())[0]
                transactions = self.get_wallet_transactions(wallet_address)

                for transaction in reversed(transactions):
                    transaction_date = self.convert_to_timestamp(transaction['block_time'])

                    if transaction_date is not None and transaction_date > last_check:
                        try:
                            transaction_data = transaction['action_trace']['act']['data']
                            from_address = transaction_data['from']
                            to_address = transaction_data['to']
                            quantity = transaction_data['quantity']
                            transaction_type = "Unknown"

                            if wallet_address == to_address:
                                transaction_type = "Incoming"
                            elif wallet_address == from_address:
                                transaction_type = "Outgoing"

                            data = {
                                "type": transaction_type,
                                "chat_id": chat_id,
                                "from": from_address,
                                "to": to_address,
                                "quantity": quantity
                            }

                            message = self.wax_message_parser(data)
                            data["message"] = message

                            new_transactions.append(data)
                            self.db.update_last_check("wax", chat_id, wallet_address, transaction_date)
                        except KeyError:
                            print("Unexpected data type")

        return new_transactions

    def wax_message_parser(self, message_input):
        if message_input['type'] == "Incoming":
            title = self.messages['incoming_transaction_title']
        elif message_input['type'] == "Outgoing":
            title = self.messages['outgoing_transaction_title']
        else:
            title = self.messages['unknown_transaction_title']

        message = f"{title} \n" \
                  f"From: {message_input['from']} \n" \
                  f"To: {message_input['to']} \n" \
                  f"Quantity: {message_input['quantity']} \n"
        return message
