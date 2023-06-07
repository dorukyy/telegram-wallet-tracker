import time
import requests
import yaml
from telegram.ext import Updater, CommandHandler
import configparser

from blockchains.wax_wallet_tracker import WaxWalletTracker
from blockchains.eth_wallet_tracker import ETHWalletTracker
from blockchains.bsc_wallet_tracker import BSCWalletTracker
from db_handler import DBHandler


class WalletTracker:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.file_handler = DBHandler()
        self.wax = WaxWalletTracker()
        self.eth = ETHWalletTracker()
        self.bsc = BSCWalletTracker()

        self.bot_token = config.get('Telegram', 'token')
        self.updater = Updater(token=self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue

        self.track_eth = config.getboolean('ETH', 'eth_track')
        self.track_bsc = config.getboolean('BSC', 'bsc_track')
        self.track_wax = config.getboolean('WAX', 'wax_track')

        self.track_eth_interval = config.getint('ETH', 'eth_track_interval')
        self.track_bsc_interval = config.getint('BSC', 'bsc_track_interval')
        self.track_wax_interval = config.getint('WAX', 'wax_track_interval')

        with open("messages.yaml", "r") as file:
            self.messages = yaml.safe_load(file)

        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("add", self.add_wallet_command))
        self.dispatcher.add_handler(CommandHandler("remove", self.remove_wallet_command))
        self.dispatcher.add_handler(CommandHandler("list", self.list_wallets_command))

    def start_command(self, update, context):
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=chat_id, text=self.messages['start_message'])

    def add_wallet_command(self, update, context):
        chat_id = update.message.chat_id
        args = context.args
        if len(args) != 2:
            context.bot.send_message(chat_id=chat_id,
                                     text="Invalid command format. Usage: /add <address> <network>")
        else:
            wallet_address = args[0]
            network = args[1].lower()
            if self.file_handler.save_wallet(chat_id, network, wallet_address):
                context.bot.send_message(chat_id=chat_id, text=self.messages["wallet_added"])
            else:
                context.bot.send_message(chat_id=chat_id, text=self.messages["wallet_add_error"])

    def remove_wallet_command(self, update, context):
        chat_id = update.message.chat_id
        args = context.args
        if len(args) != 2:
            context.bot.send_message(chat_id=chat_id,
                                     text="Invalid command format. Usage: /remove <address> <network>")
        else:
            wallet_address = args[0]
            network = args[1]
            self.file_handler.remove_wallet(chat_id, network, wallet_address)
            context.bot.send_message(chat_id=chat_id, text="Wallet removed successfully.")

    def list_wallets_command(self, update, context):
        chat_id = update.message.chat_id
        wallets = self.file_handler.load_wallets()
        if chat_id in wallets:
            wallet_list = wallets[chat_id]
            message = "Your wallets:\n"
            for network, addresses in wallet_list.items():
                message += f"- Network: {network}\n"
                for address in addresses:
                    message += f"  - Address: {address}\n"
            context.bot.send_message(chat_id=chat_id, text=message)
        else:
            context.bot.send_message(chat_id=chat_id, text=self.messages['no_wallets'])


    def run(self):
        self.updater.start_polling()
        self.file_handler.resetTimestamps()
        if self.track_wax:
            self.job_queue.run_repeating(self.check_new_wax_transactions, interval=self.track_wax_interval, first=0)
        if self.track_eth:
            self.job_queue.run_repeating(self.check_new_eth_transactions, interval=self.track_eth_interval, first=0)
        if self.track_bsc:
            self.job_queue.run_repeating(self.check_new_bsc_transactions, interval=self.track_bsc_interval, first=0)
        self.updater.idle()

    def check_new_wax_transactions(self, context):
        new_wax_transactions = self.wax.getNewTransactions()
        for transaction in new_wax_transactions:
            self.send_notification(transaction['message'], transaction['chat_id'])

    def check_new_eth_transactions(self, context):
        new_eth_transactions = self.eth.getNewTransactions()
        for transaction in new_eth_transactions:
            self.send_notification(transaction['message'], transaction['chat_id'])

    def check_new_bsc_transactions(self, context):
        new_bsc_transactions = self.bsc.getNewTransactions()
        for transaction in new_bsc_transactions:
            self.send_notification(transaction['message'], transaction['chat_id'])

    def send_notification(self, message, chat_id):
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        payload = {'chat_id': f'{chat_id}',
                   'text': f'{message}',
                   'parse_mode': 'HTML',
                   'disable_web_page_preview': True}
        response = requests.post(url, data=payload)
        print("Notification sent!")


