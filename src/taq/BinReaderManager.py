from collections import deque

class BinReaderManager:
    def __init__(self, binReaders: deque, processors: deque):
        self._binReaders = deque(binReaders)
        self._processors = deque(processors)
    def run(self):
        while len(self._binReaders) > 0 and len(self._processors) > 0:
            # Initialize number of readers with records
            # read in last iteration to zero.
            nReadersActive = 0
            # Each of the readers knows its sequence number
            # which is just the timestamp of the first
            # record each already read and is keeping in
            # its buffer. Sort the list of readers by that
            # timestamp so that the beginning of the list
            # is a reader with the lowest timestamp.
            self._binReaders = deque(
                sorted(
                    self._binReaders,
                    key = lambda oneReader: oneReader.getSN()
                )
            )

            # Use the lowest sequence number as the next
            # target sequence number.
            targetSN = self._binReaders[0].getSN()
            # Ask each reader that has the target sequence
            # number or lower to read until it has either
            # read a record with a higher sequence number
            # or has run out of data.
            for aBinReader in self._binReaders:
                # If we encounter a reader that doesn't have
                # even one record that has a sequence number
                # less than or equal to the target sequence
                # number, end this reading cycle.
                if aBinReader.getSN() > targetSN:
                    break
                # Read all the records that have the target
                # sequence number or lower. They will be
                # stored inside the reader and are accessed
                # via a getter.
                aBinReader.readThrough( targetSN )
                # Increment the counter we are using to
                # track how many readers have new records.
                nReadersActive += 1
            # Pass entire list of readers to each of the
            # processors and tell each processor how many
            # of the readers in the list have new records.
            # For example, if there are 3 readers and the
            # number active is 2, it means that the first
            # 2 have new records.
            for _ in range(len(self._processors)):
                processor = self._processors.popleft()
                processor.process(self._binReaders, nReadersActive)
                # If the processor is not finished, return it
                # to the deque of active processors.
                if not processor.isFinished():
                    self._processors.append(processor)
            # Remove dead readers
            for _ in range(nReadersActive):
                binReader = self._binReaders.popleft()
                if binReader.hasNext():
                    self._binReaders.append(binReader)

