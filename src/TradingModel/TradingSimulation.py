import os
import numpy as np
import pandas as pd
import sys

src_path = 'src'

# Add the src folder to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from taq import MyDirectories
from taq.TAQTradesReader import TAQTradesReader
from taq.TAQQuotesReader import TAQQuotesReader
from VolumeModel.VolumeEstimator import VolumeEstimator
from datetime import datetime, timedelta

class TradingSimulation:
    def __init__(self, stock, date, total_shares):
        self.stock = stock
        self.date = date
        self.total_shares = total_shares
        self.volume_model = { # to be changed
            '09:30-10:00': 0.17,
            '10:00-10:30': 0.12,
            '10:30-11:00': 0.10,
            '11:00-11:30': 0.08,
            '11:30-12:00': 0.07,
            '12:00-12:30': 0.06,
            '12:30-13:00': 0.06,
            '13:00-13:30': 0.07,
            '13:30-14:00': 0.08,
            '14:00-14:30': 0.09,
            '14:30-15:00': 0.10,
            '15:00-15:30': 0.13,
            '15:30-16:00': 0.17
        }

    def load_data(self):
        trades_file = MyDirectories.getTradesDir() + f'/{self.date}/{self.stock}_trades.binRT'
        quotes_file = MyDirectories.getQuotesDir() + f'/{self.date}/{self.stock}_quotes.binRQ'
        self.trades_reader = TAQTradesReader(trades_file)
        self.quotes_reader = TAQQuotesReader(quotes_file)

    def get_volume_percentage(self, time):
        time_str = time.strftime('%H:%M')
        for interval in self.volume_model:
            start, end = interval.split('-')
            if start <= time_str < end:
                return self.volume_model[interval]
        return 0

    def trading_decision(self, current_time):
        volume_percentage = self.get_volume_percentage(current_time)
        shares_to_trade = self.total_shares * volume_percentage
        return shares_to_trade

    def simulate_trading(self):
        start_time = datetime.strptime('09:30', '%H:%M')
        end_time = datetime.strptime('16:00', '%H:%M')
        current_time = start_time
        half_hour = timedelta(minutes=30)
        
        trading_decisions = []

        while current_time < end_time:
            shares_to_trade = self.trading_decision(current_time)
            trading_decisions.append((current_time.strftime('%H:%M'), shares_to_trade))
            current_time += half_hour
        
        return pd.DataFrame(trading_decisions, columns=['time', 'shares_to_trade'])
