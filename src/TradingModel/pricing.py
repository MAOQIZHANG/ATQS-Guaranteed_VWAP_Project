import numpy as np


def cal_premium(h: np.array, bin_shares: np.array, lambda_ = 10e-6):
    ''' Execution cost of the order.
            h: temporary impacts
            shares: Num. of shares traded in each bin
            lambda_: risk aversion parameter
    '''
    P = np.sum(h * bin_shares / 2) + lambda_ * np.var(h)

    return P

