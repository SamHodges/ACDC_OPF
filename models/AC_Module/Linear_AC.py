from __future__ import division
from pyomo.environ import *
from models.AC_Module.AC_model import AC_model

class Linear_AC(AC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
         
    def extra_setup(self):
        self.model.pL_AC      = Var(self.model.L_AC, domain= Reals) # real power injected at b onto line l, p.u.
        self.model.pLT_AC     = Var(self.model.TRANSF_AC, domain= Reals) # real power injected at b onto transformer line l, p.u.
        self.model.deltaL_AC  = Var(self.model.L_AC, domain= Reals)      # angle difference across lines
        self.model.deltaLT_AC = Var(self.model.TRANSF_AC, domain= Reals) # angle difference across transformers
                
        
    def extra_constraints(self):
        # --- Kirchoff's current law at each bus b ---
        def KCL_def(model, b):
            return sum(model.pG_AC[g] for g in model.G_AC if (b,g) in model.Gbs_AC) +\
            sum(model.pW_AC[w] for w in model.WIND_AC if (b,w) in model.Wbs_AC) == \
            sum(model.pD_AC[d] for d in model.D_AC if (b,d) in model.Dbs_AC)+\
            sum(model.pL_AC[l] for l in model.L_AC if model.A_AC[l,1]==b)- \
            sum(model.pL_AC[l] for l in model.L_AC if model.A_AC[l,2]==b)+\
            sum(model.pLT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,1]==b)- \
            sum(model.pLT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,2]==b)+\
            sum(model.GB_AC[s] for s in model.SHUNT_AC if (b,s) in model.SHUNTbs_AC)
        self.model.KCL_const_AC = Constraint(self.model.B_AC, rule=KCL_def)

        # --- Kirchoff's voltage law on each line and transformer---
        def KVL_line_def(model,l):
            return model.pL_AC[l] == (-model.BL_AC[l])*model.deltaL_AC[l]
        def KVL_trans_def(model,l):
            return model.pLT_AC[l] == (-model.BLT_AC[l])*model.deltaLT[l]
        self.model.KVL_line_const_AC     = Constraint(self.model.L_AC, rule=KVL_line_def)
        self.model.KVL_trans_const_AC    = Constraint(self.model.TRANSF_AC, rule=KVL_trans_def)

        #  --- demand model ---
        def demand_model(model,d):
            return model.pD_AC[d] == model.alpha_AC[d]*model.PD_AC[d]
        self.model.demandmodelC_AC = Constraint(self.model.D_AC, rule=demand_model)


        # # --- power flow limits on transformer lines---
        def transf_lim1_def(model,l):
            return model.pLT_AC[l] <= model.SLmaxT_AC[l]
        def transf_lim2_def(model,l):
            return model.pLT_AC[l] >= -model.SLmaxT_AC[l]
        self.model.transf_lim1_AC = Constraint(self.model.TRANSF_AC, rule=transf_lim1_def)
        self.model.transf_lim2_AC = Constraint(self.model.TRANSF_AC, rule=transf_lim2_def)

        # # --- phase angle constraints ---
        def phase_angle_diff1(model,l):
            return model.deltaL_AC[l] == model.delta_AC[model.A_AC[l,1]] - \
            model.delta_AC[model.A_AC[l,2]]
        self.model.phase_diff1_AC = Constraint(self.model.L_AC, rule=phase_angle_diff1)
