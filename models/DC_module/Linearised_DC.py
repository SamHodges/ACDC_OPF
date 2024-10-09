from __future__ import division
from pyomo.environ import *
from models.DC_module.DC_model import DC_model

class Linear_DC(DC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
         
    def extra_setup(self):
        self.model.deltaL_DC  = Var(self.model.L_DC, domain= Reals)      # angle difference across lines
        self.model.deltaLT_DC = Var(self.model.TRANSF_DC, domain= Reals) # angle difference across transformers
        
        self.model.pL_DC      = Var(self.model.L_DC, domain= Reals) # real power injected at b onto line l, p.u.
        self.model.pLT_DC     = Var(self.model.TRANSF_DC, domain= Reals) # real power injected at b onto transformer line l, 

    
    def extra_constraints(self):
        # --- Kirchoff's current law at each bus b ---
        def KCL_def(model, b):
            return sum(model.pG_DC[g] for g in model.G_DC if (b,g) in model.Gbs_DC) +\
            sum(model.pW_DC[w] for w in model.WIND_DC if (b,w) in model.Wbs_DC) == \
            sum(model.pL_DC[l] for l in model.L_DC if model.A_DC[l,1]==b)- \
            sum(model.pL_DC[l] for l in model.L_DC if model.A_DC[l,2]==b)+\
            sum(model.pLT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,1]==b)- \
            sum(model.pLT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,2]==b)+\
            sum(model.GB_DC[s] for s in model.SHUNT_DC if (b,s) in model.SHUNTbs_DC)
        self.model.KCL_const_DC = Constraint(self.model.B_DC, rule=KCL_def)
        
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
        
        # # --- line power limits ---
        def line_lim1_def(model,l):
            return model.pL_DC[l] <= model.SLmax_DC[l]
        def line_lim2_def(model,l):
            return model.pL_DC[l] >= -model.SLmax_DC[l]
        self.model.line_lim1_DC = Constraint(self.model.L_DC, rule=line_lim1_def)
        self.model.line_lim2_DC = Constraint(self.model.L_DC, rule=line_lim2_def)

        # # --- power flow limits on transformer lines---
        def transf_lim1_def(model,l):
            return model.pLT_DC[l] <= model.SLmaxT_DC[l]
        def transf_lim2_def(model,l):
            return model.pLT_DC[l] >= -model.SLmaxT_DC[l]
        self.model.transf_lim1_DC = Constraint(self.model.TRANSF_DC, rule=transf_lim1_def)
        self.model.transf_lim2_DC = Constraint(self.model.TRANSF_DC, rule=transf_lim2_def)