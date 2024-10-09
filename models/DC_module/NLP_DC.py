from __future__ import division
from pyomo.environ import *
from models.DC_module.DC_model import DC_model

class NLP_DC(DC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
          
    def extra_setup(self):
        pass
        self.model.poles_DC = Param(self.model.L_DC,  within=NonNegativeReals) # poles per line
        self.model.r_DC = Param(self.model.L_DC,  within=NonNegativeReals) # resistance per line
        self.model.rT_DC = Param(self.model.L_DC,  within=NonNegativeReals) # resistance per line
        
        self.model.Vmax_DC = Param(self.model.B_DC, within=NonNegativeReals) #  max voltage angle
        self.model.Vmin_DC = Param(self.model.B_DC, within=NonNegativeReals) #  min voltage angle
        
        self.model.v_DC = Var(self.model.B_DC,  within=NonNegativeReals) # voltage per bus
        self.model.pLfrom_DC   = Var(self.model.L_DC, domain= Reals) # real power injected at b onto line
        self.model.pLto_DC     = Var(self.model.L_DC, domain= Reals) # real power injected at b' onto line
        self.model.pLfromT_DC  = Var(self.model.TRANSF_DC, domain= Reals) # real power injected at b onto transformer
        self.model.pLtoT_DC    = Var(self.model.TRANSF_DC, domain= Reals) # real power injected at b' onto transformer

     
    def extra_constraints(self):
        def KCL_real_def(model, b):
            return sum(model.pG_DC[g] for g in model.G_DC if (b,g) in model.Gbs_DC) +\
            sum(model.pW_DC[w] for w in model.WIND_DC if (b,w) in model.Wbs_DC)==\
            sum(model.pLfrom_DC[l] for l in model.L_DC if model.A_DC[l,1]==b)+ \
            sum(model.pLto_DC[l] for l in model.L_DC if model.A_DC[l,2]==b)+\
            sum(model.pLfromT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,1]==b)+ \
            sum(model.pLtoT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,2]==b) +\
            sum(model.GB_DC[s]*model.v_DC[b]**2 for s in model.SHUNT_DC if (b,s) in model.SHUNTbs_DC)

        self.model.KCL_DC     = Constraint(self.model.B_DC, rule=KCL_real_def)
        
        # --- Kirchoff's voltage law on each line ---
        def KVL_DC_from(model,l):
            return model.pLfrom_DC[l] == model.poles_DC[l] * (1/model.r_DC[l]) * model.v_DC[model.A_DC[l,2]] * (model.v_DC[model.A_DC[l,2]] - model.v_DC[model.A_DC[l,1]])
        def KVL_DC_to(model,l):
            return model.pLto_DC[l] == model.poles_DC[l] * (1/model.r_DC[l]) * model.v_DC[model.A_DC[l,1]] * (model.v_DC[model.A_DC[l,1]] - model.v_DC[model.A_DC[l,2]])
        self.model.KVL_DC_from_C     = Constraint(self.model.L_DC, rule=KVL_DC_from)
        self.model.KVL_DC_to_C      = Constraint(self.model.L_DC, rule=KVL_DC_to)
        
        # --- Kirchoff's voltage law on each transformer line ---
        def KVL_T_DC_from(model,l):
            return model.pLfromT_DC[l] == model.poles_DC[l] * (1/model.rT_DC[l]) * model.v_DC[model.A_DC[l,2]] * (model.v_DC[model.A_DC[l,2]] - model.v_DC[model.A_DC[l,1]])
        def KVL_T_DC_to(model,l):
            return model.pLtoT_DC[l] == model.poles_DC[l] * (1/model.rT_DC[l]) * model.v_DC[model.A_DC[l,1]] * (model.v_DC[model.A_DC[l,1]] - model.v_DC[model.A_DC[l,2]])
        self.model.KVL_T_DC_from_C     = Constraint(self.model.TRANSF_DC, rule=KVL_T_DC_from)
        self.model.KVL_T_DC_to_C       = Constraint(self.model.TRANSF_DC, rule=KVL_T_DC_to)
        
         # --- voltage constraints ---
        def bus_max_dc_voltage(model,b):
            return model.v_DC[b] <= model.Vmax_DC[b]
        def bus_min_dc_voltage(model,b):
            return model.v_DC[b] >= model.Vmin_DC[b]
        self.model.Vmaxc_DC = Constraint(self.model.B_DC, rule=bus_max_dc_voltage)
        self.model.Vminc_DC = Constraint(self.model.B_DC, rule=bus_min_dc_voltage)
        
        
        
        