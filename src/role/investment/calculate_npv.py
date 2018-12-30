import logging
from inspect import signature

import pandas as pd
from numpy import npv

from src.plants.plant_registry import PlantRegistry
from src.scenario.scenario_data import modern_plant_costs

logger = logging.getLogger(__name__)

from src.role.plants.costs.fuel_plant_cost_calculations import FuelPlantCostCalculations
from src.role.plants.costs.non_fuel_cost_calculations import NonFuelCostCalculation
from src.plants.plant_costs.estimate_costs.estimate_costs import create_power_plant


"""
File name: calculate_npv
Date created: 24/12/2018
Feature: # Contains functionality to assess options of investment and return lowest NPV for decision to be made.
"""

__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"

class CalculateNPV:

    def __init__(self, discount_rate, year, expected_sell_price):
        self.discount_rate = discount_rate
        self.year = year
        self.expected_sell_price = expected_sell_price

    def calculate_npv(self, plant_type, plant_size):
        plant = create_power_plant("Test", self.year, plant_type, plant_size)

        expected_cash_flow = self.calculate_expected_cash_flow(plant)
        npv_value = npv(self.discount_rate, expected_cash_flow)
        return npv_value

    def calculate_expected_cash_flow(self, plant):
        fuel_required = PlantRegistry(plant.plant_type).check_if_fuel_required()
        if fuel_required:
            CostCalculation = FuelPlantCostCalculations
        else:
            CostCalculation = NonFuelCostCalculation


        plant_dict = vars(plant)
        func = CostCalculation
        args_to_use = signature(func)._parameters
        dict_to_use = {key: plant_dict[key] for key in plant_dict if key in args_to_use}
        cost_calc = CostCalculation(**dict_to_use)
        total_costs = cost_calc.calculate_total_costs()[1]
        total_income = cost_calc.total_income(self.expected_sell_price)
        expected_cash_flow = [income - cost for income, cost in zip(total_income, total_costs)]
        return expected_cash_flow


    def highest_npv(self):
        cost_list = []
        for plant_type in ['CCGT','Coal','Nuclear','Onshore', 'Offshore', 'PV', 'Pumped_storage', 'Hydro', 'Biomass_wood']:
            plant_cost_data = modern_plant_costs[modern_plant_costs.Type==plant_type]
            for plant_row in plant_cost_data.itertuples():
                npv = self.calculate_npv(plant_row.Type, plant_row.Plant_Size)
                dict = {"npv":npv, "capacity":plant_row.Plant_Size, "plant_type":plant_row.Type}
                cost_list.append(dict)

        npv_results = pd.DataFrame(cost_list)

        # max_result = npv_results[npv_results['npv']==npv_results['npv'].max()]
        # logger.debug(npv_results[npv_results['npv']==npv_results['npv'].max()])
        sorted_npv = npv_results.sort_values(by='npv', ascending=False)
        logger.debug("sorted_npv: {}".format(sorted_npv))
        # return npv_results[npv_results['npv']==npv_results['npv'].max()]

