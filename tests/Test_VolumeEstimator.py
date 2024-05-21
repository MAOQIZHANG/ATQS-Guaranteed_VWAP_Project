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
        date_list = date_list[:3]
        with open(os.path.join(MyDirectories.getDataDir(), 'SP500_filtered.txt'), 'r') as f:
            stock_list = [line.strip() for line in f.readlines()]

        # volume model
        VolumeModel = VolumeEstimator()

        for i, date in enumerate(date_list):
            # get bin volumes on date (ignore) (implemented in simulation part)
            volume = np.zeros(13, dtype=np.longlong)
            for stock in stock_list:
                file_path = os.path.join(MyDirectories.getTradesDir(), date, stock + '_trades.binRT')
                trades = TAQTradesReader(file_path)
                binVolumes = BinVolume(trades)
                volume += binVolumes.getVolumes()
            
            # init volume model at the start of each day
            VolumeModel.init_next_day(date)

            # Iterate over each bin in a day
            for binIdx in range(13):
                # get next bin weights estimate (all 13 bins)
                bin_weights = VolumeModel.get_bin_estimates(use_static=True)

                # save current bin volume (computation of `volume` should be implemented in simulation)
                VolumeModel.save_bin_volume(volume[binIdx])


if __name__ == "__main__":
    unittest.main()

