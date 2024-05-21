import unittest
import sys

src_path = 'src'

# Add the src folder to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from taq import MyDirectories
from taq.TAQQuotesReader import TAQQuotesReader


class Test_TAQQuotesReader(unittest.TestCase):

    def test1(self):

        reader = TAQQuotesReader(MyDirectories.getQuotesDir() + '/20070920/IBM_quotes.binRQ' )
        
        zz = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getAskSize( 0 ),
            reader.getAskPrice( 0 ),
            reader.getBidSize( 0 ),
            reader.getBidPrice( 0 )
        ])
        self.assertEqual( '[70166, 1190260800, 34210000, 1, 116.19999694824219, 38, 116.19999694824219]', str( zz ) )


if __name__ == "__main__":
    unittest.main()
