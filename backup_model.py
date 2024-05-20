from pyomon.environ import *

# init model
model = AbstractModel()

# define sets needed
model.buses = Set() # set of buses
model.generators = Set()
model.wind_generators = Set()
model.demands = Set()
model.lines = Set()
model.shunt = Set()
model.reference_buses = Set(within=model.buses)
model.line_to_end_sets = Set()
model.transformers = Set()


# link different sets together 
model.generator_buses = Set(within=model.buses * model.generators) # what does the * mean here? overlap? or...?
model.wind_buses = Set(within=model.buses * model.wind)
model.demand_buses = Set(within=model.buses * model.demands)
model.shunt_buses = Set(within=model.buses * model.shunt)


# set some constraints as params linked to sets
model.bus_line_matrix = Param(model.lines * model.lines_to_end_sets, within=Any)
model.bus_transformer_matrix = Param(model.transformers * model.lines_to_end_sets, within=Any) # within = any?

model.power_demand = Param(model.demand, within=Reals)
model.value_lost_load = Param(model.demand, within=Reals) #how do these 2 combine for demand? or is something else happening?

model.max_power_generator = Param(model.generator, within=NonNegativeReals)
model.min_power_generator = Param(model.generator, within=Reals)
model.fpn = Param(model.generator, within=Reals)
model.max_power_wind = Param(model.wind_generators, within=NonNegativeReals)
model.min_power_wind = Param(model.wind_generators, within=NonNegativeReals)

model.power_line_limit = Param(model.lines, within=NonNegativeReals)
model.power_transformer_limit = Param(model.transformers, within)

# cost function
def cost_objective(model):
	objective = sum(model.)


# KCL + KVL



# power limits


# phase angle constraints


# reference bus constraint

