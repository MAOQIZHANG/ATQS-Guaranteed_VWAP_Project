import numpy as np
from taq.TAQTradesReader import TAQTradesReader


# compute bin trading volume for each trades reader
class BinVolume:
    def __init__(
            self, 
            data: TAQTradesReader, 
            binLen = 30 * 60 * 1000,
            startTS = 9.5 * 60 * 60 * 1000,  # 9:30AM
            endTS = 16 * 60 * 60 * 1000  # 4PM
        ):
        numBuckets = int(np.ceil((endTS - startTS) / binLen))
        self.volumes = np.array([0.0] * numBuckets, dtype=np.longlong)
        iBucket = -1
        for i in range(data.getN()):
            ts = data.getMillisFromMidn(i)
            if ts >= endTS:
                break
            if ts < startTS:
                continue
            iBucket = int(np.floor((ts - startTS) / binLen))
            self.volumes[iBucket] += data.getSize(i)
    
    def getVolumes(self):
        return self.volumes
    
    def getN(self):
        return len(self.volumes)


if __name__ == "__main__":
    from taq import MyDirectories
    import matplotlib.pyplot as plt

    data = TAQTradesReader(MyDirectories.getTradesDir() + "/20070620/IBM_trades.binRT")
    binVolume = BinVolume(data, binLen=30 * 60_000)

    print(binVolume.getN())
    volume = binVolume.getVolumes()
    plt.plot(volume)
    plt.show()
