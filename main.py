import requests
from eth_wallet_tracker import EthWalletTracker
from bsc_wallet_tracker import BscWalletTracker
from telegram_handler import WalletTracker
from wax_wallet_tracker import WaxWalletTracker

telegram_bot= WalletTracker("6006972156:AAFcMD3pLyFonKeJygT3XofyqPyxTiP4OU8")
telegram_bot.run()
