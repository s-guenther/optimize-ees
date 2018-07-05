#!/usr/bin/env python3

from optimize_ess import OptimizeSingleESS, OptimizeHybridESS
from powersignal import Signal
from storage import Storage
from objective import Objective, Solver
from matplotlib import pyplot as plt
from collections import defaultdict


class OnTheFlyDict(defaultdict):
    """Performs for a specific cut which is missing in the inter/nointer
    dict of HybridDia the adequate calculation and adds it the dict"""
    def __init__(self, hybdia, strategy):
        super().__init__()
        self.hybdia = hybdia
        self.strategy = strategy

    def __missing__(self, key):
        optim_case = self.hybdia.calculate_cut(key, self.strategy, True)
        return optim_case


class HybridDia:
    # noinspection PyArgumentList
    def __init__(self, signal, singlestorage, objective, solver='gurobi',
                 name='Hybridisation Diagram'):
        self.signal = Signal(signal)
        self.storage = Storage(singlestorage)
        self.objective = Objective(objective)
        self.solver = Solver(solver)
        self.single = None
        self.inter = OnTheFlyDict(self, 'inter')
        self.nointer = OnTheFlyDict(self, 'nointer')
        self.name = str(name)

    def calculate_single(self, add_to_internal_list=True):
        single = OptimizeSingleESS(self.signal, self.storage,
                                   self.objective, self.solver)
        if add_to_internal_list:
            self.single = single
        return single

    def calculate_cut(self, cut, strategy='inter', add_to_internal_list=True):
        signal = self.signal
        base = cut*self.storage
        peak = (1 - cut)*self.storage
        objective = self.objective
        solver = self.solver

        optim_case = OptimizeHybridESS(signal, base, peak, objective,
                                       strategy, solver)

        if add_to_internal_list:
            if strategy == 'inter':
                self.inter[cut] = optim_case
            elif strategy == 'nointer':
                self.nointer[cut] = optim_case
        return optim_case

    def calculate_curves(self, cuts=None):
        if cuts is None:
            cuts = [0.1, 0.25, 0.4, 0.6, 0.9]

        if not self.single:
            self.calculate_single()

        for cut in cuts:
            # TODO parallelize this code
            print('Starting cut={}'.format(cut))
            self.calculate_cut(cut, 'inter')
            self.calculate_cut(cut, 'nointer')
            print('Ending cut={}'.format(cut))

    def pprint(self):
        # TODO implement
        pass

    def pplot(self):
        if not self.inter or not self.nointer:
            self.calculate_curves()

        # TODO remove duplicate code
        cutsinter = [0]
        inter = [0]
        for cut in sorted(self.inter.keys()):
            cutsinter.append(cut)
            optim_case = self.inter[cut]
            inter.append(optim_case.results.baseenergycapacity)
        cutsinter.append(1)
        inter.append(self.single.results.energycapacity)

        cutsnointer = [0]
        nointer = [0]
        for cut in sorted(self.nointer.keys()):
            cutsnointer.append(cut)
            optim_case = self.nointer[cut]
            nointer.append(optim_case.results.baseenergycapacity)
        cutsnointer.append(1)
        nointer.append(self.single.results.energycapacity)

        ax = plt.figure().add_subplot(1, 1, 1)
        ax.plot([0, self.single.results.energycapacity], [0, 1])
        ax.plot(nointer, cutsnointer, linestyle='--')
        ax.plot(inter, cutsinter)
        ax.set_ylabel('Cut')
        ax.set_xlabel('Energy')
        ax.autoscale(tight=True)

# TODO __repr__