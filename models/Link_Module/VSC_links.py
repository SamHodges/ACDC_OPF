from __future__ import division
from pyomo.environ import *
from models.Link_Module.HVDC_links import HVDC_Links

class VSC_Links(HVDC_Links):
    def __init__(self, model):
         super().__init__(model)
         
    def extra_constraints(self):
        def PQ_Circle(model, g):
            return model.pG_AC[g]**2 + model.qG_AC[g]**2 <= model.PGmax_AC[g]**2
        self.model.inside_PQ_VSC = Constraint(self.model.HVDC_CONV, rule=PQ_Circle)
