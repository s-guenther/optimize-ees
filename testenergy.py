#!/usr/bin/env python3
"""
Loads a predefined factory setup, feeds optimization class and prints some
outputs.
"""

from factories import DataFactory, ObjectiveFactory, HybridSetupFactory, \
    SingleSetupFactory, StorageFactory
from optimize_ess import OptimizeHybridESS, OptimizeSingleESS
from storage import Storage
from objective import Objective
from hybriddia import HybridDia
import timeit

signal = DataFactory.rand(200, mu=1, freq=(6, 10),
                          ampl=(1, 3), time=100, seed=200)
signal.pplot()
objective = Objective('energy', 170)
storage = Storage(2.1, 0.95, 1e50)
opt = OptimizeSingleESS(signal, storage, objective)
opt.solve_pyomo_model()

base = Storage(1.05, 0.95, 1e50)
peak = Storage(1.05, 0.95, 1e50)
opthyb = OptimizeHybridESS(signal, base, peak, objective)
opthyb.solve_pyomo_model()

virtualbreakpoint = True
