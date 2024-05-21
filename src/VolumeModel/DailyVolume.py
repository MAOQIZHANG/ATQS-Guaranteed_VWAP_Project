import os
import numpy as np
import pandas as pd
from tqdm import tqdm

from taq import MyDirectories
from taq.TAQTradesReader import TAQTradesReader
from VolumeModel.BinVolume import BinVolume


BIN_WEIGHTS = [0.11360032261234025, 0.09205599681693498, 0.07917854698122093, 0.07043792481418891, 0.061569604323528454, 
               0.05845218641752526, 0.0535419372435032, 0.05266639677714413, 0.055362300870950454, 0.06525550133095738,
               0.07086296027471138, 0.08585945858875539, 0.1411568629482394]


class DailyBinVolume:
    def __init__(self, binLen=30*60_000, startTS=9.5*60*60_000, endTS=16*60*60_000):
        self.binLen = binLen
        self.startTS = startTS
        self.endTS = endTS
        self.numBuckets = int(np.ceil((endTS - startTS) / binLen))
        self.totalVolume = np.zeros(self.numBuckets, dtype=float)
        self.dailyVolumes = {}
        self.EWMAVolumes = {}
        self.date_list = sorted(list(os.listdir(MyDirectories.getTradesDir())))
        # assert(len(self.date_list) == 65)
        with open(os.path.join(MyDirectories.getDataDir(), 'SP500_filtered.txt'), 'r') as f:
            self.stock_list = [line.strip() for line in f.readlines()]
        # assert(len(self.stock_list) == 502)
    
    def getDateVolume(self, date):
        volume = np.zeros(self.numBuckets, dtype=np.longlong)
        for stock in self.stock_list:
            file_path = os.path.join(MyDirectories.getTradesDir(), date, stock + '_trades.binRT')
            trades = TAQTradesReader(file_path)
            binVolumes = BinVolume(trades, self.binLen, self.startTS, self.endTS)
            volume += binVolumes.getVolumes()
        return volume
    
    def getDailyBinVolumes(self, date_list=None, EWMA=None, save=False):
        # compute bin volumes in date_list
        if date_list is None:
            date_list = self.date_list
        date_list = sorted(date_list)
        if save:
            df = pd.DataFrame(np.zeros((self.numBuckets, len(date_list))), columns=date_list)
        for i, date in enumerate(tqdm(date_list)):
            if date not in self.dailyVolumes.keys():
                self.dailyVolumes[date] = self.getDateVolume(date)
            self.totalVolume += self.dailyVolumes[date]
            if EWMA is not None:
                if i == 0:
                    self.EWMAVolumes[date] = self.dailyVolumes[date]
                else:
                    self.EWMAVolumes[date] = (1 - EWMA) * self.dailyVolumes[date] + EWMA * self.EWMAVolumes[date_list[i-1]]
            if save:
                df[date] = self.dailyVolumes[date]
        # save
        if save:
            df.to_csv(os.path.join(MyDirectories.getOutputDir(), 'daily_total_volumes.csv'), index=False)
        
                
    def getTotalVolumes(self):
        return self.totalVolume
    
    def getVolumeWeigths(self):
        return self.totalVolume / np.sum(self.totalVolume)
    
    def getDates(self):
        return self.date_list



if __name__ == "__main__":
    dv = DailyBinVolume()
    dv.getDailyBinVolumes(save=True)

    import matplotlib.pyplot as plt

    plt.plot(dv.getVolumeWeigths())
    plt.grid()
    plt.show()

