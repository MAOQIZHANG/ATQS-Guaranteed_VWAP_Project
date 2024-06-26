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
from impact_model import ImpactModel
from datetime import datetime, timedelta

class TradingSimulation:
    def __init__(self, stock, date, total_shares):
        self.stock = stock
        self.date = date
        self.total_shares = total_shares
        self.volume_model = VolumeEstimator()
        self.remaining_shares = total_shares
        self.impact_model = ImpactModel('Impact-Model-Matrix')

    def load_data(self):
        trades_file = MyDirectories.getTradesDir() + f'/{self.date}/{self.stock}_trades.binRT'
        self.trades_reader = TAQTradesReader(trades_file)

    def trading_decision(self, bin_idx):
        bin_weights = self.volume_model.get_trading_rate(use_static=False)
        volume_percentage = bin_weights[bin_idx]
        shares_to_trade = self.total_shares * volume_percentage
        return shares_to_trade

    def simulate_trading(self):
        self.volume_model.init_next_day(self.date)
        trading_decisions = []
        
        for bin_idx in range(13):
            bin_volume = self.get_bin_volume(bin_idx)
            self.volume_model.save_bin_volume(bin_volume)
            shares_to_trade = self.trading_decision(bin_idx)
            shares_to_trade = min(shares_to_trade, self.remaining_shares)
            self.remaining_shares -= shares_to_trade
            time_str = (datetime.strptime('09:30', '%H:%M') + timedelta(minutes=30*bin_idx)).strftime('%H:%M')
            trading_decisions.append((time_str, shares_to_trade))
            
        return pd.DataFrame(trading_decisions, columns=['time', 'shares_to_trade'])

    def get_bin_volume(self, bin_idx):
        # Calculate the total volume in the specified bin
        start_time = 9.5 * 60 * 60 * 1000 + bin_idx * 30 * 60 * 1000
        end_time = start_time + 30 * 60 * 1000
        volume = 0
        for i in range(self.trades_reader.getN()):
            ts = self.trades_reader.getMillisFromMidn(i)
            if start_time <= ts < end_time:
                volume += self.trades_reader.getSize(i)
        return volume
    
    def cal_temp_impact(self):
        self.impact_model.read_data()
        self.h = np.zeros(13)
        for bin_idx in range(1, 13):
            X = self.volume_model.day_volume[bin_idx - 1]
            date_list = sorted(list(os.listdir(MyDirectories.getTradesDir())))
            date_idx = date_list.index(self.date)
            self.h[bin_idx] = self.impact_model.cal_temp_impact(self.stock, date_idx, X)
    
    def get_premium(self, lambda_ = 10e-6):
        ''' Execution cost of the order.
                h: temporary impacts
                shares: Num. of shares traded in each bin
                lambda_: risk aversion parameter
        '''
        bin_shares = np.zeros(13)
        for bin_idx in range(13):
            bin_shares[bin_idx] = self.trading_decision(bin_idx)

        P = np.sum(self.h * bin_shares / 2) + lambda_ * np.var(self.h)

        return P

