from __future__ import division
from pyomo.environ import *
from models.DC_module.DC_model import DC_model

class NLP_DC(DC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
         
         
    def extra_setup(self):
        self.model.resistance_DC = Param(self.model.L_DC, within=NonNegativeReals) 
        self.model.poles_DC = Param(self.model.L_DC, within=NonNegativeReals) 
        
        self.model.v_DC = Var(self.model.B_DC, domain= NonNegativeReals) 
        
    
    def extra_constraints(self):
        def volt_constraint(model, b):
            for l in model.L_DC:
                if model.A_DC[l,1]==b:
                    if model.pL_DC[l] != model.poles_DC[l]*(1/model.resistance_DC[l])*model.v_DC[b]*(model.v_DC[b] - model.v_DC[model.A_DC[l,2]]):
                        return False
                    
            for l in model.L_DC:
                if model.A_DC[l,2]==b:
                    if model.pL_DC[l] != model.poles_DC[l]*(1/model.resistance_DC[l])*model.v_DC[b]*(model.v_DC[b] - model.v_DC[model.A_DC[l,2]]):
                        return False
                    
                
            return True