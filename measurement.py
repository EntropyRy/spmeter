#!/usr/bin/env python3
"""Measurement code.

This module performs the signal processing calculations
for sound level measurements.

The program reads audio data from stdin
and uses resultwriter.py to store measurement results.
"""
import sys
import math
import time

import numpy as np
from scipy import signal
#from pyfilterbank import splweighting

import resultwriter

# Number of samples for each block.
# This determines how often a log record is made.
bufsize = 48000*5

# Sample rate
fs = 48000

# TODO: move calibration value into settings.py
calib_c = 134.0

calib_a = calib_c

writer = resultwriter.Writer(measurement="spl")

def to_dB(v):
    if v > 0: return 10.0*math.log10(v)
    else: return -1000.0

def lowpass_ba(timeconstant, fs):
    x = math.exp(-1.0/(timeconstant*fs))
    return np.asarray([1-x]), np.asarray([1,-x])

#[a_wb, a_wa] = splweighting.a_weighting_coeffs_design(fs)
#[c_wb, c_wa] = splweighting.c_weighting_coeffs_design(fs)
# Hardcode them to avoid need to install pyfilterbank
a_wb = np.asarray([0.23430179229951347830, -0.46860358459902695660,
-0.23430179229951347830, 0.93720716919805391321,
-0.23430179229951347830, -0.46860358459902695660,
 0.23430179229951347830])
a_wa = np.asarray([1.00000000000000000000, -4.11304340877587115699,
6.55312175265504581745, -4.99084929416337796937,
1.78573730293757093612, -0.24619059531948619957,
0.01122425003323116767])
c_wb = np.asarray([0.19788712002639341492, 0.00000000000000000000,
-0.39577424005278682984, 0.00000000000000000000,
0.19788712002639341492])
c_wa = np.asarray([1.00000000000000000000, -2.21917291405280048266,
1.45513587894716867055, -0.24849607388778169326,
0.01253882314727234465])

[lpfb, lpfa] = lowpass_ba(0.125, fs)

a_zi = signal.lfiltic(a_wb, a_wa, [0])
c_zi = signal.lfiltic(c_wb, c_wa, [0])
al_zi = signal.lfiltic(lpfb, lpfa, [0])
cl_zi = signal.lfiltic(lpfb, lpfa, [0])

while True:
    buf = sys.stdin.buffer.read(4*bufsize)  # 32-bit samples
    time1 = time.time()
    audio = np.frombuffer(buf, dtype=np.float32)

    a_audio, a_zi = signal.lfilter(a_wb, a_wa, audio, zi=a_zi)
    c_audio, c_zi = signal.lfilter(c_wb, c_wa, audio, zi=c_zi)

    a_s = np.square(a_audio)
    c_s = np.square(c_audio)

    a_lpf, al_zi = signal.lfilter(lpfb, lpfa, a_s, zi=al_zi)
    c_lpf, cl_zi = signal.lfilter(lpfb, lpfa, c_s, zi=cl_zi)

    db_mean_a = calib_a + to_dB(np.mean(a_s))
    db_mean_c = calib_c + to_dB(np.mean(c_s))
    db_peak_a = calib_a + to_dB(np.max(a_s))
    db_peak_c = calib_c + to_dB(np.max(c_s))
    db_fast_a = calib_a + to_dB(np.max(a_lpf))
    db_fast_c = calib_c + to_dB(np.max(c_lpf))

    writer.write(time1, (
        ("LAeq",   db_mean_a),
        ("LApeak", db_peak_a),
        ("LAFmax", db_fast_a),
        ("LCeq",   db_mean_c),
        ("LCpeak", db_peak_c),
        ("LCFmax", db_fast_c),
    ))
