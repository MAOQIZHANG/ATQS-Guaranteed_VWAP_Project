import unittest
import os
import numpy as np
import sys

src_path = 'src'

# Add the src folder to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from impact_model import ImpactModel

class Test_Impact(unittest.TestCase):

    def test_vol(self):

        hTest = ImpactModel('Impact-Model-Matrix')
        hTest.read_data()

        self.assertAlmostEqual(5.262253830959499e-07, hTest.cal_temp_impact('JAVA', 0, 10))
        self.assertEqual((502, 65), hTest.df_h.shape)
        # self.assertEqual(hTest.cal_temp_impact('JAVA', 0, 10.25 * 60 * 60 * 1000), hTest.cal_temp_impact('JAVA', 0, 10.75 * 60 * 60 * 1000))
        
        
if __name__ == "__main__":
    unittest.main()
