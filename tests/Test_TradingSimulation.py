import unittest
import sys
src_path = 'src'

# Add the src folder to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from taq import MyDirectories
from taq.TAQTradesReader import TAQTradesReader
from VolumeModel.VolumeEstimator import VolumeEstimator
from VolumeModel.BinVolume import BinVolume
from TradingModel.TradingSimulation import TradingSimulation

class Test_TradingSimulation(unittest.TestCase):

    def setUp(self):
        # Setup for the test, with a sample stock and date
        self.stock = 'IBM'
        self.date = '20070920'
        self.total_shares = 400000
        self.simulation = TradingSimulation(self.stock, self.date, self.total_shares)
        self.simulation.load_data()

    def test_trading_decisions(self):
        # Run the simulation
        results = self.simulation.simulate_trading()
        
        # Check if the results DataFrame is not empty
        self.assertFalse(results.empty, "The trading simulation results should not be empty.")
        
        # Check if the results have the correct columns
        self.assertListEqual(list(results.columns), ['time', 'shares_to_trade'], "The results should have 'time' and 'shares_to_trade' columns.")
        
        # Check if the total shares to trade matches the expected total shares
        total_traded_shares = results['shares_to_trade'].sum()
        self.assertAlmostEqual(total_traded_shares, self.total_shares, delta=1, msg="The total traded shares should approximately match the parent order size.")

if __name__ == "__main__":
    unittest.main()