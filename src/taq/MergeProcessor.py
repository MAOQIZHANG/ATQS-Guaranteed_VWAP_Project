import gzip
import os
import struct
from collections import deque
from taq.BinReader import BinReader
from taq.BinReaderManager import BinReaderManager
from taq.MyDirectories import MyDirectories


class MergeProcessor:
    def __init__(self, outFilePathName, writeFormat):
        self._out = gzip.open(outFilePathName, "wb")
        self._encoder = struct.Struct(writeFormat)
    # This method gets called when some number of readers
    # at the beginning of the list, 'binReaders' have new
    # records. That number is in 'nActive'.
    def process(self, binReaders, nActive):
        for iActive in range(nActive):
            for rec in binReaders[iActive].getRecs():
                self._out.write(self._encoder.pack(*rec))
    def isFinished(self):
        return False
    def close(self):
        self._out.close()
    @classmethod
    def MergeFiles(cls, filenames, fmt):
        generationCounter = 0
        newFileNames = deque()
        filenames = deque(filenames)
        while True:
            fileCounter = 0
            while len(filenames) > 1:
                # Instantiate two readers.
                readers = deque([
                    BinReader(filenames.popleft(), fmt, 10000),
                    BinReader(filenames.popleft(), fmt, 10000)
                ])
                # If there's only one more left, this is the final
                # read, so we'll read three at a time instead of two.
                if len(readers) == 1:
                    readers.append(BinReader(filenames.popleft(), fmt, 10000))
                # Instantiate the merge processor.
                newFileNames.append(MyDirectories.TempDir + "/bin_%d_%d.gz" % (generationCounter, fileCounter ))
                processors = deque([MergeProcessor(newFileNames[-1], fmt)])
                # Hand the list of readers and processors to
                # BinReaderManager and tell it to run.
                BinReaderManager(readers, processors).run()
                # After the second merge, there will be files to
                # delete from the previous merge.
                if generationCounter > 0:
                    for reader in readers:
                        os.remove(reader.getFilePathName())
                # I don't love this: I have to manually close the
                # processors. Maybe a better design is to have
                # the BinReaderManager close them.
                for processor in processors:
                    processor.close()
                fileCounter += 1
            # If, in the current generation, we wrote only
            # one file, we have fully merged the data set.
            if fileCounter == 1:
                # We are finished merging, so exit.
                break
            # We are not finished merging.
            filenames = deque(newFileNames)
            generationCounter += 1
