#!/usr/bin/env python3
"""Load csv file, generate signal from in, define rest of optimisation
setup, run optimisation, save results"""

import numpy as np
import timeit
from scipy.signal import resample
from matplotlib import pyplot as plt

from hybriddia import HybridDia
from objective import Objective
from powersignal import Signal
from storage import Storage

data = np.genfromtxt('stahlwerkmod.csv', delimiter=';')
power = data[:, 4]
time = (np.arange(len(power))*6 + 6)/3600

resampled_power, resampled_time = resample(power, t=time,
                                           num=int(np.floor(len(time)/10/15)))

signal = Signal(time, power)
resampled_signal = Signal(resampled_time, resampled_power)

peakcut = 1050
storpower = max(resampled_signal.vals) - peakcut

objective = Objective('power', peakcut)
storage = Storage(storpower, 0.95, 1e-3)

# ax = plt.figure().add_subplot(1, 1, 1)
# signal.pplot(ax=ax)
# resampled_signal.pplot(ax=ax)

print('Initializing HybridDia Object...')
start = timeit.default_timer()
hybdia = HybridDia(resampled_signal, storage, objective, name='Stahlwerk Unna')
end = timeit.default_timer() - start
print('Initialized... Time: {} seconds'.format(end))

start = timeit.default_timer()
hybdia.calculate_curves(cuts=(0.25, 0.4, 0.55, 0.8))
end = timeit.default_timer() - start
print('Calculated... Time: {} seconds'.format(end))

a = 'asdf'