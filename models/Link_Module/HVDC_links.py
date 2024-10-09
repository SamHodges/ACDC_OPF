from __future__ import division
from pyomo.environ import *

class HVDC_Links:
    def __init__(self, model):
         self.model = model
         
    def add_links(self):
        self.basic_links()
        self.extra_constraints()
         
    def basic_links(self):
        self.model.ACDC_Links   = Set(dimen=2)  # set of HVDC
        self.model.HVDC_Pairs   = Set(dimen=2)  # set of HVDC
        self.model.HVDC_CONV = Set(within=self.model.G_AC)
        self.model.LOCAL_HVDC = Set()
        
        def Equal_HVDC(model, g1, g2):
            return model.pG_AC[g1] == -model.pG_AC[g2]
        def ACDC_Link(model, g_AC, g_DC):
            return model.pG_AC[g_AC] == -model.pG_DC[g_DC]
        def ACDC_stop_circumnavigation(model, g_AC, g_DC):
            return sum(model.pG_DC[g[1]] for g in model.ACDC_Links) >= 0
        self.model.equalHVDC = Constraint(self.model.HVDC_Pairs, rule=Equal_HVDC)
        self.model.link_ACDC = Constraint(self.model.ACDC_Links, rule=ACDC_Link)
        # self.model.ACDC_Limit = Constraint(self.model.ACDC_Links, rule=ACDC_stop_circumnavigation)
        
    def extra_constraints(self):
        pass