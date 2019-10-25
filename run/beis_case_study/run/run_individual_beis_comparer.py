import sys

from multiprocessing import Pool, cpu_count
import pickle
sys.path.insert(0, '/home/alexkell/elecsim/')

from elecsim.model.world import World

import pandas as pd

from elecsim.constants import ROOT_DIR
import logging
logger = logging.getLogger(__name__)
import numpy as np


"""
File name: run_individual_beis_comparer
Date created: 23/10/2019
Feature: #Enter feature description here
"""

__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"

ga_results = pd.read_csv('run/beis_case_study/data/GA_optimisation_results/GA_results.csv')
# ga_results = pd.read_csv('/Users/b1017579/Documents/PhD/Projects/10. ELECSIM/run/beis_case_study/data/GA_optimisation_results/GA_results.csv')

ga_results_small = ga_results[ga_results.reward < 10].iloc[:,7:-5]
params_list = ga_results_small.values.tolist()


params_repeated = np.repeat(params_list, 10, axis=0)

params_repeated_list = params_repeated.tolist()

# params_repeated_list = np.array([0]*74).reshape(2,-1).tolist()


# ray.init()

# @ray.remote
def eval_world_parallel(individual):
    prices_individual = np.array(individual[:-3]).reshape(-1, 2).tolist()

    MARKET_TIME_SPLICES = 8
    YEARS_TO_RUN = 18
    number_of_steps = YEARS_TO_RUN * MARKET_TIME_SPLICES

    scenario_2018 = "{}/../run/beis_case_study/scenario/reference_scenario_2018.py".format(ROOT_DIR)
    world = World(initialization_year=2018, scenario_file=scenario_2018, market_time_splices=MARKET_TIME_SPLICES, data_folder="best_run_beis_comparison", number_of_steps=number_of_steps, long_term_fitting_params=prices_individual, highest_demand=63910, nuclear_subsidy=individual[-3], future_price_uncertainty_m=individual[-2], future_price_uncertainty_c=individual[-1])

    for j in range(YEARS_TO_RUN):
        for i in range(MARKET_TIME_SPLICES):
            try:
                print("j:{}, i: {}".format(j, i))
                results_df, over_invested = world.step()
            except:
                return 99999, 0
    del world
    return individual, results_df


#
# results_id = []
# for param_list in params_repeated_list:
#     results_id.append(eval_world_parallel.remote(param_list))
#
# results = ray.get(results_id)
#
# with open('results.pkl', 'wb') as f:
#     pickle.dump(results, f)


pool = Pool(cpu_count())
out1, out2 = zip(*pool.map(eval_world_parallel, params_repeated_list))

with open('out1.pkl', 'wb') as f:
    pickle.dump(out1, f)

with open('out2.pkl', 'wb') as f:
    pickle.dump(out2, f)