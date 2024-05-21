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
        self.volume_model = VolumeEstimator()
        self.remaining_shares = total_shares

    def load_data(self):
        trades_file = MyDirectories.getTradesDir() + f'/{self.date}/{self.stock}_trades.binRT'
        self.trades_reader = TAQTradesReader(trades_file)

    def trading_decision(self, bin_idx):
        # Get volume percentage for the current bin
        bin_weights = self.volume_model.get_bin_estimates(use_static=True)
        volume_percentage = bin_weights[bin_idx]
        
        # Calculate the number of shares to trade
        shares_to_trade = self.total_shares * volume_percentage
        return shares_to_trade

    def simulate_trading(self):
        self.volume_model.init_next_day(self.date)
        trading_decisions = []
        
        for bin_idx in range(13):
            # Get the volume for the current bin
            bin_volume = self.get_bin_volume(bin_idx)
            
            # Update volume model with the bin volume
            self.volume_model.save_bin_volume(bin_volume)
            
            # Make trading decision for the current bin
            shares_to_trade = self.trading_decision(bin_idx)
            
            # Ensure we don't trade more than the remaining shares
            shares_to_trade = min(shares_to_trade, self.remaining_shares)
            self.remaining_shares -= shares_to_trade
            
            # Record the decision
            time_str = (datetime.strptime('09:30', '%H:%M') + timedelta(minutes=30*bin_idx)).strftime('%H:%M')
            trading_decisions.append((time_str, shares_to_trade))
            
        return pd.DataFrame(trading_decisions, columns=['time', 'shares_to_trade'])


    def get_bin_volume(self, bin_idx):
        # Placeholder method to get bin volume, should be implemented to read from trades data
        # This method should calculate the total volume in the specified bin
        # For now, we return a dummy volume
        return 100000  # Dummy volume value, replace with actual calculation
