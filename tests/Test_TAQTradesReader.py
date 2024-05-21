import unittest
import sys

src_path = 'src'

# Add the src folder to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from taq import MyDirectories
from taq.TAQTradesReader import TAQTradesReader

class Test_TAQTradesReader(unittest.TestCase):

    def test1(self):

        reader = TAQTradesReader( MyDirectories.getTradesDir() + '/20070920/IBM_trades.binRT' )
        
        zz = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getSize( 0 ),
            reader.getPrice( 0 )
        ])

        self.assertEqual(
            '[25367, 1190260800, 34210000, 76600, 116.2699966430664]',
            str( zz )
        )


if __name__ == "__main__":
    unittest.main()
