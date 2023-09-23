# Telegram Crypto Wallet Tracker


The Telegram Crypto Wallet Tracker is a Python application that allows users to track cryptocurrency wallets for various blockchains and sends notifications on Telegram when a transaction is made.

The application provides a convenient way for users to add, remove, and list their cryptocurrency wallets. It supports popular blockchains such as WAX, BSC (Binance Smart Chain), and ETH (Ethereum).

When a new transaction occurs in any of the tracked wallets, the application sends a notification message to the user's Telegram chat, providing details about the transaction.

This wallet tracking solution is designed to keep users informed about their cryptocurrency transactions and provide a seamless experience for managing multiple wallets across different blockchains.



<img src="https://img.shields.io/github/last-commit/dorukyy/telegram-wallet-tracker">



### Supported Block-chains
- ETH
- BSC
- WAX

You can contact me via:

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/dorukyd)

## Support

If you like the project you can support me with the link below

<a href="https://www.buymeacoffee.com/dorkyy" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-yellow.png" alt="Buy Me A Coffee" height="41" width="174"></a>


## Prerequisites

- Python 3.7 or higher
- `pip` package manager

## Installation

1. Clone the repository:

```shell
git clone https://github.com/your-username/wallet-tracker.git
```


2. Install the required dependencies:

```shell
pip install -r requirements.txt
```

3. Edit the config.ini file to configure the Telegram token and blockchain settings:

```
[Telegram]
token = <your-telegram-bot-token>

[WAX]
wax_track = False
wax_track_interval = 60

[BSC]
token = <your-bsc-token>
bsc_track = True
bsc_track_interval = 60

[ETH]
token = <your-eth-token>
eth_track = False
eth_track_interval = 60
```

4. Run the application:
```
python main.py
```
## Usage

1. Start the bot by sending the /start command.

2. Add a wallet by sending the /add <address> <network> command. For example:


```
/add 0x123456789abcdefg eth
```
This will add an Ethereum wallet with the given address.

3.Remove a wallet by sending the /remove <address> <network> command. For example:

```
/remove 0x123456789abcdefg eth
```
This will remove the Ethereum wallet with the given address.

4. List all your wallets by sending the /list command.


## Contributions
Contributions are welcome! If you find any issues or have suggestions, please create a new issue or submit a pull request.
