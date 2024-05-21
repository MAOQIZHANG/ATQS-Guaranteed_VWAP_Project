import unittest
import os
import numpy as np
import sys

src_path = 'src'

# Add the src folder to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from taq import MyDirectories
from taq.TAQTradesReader import TAQTradesReader
from VolumeModel.VolumeEstimator import VolumeEstimator
from VolumeModel.BinVolume import BinVolume


class Test_TAQQuotesReader(unittest.TestCase):

    def test1(self):
        # get test dates and stocks
        date_list = sorted(list(os.listdir(MyDirectories.getTradesDir())))
        date_list = date_list[:15]
        with open(os.path.join(MyDirectories.getDataDir(), 'SP500_filtered.txt'), 'r') as f:
            stock_list = [line.strip() for line in f.readlines()]

        # volume model
        VolumeModel = VolumeEstimator()

        for i, date in enumerate(date_list):
            print(date)

            # get bin volumes on date (ignore) (implemented in simulation part)
            volume = np.zeros(13, dtype=np.longlong)
            for stock in stock_list:
                file_path = os.path.join(MyDirectories.getTradesDir(), date, stock + '_trades.binRT')
                trades = TAQTradesReader(file_path)
                binVolumes = BinVolume(trades)
                volume += binVolumes.getVolumes()
            
            # init volume model at the start of each day
            VolumeModel.init_next_day(date)

            # print(np.sum(volume), VolumeModel.total_volume_pred)
            print(VolumeModel.daily_weights)

            # Iterate over each bin in a day
            for binIdx in range(13):
                # get next bin weights estimate (all 13 bins)
                bin_weights = VolumeModel.get_trading_rate(use_static=False)
                # if binIdx == 0:
                #     print(bin_weights)

                # save current bin volume (computation of `volume` should be implemented in simulation)
                VolumeModel.save_bin_volume(volume[binIdx])

            print(VolumeModel.traded_weights)


if __name__ == "__main__":
    unittest.main()

