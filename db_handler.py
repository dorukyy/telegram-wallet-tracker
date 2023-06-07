import sqlite3
import time
from datetime import datetime

import requests
from future.moves import configparser


class DBHandler:
    def __init__(self):
        self.wallets_file = "wallets.db"
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.eth_api_key = config.get("ETH", "token")
        self.bsc_api_key = config.get("BSC", "token")

    def create_connection(self):
        return sqlite3.connect(self.wallets_file)

    def load_wallets(self):
        connection = self.create_connection()
        cursor = connection.cursor()

        wallets = {}

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = cursor.fetchall()

        for table_name in table_names:
            table_name = table_name[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                network = table_name
                chat_id, address, last_check = row
                if chat_id not in wallets:
                    wallets[chat_id] = {}
                if network not in wallets[chat_id]:
                    wallets[chat_id][network] = []
                wallets[chat_id][network].append(address)

        connection.close()
        return wallets

    def save_wallet(self, chat_id, network, address):
        if network == "wax":
            timestamp = self.getCurrentTimeWax()
        elif network == "eth":
            timestamp = self.getCurrentTimeETH()
        elif network == "bsc":
            timestamp = self.getCurrentTimeBSC()
        else:
            return

        with self.create_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {network} (chat_id INTEGER, address TEXT, last_check LONG)")

            cursor.execute(f"SELECT * FROM {network} WHERE chat_id = ? AND address = ?", (chat_id, address))
            existing_row = cursor.fetchone()
            if existing_row is None:
                cursor.execute(f"INSERT INTO {network} (chat_id, address, last_check) VALUES (?, ?, ?)",
                               (chat_id, address, timestamp))
                return True
            else:
                return False

    def remove_wallet(self, chat_id, network, address):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {network} WHERE chat_id = ? AND address = ?",
                       (chat_id, address))
        connection.commit()
        connection.close()

    def load_wallets_by_blockchain(self, blockchain):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {blockchain}")
        rows = cursor.fetchall()
        wallets = {}
        for row in rows:
            chat_id, address, last_check = row
            if chat_id not in wallets:
                wallets[chat_id] = []
            wallets[chat_id].append({address: last_check})
        connection.close()
        return wallets

    def update_last_check(self, blockchain, chat_id, address, new_last_check):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(f"UPDATE {blockchain} SET last_check = ? WHERE chat_id = ? AND address = ?",
                       (new_last_check, chat_id, address))
        connection.commit()
        connection.close()

    def getCurrentTimeWax(self):
        url = f"https://api.waxsweden.org:443/v1/chain/get_info"
        response = requests.post(url)
        data = response.json()
        head_block_time = data['head_block_time']
        time_stamp = self.convert_to_timestamp(head_block_time)

        return time_stamp

    def convert_to_timestamp(self, timestamp):
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        timestamp = int(dt.timestamp())
        return timestamp

    def getCurrentTimeETH(self):
        url = f"https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={self.eth_api_key}"
        response = requests.get(url)
        data = response.json()
        block_number = int(data['result'], 16)
        print(block_number)
        while True:
            timestamp = requests.get(
                f"https://api.etherscan.io/api?module=block&action=getblockreward&blockno={block_number}&apikey={self.eth_api_key}").json()
            print(timestamp)
            if timestamp['result']['timeStamp'] is None:
                time.sleep(2)
            else:
                return timestamp['result']['timeStamp']

    def getCurrentTimeBSC(self):
        url = f"https://api.bscscan.com/api?module=proxy&action=eth_blockNumber&apikey={self.bsc_api_key}"
        response = requests.get(url)
        data = response.json()
        block_number = int(data['result'], 16)
        print(block_number)
        while True:
            timestamp = requests.get(
                f"https://api.bscscan.com/api?module=block&action=getblockreward&blockno={block_number}&apikey={self.bsc_api_key}").json()
            print(timestamp)
            if timestamp['result']['timeStamp'] is None:
                time.sleep(2)
            else:
                return timestamp['result']['timeStamp']

    def resetTimestamps(self):
        connection = self.create_connection()
        cursor = connection.cursor()

        # Update last_check for eth
        timestamp_eth = self.getCurrentTimeETH()
        try:
            cursor.execute("UPDATE eth SET last_check = ?", (timestamp_eth,))
            connection.commit()
            print(f"Updated last_check for ETH: {timestamp_eth}")
        except Exception as e:
            print(f"Error updating last_check for ETH: {e}")

        # Update last_check for bsc
        timestamp_bsc = self.getCurrentTimeBSC()
        try:
            cursor.execute("UPDATE bsc SET last_check = ?", (timestamp_bsc,))
            connection.commit()
            print(f"Updated last_check for BSC: {timestamp_bsc}")
        except Exception as e:
            print(f"Error updating last_check for BSC: {e}")

        # Update last_check for wax
        timestamp_wax = self.getCurrentTimeWax()
        try:
            cursor.execute("UPDATE wax SET last_check = ?", (timestamp_wax,))
            connection.commit()
            print(f"Updated last_check for WAX: {timestamp_wax}")
        except Exception as e:
            print(f"Error updating last_check for WAX: {e}")

        connection.close()
