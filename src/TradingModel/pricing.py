import numpy as np


def ExecutionCost(h: np.array, bin_shares: np.array, bin_prices: np.array, vwap):
    ''' Execution cost of the order.
            h: temporary impacts
            shares: Num. of shares traded in each bin
            prices: price per share in each bin
            vwap: vwap of the stock in the day
    '''
    cost = np.abs(vwap * np.sum(bin_shares) - bin_prices * bin_shares)
    impacts = h * bin_shares
    E = cost + impacts
    return E

