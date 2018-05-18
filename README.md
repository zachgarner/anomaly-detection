# AnomalyDetection and BreakoutDetection in Python 3

This is a fork of Indeed's port of Twitter's AnomalyDetection and BreakoutDetection.

Twitter's original code is in R. Indeed's port is for Python 2. This fork supports Python 3

References:
 - https://github.com/indeedeng/anomaly-detection
 - https://github.com/twitter/AnomalyDetection

To Install:
- pip install py3c
- python setup.py install
- Also see Indeed's README


Note that the function definition of detect_anoms is incorrect in Indeed's README.
Use this:
```
   res = detect_anoms(x, 0.02)
```
