import unittest

import senzing_governor
from senzing_governor import Governor

__all__ = []
__version__ = "1.0.0"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2022-01-05'
__updated__ = '2022-01-05'

class TestGetWaitTime(unittest.TestCase):

    def test_get_wait_time_step_1(self):
        """
        Test ratio <= 0.1
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_230_000_000)
        self.assertEqual(result, 0)
        governor.close()

    def test_get_wait_time_step_2(self):
        """
        Test ratio <= 0.2
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_260_000_000)
        self.assertEqual(result, 0.1)
        governor.close()

    def test_get_wait_time_step_3(self):
        """
        Test ratio <= 0.4
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_320_000_000)
        self.assertEqual(result, 0.5)
        governor.close()

    def test_get_wait_time_step_4(self):
        """
        Test ratio <= 0.8
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_430_000_000)
        self.assertEqual(result, 4)
        governor.close()

    def test_get_wait_time_step_5(self):
        """
        Test ratio <= 0.8
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_440_000_000)
        self.assertEqual(result, 4)
        governor.close()

    def test_get_wait_time_step_6(self):
        """
        Test ratio <= 1
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_500_000_000)
        self.assertEqual(result, 9)
        governor.close()

    def test_get_wait_time_step_7(self):
        """
        Test ratio > 1
        """
        governor = Governor(hint="Tester")
        result = governor.get_wait_time(1_500_000_001)
        self.assertEqual(result, -1.0)
        governor.close()


if __name__ == '__main__':
    unittest.main()
