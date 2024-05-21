import numpy as np


BASE_WEIGHTS = np.array([
    0.11360032261234025, 0.09205599681693498, 0.07917854698122093, 0.07043792481418891, 0.061569604323528454, 
    0.05845218641752526, 0.0535419372435032, 0.05266639677714413, 0.055362300870950454, 0.06525550133095738,
    0.07086296027471138, 0.08585945858875539, 0.1411568629482394]
)


class VolumeEstimator:
    def __init__(self, binLen=30*60_000, startTS=9.5*60*60_000, endTS=16*60*60_000):
        self.date_list = []
        self.date = None
        self.binIndex = -1
        self.numBuckets = int(np.ceil((endTS - startTS) / binLen))
        self.day_volume = np.zeros(self.numBuckets, dtype=float)
        self.dailyBinVolumes = np.zeros((0, self.numBuckets), dtype=float)
        self.daily_weights = BASE_WEIGHTS


    def init_next_day(self, date: str):
        ''' init estimator at beginning of the day
        '''
        self.date = date
        self.date_list.append(date)
        self.day_volume = np.zeros(self.numBuckets, dtype=float)
        self.binIndex = 0
        if len(self.dailyBinVolumes) == 0:
            self.daily_weights = BASE_WEIGHTS
        else:
            self.daily_weights = self.estimate_daily_bin_weights()
        
    
    def get_bin_estimates(self, use_static=True):
        '''
            Return: bin volume weights of the day
        '''
        if use_static:
            return self.daily_weights
        
    
    def save_bin_volume(self, bin_volume):
        ''' save bin volume
        '''
        assert(self.binIndex < 13)
        self.day_volume[self.binIndex] = bin_volume
        # end of day
        if self.binIndex == 12:
            self.dailyBinVolumes = np.vstack((self.dailyBinVolumes, self.day_volume))
        self.binIndex += 1
        

    def estimate_daily_bin_weights(self):
        '''estimate all bin weights next day
        '''
        bin_volumes = self.dailyBinVolumes.mean(axis=0)
        bin_weights = bin_volumes / np.sum(bin_volumes)
        return bin_weights
        
