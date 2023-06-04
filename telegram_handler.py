import json
import threading
import time
from telegram.ext import Updater, CommandHandler

class WalletTracker:
    def __init__(self, bot_token):
        self.wallets_file = "wallets.json"
        self.bot_token = bot_token
        self.updater = Updater(token=bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler("addwallet", self.add_wallet_command))
        self.dispatcher.add_handler(CommandHandler("removewallet", self.remove_wallet_command))
        self.dispatcher.add_handler(CommandHandler("listwallets", self.list_wallets_command))

    def load_wallets(self):
        try:
            with open(self.wallets_file, "r") as file:
                wallets = json.load(file)
        except FileNotFoundError:
            wallets = {}
        return wallets if isinstance(wallets, dict) else {}

    def save_wallets(self, wallets):
        with open(self.wallets_file, "w") as file:
            json.dump(wallets, file)

    def add_wallet_command(self, update, context):
        chat_id = update.message.chat_id
        args = context.args
        if len(args) != 2:
            context.bot.send_message(chat_id=chat_id, text="Invalid command format. Usage: /addwallet <address> <network>")
        else:
            wallet_address = args[0]
            network = args[1]
            self.add_wallet(chat_id, wallet_address, network)
            context.bot.send_message(chat_id=chat_id, text="Wallet added successfully.")

    def remove_wallet_command(self, update, context):
        chat_id = update.message.chat_id
        args = context.args
        if len(args) != 2:
            context.bot.send_message(chat_id=chat_id, text="Invalid command format. Usage: /removewallet <address> <network>")
        else:
            wallet_address = args[0]
            network = args[1]
            self.remove_wallet(chat_id, wallet_address, network)
            context.bot.send_message(chat_id=chat_id, text="Wallet removed successfully.")

    def list_wallets_command(self, update, context):
        chat_id = update.message.chat_id
        wallets = self.load_wallets()
        if chat_id in wallets:
            wallet_list = wallets[chat_id]
            message = "Your wallets:\n"
            for network, addresses in wallet_list.items():
                message += f"- Network: {network}\n"
                for address in addresses:
                    message += f"  - Address: {address}\n"
            context.bot.send_message(chat_id=chat_id, text=message)
        else:
            context.bot.send_message(chat_id=chat_id, text="You have no wallets.")

    def add_wallet(self, chat_id, wallet_address, network):
        wallets = self.load_wallets()

        if str(chat_id) not in wallets:
            wallets[str(chat_id)] = {}

        if network not in wallets[str(chat_id)]:
            wallets[str(chat_id)][network] = []

        if wallet_address not in wallets[str(chat_id)][network]:
            wallets[str(chat_id)][network].append(wallet_address)
            self.save_wallets(wallets)
            print("Cüzdan başarıyla eklendi.")
        else:
            print("Bu cüzdan zaten kaydedilmiş.")

    def remove_wallet(self, chat_id, wallet_address, network):
        wallets = self.load_wallets()

        if chat_id in wallets and network in wallets[chat_id]:
            wallets[chat_id][network].remove(wallet_address)

            if len(wallets[chat_id][network]) == 0:
                del wallets[chat_id][network]

            if len(wallets[chat_id]) == 0:
                del wallets[chat_id]

            self.save_wallets(wallets)

    def check_wallets(self):
        wallets = self.load_wallets()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        for chat_id, wallet_list in wallets.items():
            for network, addresses in wallet_list.items():
                print("sa")

    def run(self):
        threading.Thread(target=self.check_wallets).start()
        self.updater.start_polling()
        self.updater.idle()
