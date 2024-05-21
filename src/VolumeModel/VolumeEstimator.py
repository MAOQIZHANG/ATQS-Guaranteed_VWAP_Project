import numpy as np
from pandas import isna
import scipy.optimize as opt


BASE_WEIGHTS = np.array([0.13, 0.08, 0.08, 0.07, 0.06, 0.05, 0.05, 0.05, 0.06, 0.07, 0.08, 0.08, 0.14])


class VolumeEstimator:
    def __init__(self, binLen=30*60_000, startTS=9.5*60*60_000, endTS=16*60*60_000):
        self.date_list = []
        self.date = None
        self.binIndex = -1
        self.numBuckets = int(np.ceil((endTS - startTS) / binLen))
        self.day_volume = np.zeros(self.numBuckets, dtype=float)
        self.dailyBinVolumes = np.zeros((0, self.numBuckets), dtype=float)
        self.daily_weights = BASE_WEIGHTS
        self.daily_total_volumes = []


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
        self.traded_weights = np.zeros_like(self.daily_weights)
        self.total_volume_pred = self.estimate_daily_total_volume()
        
    
    def get_trading_rate(self, use_static=True):
        '''
            trading model.
        '''
        if use_static or len(self.dailyBinVolumes) == 0:
            self.traded_weights = self.daily_weights
        else:
            if self.binIndex == 0:
                self.traded_weights[0] = self.daily_weights[0]
            else:
                volumes_traded = np.sum(self.day_volume)
                traded = volumes_traded / self.total_volume_pred
                traded_pred = np.sum(self.daily_weights[: self.binIndex])
                delta = traded - traded_pred
                # adjust trading rate
                next_weight = self.trading_model(delta)
                # record trade
                self.traded_weights[self.binIndex] = next_weight

        return self.traded_weights


    def trading_model(self, delta):
        # next trading rate according to original schedule
        pctg_traded = np.sum(self.traded_weights)
        pctg_remain = 1.0 - pctg_traded
        weights_to_trade = self.daily_weights[self.binIndex: ]
        weights_to_trade = weights_to_trade / np.sum(weights_to_trade) * pctg_remain
        w_next = weights_to_trade[0]
        if self.binIndex == 12:
            return w_next
        # adjust trading rate
        factor = np.arctanh(-delta) + 1
        if np.isnan(factor):
            factor = 1.0
        factor = np.clip(factor, 0.9, 1.1)
        w_next *= factor
        return w_next
    
    
    def save_bin_volume(self, bin_volume):
        ''' save bin volume
        '''
        assert(self.binIndex < 13)
        self.day_volume[self.binIndex] = bin_volume
        # end of day
        if self.binIndex == 12:
            self.dailyBinVolumes = np.vstack((self.dailyBinVolumes, self.day_volume))
            self.daily_total_volumes.append(np.sum(self.day_volume))
        self.binIndex += 1
        

    def estimate_daily_bin_weights(self):
        '''estimate all bin weights next day
        '''
        bin_volumes = self.dailyBinVolumes.mean(axis=0)
        bin_weights = bin_volumes / np.sum(bin_volumes)
        return bin_weights
    

    def estimate_daily_total_volume(self):
        if len(self.dailyBinVolumes) == 0:
            return -1
        res = opt.minimize(
            self.MSE_loss,
            x0 = 0.5, 
            args = np.array(self.daily_total_volumes),
            bounds = ((0.0, 1.0),),
            options = {"maxiter": 100, "disp": False}
        )
        k = res.x
        V = self.EWMA(np.array(self.daily_total_volumes), k)
        return V[-1]
    
    def EWMA(self, volumes, k):
        V = np.zeros_like(volumes, dtype=float)
        V[0] = volumes[0]
        for i in range(1, len(volumes)):
            V[i] = k * V[i-1] + (1 - k) * volumes[i-1]
        return V
    
    def MSE_loss(self, k, volumes):
        V = self.EWMA(volumes, k)
        return np.linalg.norm(V - volumes)
