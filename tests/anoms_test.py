import tests
import unittest
from anoms import detect_anoms
import numpy as np


# Test that we can get exactly the same result as Twitter's AnomalyDetection library.
# The 'raw_data.txt' is containing the same data as 'raw_data.R'.
# The expected_*.txt files are containing the same result from 'vec_anom_detection.R' using same parameters.
def read_twitter_raw_data(filename):
    x = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            x.append(float(line))
    return x


def _read_twitter_test_result(filename):
    index = []
    e_values = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            parts = line.split(' ')
            index.append(int(parts[0]) - 1)  # The 'index' column. R's array index is from 1, not 0
            e_values.append(float(parts[2]))  # The 'expected_value' column
    return index, e_values


class TestDetectAnoms(unittest.TestCase):
    def test_seasonal_data(self):
        """
        An example from real Indeed data. Numbers are the click count of one of Indeed pages.
        The last number is an anomaly caused by a holiday.
        """
        x = [534592, 854369, 868702, 852728, 773757, 618216, 423549, 497898, 836237, 883591, 888337, 818443, 660449,
             482778, 477392, 904671, 943225, 918105, 843145, 685644, 511239, 558484, 894195, 927928, 919406, 852359,
             658974, 473478, 458006, 587811]
        anoms_index = detect_anoms(x, 7)
        self.assertEqual([29], anoms_index)

    def test_constants(self):
        ret = detect_anoms([1] * 1000, 14, direction='both')
        self.assertEqual([], ret)

    def test_twitter_data_both(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the direction=both
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_both.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_pos(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the direction=pos
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_pos.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='pos', e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_neg(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the direction=neg
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_neg.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='neg', e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_onlylast(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the only_last=True
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_onlylast.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', only_last=1440, e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_threshold_med(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the threshold=med_max
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_threshold_med.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', threshold='med_max', e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_threshold_p95(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the threshold=p95
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_threshold_p95.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', threshold='p95', e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_threshold_p99(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the threshold=p99
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_threshold_p99.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', threshold='p99', e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_longterm(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the longterm_period to 1440 * 7
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_longterm.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', longterm_period=1440 * 7,
                                       e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_twitter_data_longterm_onlylast(self):
        """
        Use the same test data from Twitter's library. The result will be exactly the same as Twitter's.
        Set the longterm_period to 1440 * 7
        """
        x = read_twitter_raw_data('tests/raw_data.txt')
        expected_index, expected_e_values = _read_twitter_test_result('tests/expected_longterm_onlylast.txt')
        index, e_values = detect_anoms(x, 1440, max_anoms=0.02, direction='both', longterm_period=1440 * 7,
                                       only_last=1440, e_value=True)
        self.assertListEqual(expected_index, index)
        self.assertListEqual(expected_e_values, list(e_values))

    def test_illegal_data_and_parameters(self):
        self.assertRaises(ValueError, detect_anoms, [1] * 1000, 14, max_anoms=0.5)
        self.assertRaises(ValueError, detect_anoms, [1] * 1000, 14, max_anoms=0)
        self.assertRaises(ValueError, detect_anoms, [1] * 1000, 14, alpha=0)
        self.assertRaises(ValueError, detect_anoms, [1] * 27, 14)  # time series' length is less than period * 2.
        x = [1] * 1000
        x[999] = np.nan
        self.assertRaises(ValueError, detect_anoms, x, 14)


class TestAnomWithBreakout(unittest.TestCase):
    def setUp(self):
        # A breakout happened in the position 33:
        self.data = read_twitter_raw_data('tests/anom_breakout_data.txt')

    def test_anom_without_breakout(self):
        # when the breakout just happened, reports it as anomaly, which is correct.
        ret = detect_anoms(self.data[3:33], 7, max_anoms=0.01, only_last=1)
        self.assertEqual([29], ret)
        # after the time windows moved forward, still reports the last data is anomaly, which is bad.
        ret = detect_anoms(self.data[8:38], 7, max_anoms=0.01, only_last=1)
        self.assertEqual([29], ret)
        ret = detect_anoms(self.data[12:42], 7, max_anoms=0.01, only_last=1)
        self.assertEqual([29], ret)

    def test_anom_with_breakout(self):
        breakout_kwargs = {'min_size': 7, 'method': 'multi', 'beta': 0.008}
        # when the breakout just happened, reports it as anomaly, which is correct.
        ret = detect_anoms(self.data[3:33], 7, max_anoms=0.01, only_last=1, breakout_kwargs=breakout_kwargs)
        self.assertEqual([29], ret)
        # after the time window moved forward, detects the breakout and stops reporting the last point as anomaly.
        ret = detect_anoms(self.data[8:38], 7, max_anoms=0.01, only_last=1, breakout_kwargs=breakout_kwargs)
        self.assertEqual([], ret)
        ret = detect_anoms(self.data[12:42], 7, max_anoms=0.01, only_last=1, breakout_kwargs=breakout_kwargs)
        self.assertEqual([], ret)
