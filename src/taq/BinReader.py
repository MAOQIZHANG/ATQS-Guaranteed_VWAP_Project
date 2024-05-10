import gzip
import struct
from collections import deque


class BinReader(object):
    def __init__(self, filePathName, conversionFmt, bufSizeInRecs):
        self._last = None
        self._recConv = struct.Struct(conversionFmt)
        # Calculate record size from conversion format
        self._recSize = struct.calcsize(conversionFmt)
        # Allocate buffer using rec size and number of
        # recs specified in constructor argument.
        self._buff = bytearray(bufSizeInRecs * self._recSize)
        # Set the buffer offset to 0. We will be
        # reading into the beginning of the buffer.
        self._bufOffst = 0
        # Save the file path name for testing.
        self._filePathName = filePathName
        # Open the gzipped data file we'll be reading.
        self._in = gzip.open(self._filePathName, "rb")
        # Create a converter for sequence numbers.
        # Our sequence number is always a long integer
        self._snConv = struct.Struct(">Q")
        # Create a deque for storing records that have
        # been read.
        self._recs = deque()
        # Read a full buffer of data, possibly millions
        # of bytes.
        self._readFullBuff()

    def getSN(self):
        return self._snConv.unpack_from(self._buff, self._bufOffst)[0]
    
    def readThrough(self, sn):
        # V2 - Implement ALL, LAST, or applyFunc functionality to reduce object creation
        self._last = sn
        self._recs.clear()
        while self.getSN() <= sn:
            self._recs.append(self.next())
            if not self.hasNext():
                break
        return self._recs
    
    # Read data into our buffer
    def _readFullBuff(self):
        self._nBytesRead = self._in.readinto(self._buff)
        self._bufOffst = 0
        if self._nBytesRead < len(self._buff):
            self.close()

    def hasNext(self):
        return self._bufOffst < self._nBytesRead
    
    # Process next record in our buffer or, if at end of buffer, read more data into buffer
    def next(self):
        rec = self._recConv.unpack_from(self._buff, self._bufOffst)
        self._bufOffst = self._bufOffst + self._recSize
        if self._bufOffst == self._nBytesRead:
            if self._nBytesRead == len(self._buff):
                self._readFullBuff()
        return rec
    
    def close(self):
        if self._in is not None:
            self._in.close()
            self._in = None

    # Get a deque of all records read
    def getRecs(self):
        return self._recs
    
    # Return true if this reader has read through sn
    def hasRecs(self, sn):
        return self._last <= sn
    
    # Write all recs to a specified binary file
    def writeTo(self, outFile):
        for rec in self._recs:
            outFile.write(self._recConv.pack(*rec))

    def getFilePathName(self):
        return self._filePathName
