import numpy as np
from pyloess import stl
from scipy.stats import t
from pandas import Series
from math import floor
from breakout import detect_breakout
import logging

logger = logging.getLogger('indeed.anoms')


def detect_anoms(x, period, max_anoms=0.10, alpha=0.05, direction='both', longterm_period=None, only_last=None,
                 threshold=None, e_value=False, breakout_kwargs=None):
    """
    Anomaly Detection Using Seasonal Hybrid ESD Test.
    :param x: a list of floats, which consists of the observations.
    :param period: int, the number of observations in a single period.
    :param max_anoms: float in (0, 0.49]. Maximum number of anomalies that S-H-ESD will detect as a percentage of the
                                          data
    :param alpha: float. The level of statistical significance with which to accept or reject anomalies.
    :param direction: string. Directionality of the anomalies to be detected. Options are: 'pos', 'neg', 'both'.
                              'pos' only reports positive going anomalies, 'neg' only reports negative going anomalies,
                              'both' report anomalies on both direction,
    :param longterm_period: int. Split x into lists of given size, and perform anomaly detection on them
                            individually.
    :param only_last: int. Find and report anomalies only within a length in the tail of the time series.
    :param threshold: string. Only report positive going anomalies above the threshold specified.
                     Options are: None, 'med_max', 'p95' and 'p99'.
    :param e_value: boolean. Returns an additional list containing the expected value.
    :param breakout_kwargs: dict. If given, use it as parameter to call breakout detection to improve the trends.
    :return: a list of int, consists of the index of the anomalies in x.
             If e_value is set to True, a list of float is returned as the second return value, which consists the
             expected values of each detected anomaly.
    """
    if max_anoms > 0.49 or max_anoms <= 0:
        raise ValueError("max_anoms must be >0 and <= 0.49")
    if alpha <= 0:
        raise ValueError("alpha must greater than 0.")
    if longterm_period is None:
        longterm_period = len(x)
    for v in x:
        if np.isnan(v):
            raise ValueError("data contains NaN value.")
    ret = set()
    e_values = None
    if e_value:
        e_values = [None] * len(x)  # To keep the expected values when e_value is set.
    for window_start in range(0, len(x), longterm_period):
        # If the data is too long, split the data into smaller windows, and do the anomaly detection on each window.
        window_end = min(len(x), window_start + longterm_period)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Start to process window: window_start=%s, window_end=%s" %
                         (window_start, window_end))
        # If the window size doesn't divide the total size, the last window doesn't have enough data.
        # In this case, adjust the start position of last window to make it having same size as previous windows.
        if window_end - window_start < longterm_period:
            window_start = window_end - longterm_period
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("The last window doesn't contain enough length of data. "
                             "Adjusted the starting index. window_start=%s, window_end=%s" % (window_start, window_end))
        window_x = x[window_start:window_end]
        if len(window_x) < period * 2:
            raise ValueError("Anom detection needs at least 2 periods worth of data.")
        window_ret = _detect_anomaly_for_one_window(window_x, period, max_anoms, alpha, direction, e_values,
                                                    window_start, breakout_kwargs)
        if threshold:
            window_ret = _post_processing_threshold(window_x, period, window_ret, threshold)
        ret = ret.union(window_ret)
    if only_last:
        ret = _post_processing_only_last(x, ret, only_last)
    ret = sorted(ret)
    if e_value:
        return ret, map(lambda i: e_values[i], ret)
    return ret


def _get_trends_by_median(x):
    median = np.median(x)
    return [median] * len(x)


def _get_trends_by_breakout_detection(x, kwargs):
    # divide the data into parts using breakout detection, using the median of each part as the trend.
    ret_list = detect_breakout(x, **kwargs)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("detect_breakout result: %s" % ret_list)
    last_loc = len(x)
    if last_loc not in ret_list:
        ret_list.append(last_loc)
    prev_loc = 0
    trends = []
    for loc in ret_list:
        median = np.median(x[prev_loc:loc])
        trends.extend([median] * (loc - prev_loc))
        prev_loc = loc
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("detect_breakout trends: %s length=%s" % (trends, len(trends)))
    return trends


def _detect_anomaly_for_one_window(x, period, max_anoms, alpha, direction, e_values, window_start, breakout_kwargs):
    # The core part of anomaly detection:
    # 1. Use STL to perform seasonal decomposition.
    # parameters are copied from R's stl()
    stl_ret = stl(x, np=period, ns=len(x) * 10 + 1, isdeg=0, robust=True, ni=1, no=15)
    # 2. Calculate residuals using seasonal from STL result and median as the trends.
    seasons = stl_ret['seasonal']
    if e_values:  # store the expected values if e_value is set
        trends = stl_ret['trend']
        for i in range(0, len(x)):
            if e_values[window_start + i] is None:
                e_values[window_start + i] = floor(seasons[i] + trends[i])
    if breakout_kwargs:
        trends = _get_trends_by_breakout_detection(x, breakout_kwargs)
    else:
        trends = _get_trends_by_median(x)
    residuals = [x[i] - seasons[i] - trends[i] for i in range(0, len(x))]
    # 3. Use ESD to find out outliers from residuals. These outliers' corresponding values in x are the anomalies
    max_anom_num = max(1, int(len(x) * max_anoms))
    anom_index = _esd(residuals, max_anom_num, alpha, direction=direction)
    ret = set()
    for anom_i in anom_index:
        ret.add(window_start + anom_i)  # convert the index to the index in x
    return ret


def _post_processing_threshold(x, period, ret, threshold):
    # The threshold is calculated from the max values of each window.
    period_maxs = []
    for i in range(0, len(x), period):
        period_maxs.append(max(x[i: min(len(x), i + period)]))
    thresh = 0
    if threshold == 'med_max':
        thresh = np.median(period_maxs)
    elif threshold == 'p95':
        thresh = np.percentile(period_maxs, 95)
    elif threshold == 'p99':
        thresh = np.percentile(period_maxs, 99)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("threshold is True. threshold=%s, thresh=%s" % (threshold, thresh))
    ret = set(filter(lambda index: x[index] >= thresh, ret))
    return ret


def _post_processing_only_last(x, ret, only_last):
    last_period_start = len(x) - only_last
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("only_last is set. Will remove all anomalies before index %s." % last_period_start)
    ret = set(filter(lambda value: value >= last_period_start, ret))
    return ret


_MAD_CONSTANT = 1.4826  # a magic number copied from R's mad() function


def _esd(x, max_outlier, alpha, direction):
    """
    The ESD test using median and MAD in the calculation of the test statistic.
    """
    x = Series(x)
    n = len(x)
    outlier_index = []
    for i in range(1, max_outlier + 1):
        median = x.median()
        mad = np.median([abs(value - median) for value in x]) * _MAD_CONSTANT
        if mad == 0:
            break
        if direction == 'both':
            ares = x.map(lambda value: abs(value - median) / mad)
        elif direction == 'pos':
            ares = x.map(lambda value: (value - median) / mad)
        elif direction == 'neg':
            ares = x.map(lambda value: (median - value) / mad)
        r_idx = ares.idxmax()
        r = ares[r_idx]
        if direction == 'both':
            p = 1.0 - alpha / (2 * (n - i + 1))
        else:
            p = 1.0 - alpha / (n - i + 1)
        crit = t.ppf(p, n-i-1)
        lam = (n-i)*crit / np.sqrt((n-i-1+crit**2) * (n-i+1))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("%s/%s outlier. median=%s, mad=%s, r_idx=%s, r=%s, crit=%s, lam=%s" %
                         (i, max_outlier, median, mad, r_idx, r, crit, lam))
        if r > lam:
            outlier_index.append(r_idx)
            x = x.drop(r_idx)
        else:
            # The r keeps decreasing while lam keeps increasing. Therefore, when r is less than lam for the first time,
            # we can stop.
            break
    return outlier_index
