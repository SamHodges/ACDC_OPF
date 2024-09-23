from __future__ import division
from pyomo.environ import *
from models.DC_module.DC_model import DC_model

class Linear_DC(DC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
         
    def extra_setup(self):
        self.model.deltaL_DC  = Var(self.model.L_DC, domain= Reals)      # angle difference across lines
        self.model.deltaLT_DC = Var(self.model.TRANSF_DC, domain= Reals) # angle difference across transformers

    
    def extra_constraints(self):
        # --- Kirchoff's voltage law on each line and transformer---
        def KVL_line_def(model,l):
            return model.pL_DC[l] == (-model.BL_DC[l])*model.deltaL_DC[l]
        def KVL_trans_def(model,l):
            return model.pLT_DC[l] == (-model.BLT_DC[l])*model.deltaLT_DC[l]
        self.model.KVL_line_const_DC     = Constraint(self.model.L_DC, rule=KVL_line_def)
        self.model.KVL_trans_const_DC    = Constraint(self.model.TRANSF_DC, rule=KVL_trans_def)
        
        # --- phase angle constraints ---
        def phase_angle_diff1(model,l):
            return model.deltaL_DC[l] == model.delta_DC[model.A_DC[l,1]] - \
            model.delta_DC[model.A_DC[l,2]]
        self.model.phase_diff1_DC = Constraint(self.model.L_DC, rule=phase_angle_diff1)