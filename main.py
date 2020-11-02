# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
import sys
from dwave.system import LeapHybridSampler
from math import log, ceil
import dimod
from dwave.cloud import Client

# From Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
# Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
# based on Lucas, Frontiers in Physics _2, 5 (2014)

#client = Client.from_config(config_file='dwave.conf')

# Found solution [12, 27, 20, 10] at energy -270.0.
# Found solution [12, 11, 20, 10, 15] at energy -270.0.
# Found solution [27, 20, 10, 15] at energy -286.0. -> lagrange = 1
# Found solution [12, 11, 20, 10, 15] at energy -270.0. -> lagrange = max(costs) * 2

def knapsack_bqm(costs, weights, weight_capacity):

    costs = costs

    # Initialize BQM - use large-capacity BQM so that the problem can be
    # scaled by the user.
    bqm = dimod.AdjVectorBQM(dimod.Vartype.BINARY)

    # Lagrangian multiplier
    # First guess as suggested in Lucas's paper
    lagrange = max(costs)

    # Number of objects
    x_size = len(costs)
    """
    # Lucas's algorithm introduces additional slack variables to handle
    # the inequality. max_y_index indicates the maximum index in the y
    # sum; hence the number of slack variables.
    max_y_index = ceil(log(weight_capacity, 2))


    # Slack variable list for Lucas's algorithm. The last variable has
    # a special value because it terminates the sequence.
    y = [2**n for n in range(max_y_index - 1)]
    y.append(weight_capacity + 1 - 2**(max_y_index - 1))

    # Hamiltonian xi-xi terms
    for k in range(x_size):
        bqm.set_linear('x' + str(k), lagrange * (weights[k]**2) - costs[k])
    
    # f)
        for n in range(x_size):
            bqm.set_linear('x' + str(n), lagrange * (weights[n]**2))
    # h) 
    for n in range(x_size):
        bqm.set_linear('x' + str(n), lagrange * -1 * costs[n])
    
   

    # Hamiltonian xi-xj terms
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = ('x' + str(i), 'x' + str(j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]
  
    # g)
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = ('x' + str(i), 'x' + str(j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]
   


    # Hamiltonian y-y terms
    for k in range(max_y_index):
        bqm.set_linear('y' + str(k), lagrange * (y[k]**2))
    
    # c)
    for n in range(70):
        bqm.set_linear('y' + str(n), lagrange * n**2)
   


    # Hamiltonian yi-yj terms
    for i in range(max_y_index):
        for j in range(i + 1, max_y_index):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * y[i] * y[j]

    # d)
    for i in range(70):
        for j in range(i + 1, 70):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * i * j
    
  


    # Hamiltonian x-y terms
    for i in range(x_size):
        for j in range(max_y_index):
            key = ('x' + str(i), 'y' + str(j))
            bqm.quadratic[key] = -2 * lagrange * weights[i] * y[j]


    # e)
    for n in range(70):
        for a in range(x_size):
            key = ('x' + str(a), 'y' + str(n))
            bqm.quadratic[key] = -2 * lagrange * n * weights[a]
    
    
    # These are not in the original solution
    # 1)
    # a)
    for n in range(70):
        bqm.set_linear('y' + str(n), lagrange * -1)

    # b)
    for i in range(70):
        for j in range(i + 1, 70):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange
    
    
    """

    # 1)
    # a)
    for n in range(weight_capacity):
        bqm.set_linear('y' + str(n), lagrange * -1)

    # b)
    for i in range(weight_capacity):
        for j in range(i + 1, weight_capacity):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange

    # 2)
    # c)
    for n in range(weight_capacity):
        bqm.set_linear('y' + str(n), lagrange * n ** 2)

    # d)
    for i in range(weight_capacity):
        for j in range(i + 1, weight_capacity):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * i * j

    # e)
    for n in range(weight_capacity):
        for a in range(x_size):
            key = ('x' + str(a), 'y' + str(n))
            bqm.quadratic[key] = -2 * lagrange * n * weights[a]
    # f)
    for n in range(x_size):
        bqm.set_linear('x' + str(n), lagrange * (weights[n] ** 2))

    # g)
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = ('x' + str(i), 'x' + str(j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]

    # 3)
    # h)
    for n in range(x_size):
        bqm.set_linear('x' + str(n), lagrange * -1 * costs[n])

    return bqm











data_file_name = "small.csv"
weight_capacity = 70

# parse input data
df = pd.read_csv(data_file_name, header=None)
df.columns = ['cost', 'weight']



bqm = knapsack_bqm(df['cost'], df['weight'], weight_capacity)

#exit()

sampler = LeapHybridSampler()
sampleset = sampler.sample(bqm)
for sample, energy in zip(sampleset.record.sample, sampleset.record.energy):

    # Build solution from returned bitstring
    solution = []
    for this_bit_index, this_bit in enumerate(sample):
        # The x's indicate whether each object has been selected
        this_var = sampleset.variables[this_bit_index]
        if this_bit and this_var.startswith('x'):
            # Indexing of the weights is different than the bitstring;
            # cannot guarantee any ordering of the bitstring, but the
            # weights are numerically sorted
            solution.append(df['weight'][int(this_var[1:])])
    print("Found solution {} at energy {}.".format(solution, energy))

#client.close()
