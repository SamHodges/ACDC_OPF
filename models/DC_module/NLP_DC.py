from __future__ import division
from pyomo.environ import *
from models.DC_module.DC_model import DC_model

class NLP_DC(DC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
          
    def extra_setup(self):
        self.model.poles_DC = Param(self.model.L_DC,  within=NonNegativeReals) # poles per line
        self.model.r_DC = Param(self.model.L_DC,  within=NonNegativeReals) # resistance per line
        
        self.model.v_DC = Var(self.model.B_DC,  within=NonNegativeReals) # voltage per bus
        self.model.pLfrom_DC   = Var(self.model.L_DC, domain= Reals) # real power injected at b onto line
        self.model.pLto_DC     = Var(self.model.L_DC, domain= Reals) # real power injected at b' onto line
        self.model.pLfromT_DC  = Var(self.model.TRANSF_DC, domain= Reals) # real power injected at b onto transformer
        self.model.pLtoT_DC    = Var(self.model.TRANSF_DC, domain= Reals) # real power injected at b' onto transformer

     
    def extra_constraints(self):
        def KCL_real_def(model, b):
            return sum(model.pG_DC[g] for g in model.G_DC if (b,g) in model.Gbs_DC) +\
            sum(model.pW_DC[w] for w in model.WIND_DC if (b,w) in model.Wbs_DC)==\
            sum(model.pD_DC[d] for d in model.D_DC if (b,d) in model.Dbs_DC)+\
            sum(model.pLfrom_DC[l] for l in model.L_DC if model.A_DC[l,1]==b)+ \
            sum(model.pLto_DC[l] for l in model.L_DC if model.A_DC[l,2]==b)+\
            sum(model.pLfromT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,1]==b)+ \
            sum(model.pLtoT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,2]==b)+\
            sum(model.GB_DC[s]*model.v_DC[b]**2 for s in model.SHUNT_DC if (b,s) in model.SHUNTbs_DC)

        self.model.KCL_real     = Constraint(self.model.B_DC, rule=KCL_real_def)
        
        # --- Kirchoff's voltage law on each line ---
        def KVL_real_fromend(model,l):
            return model.pLfrom_DC[l] == model.G11[l]*(model.v_DC[model.A_DC[l,1]]**2)+\
            model.v_DC[model.A_DC[l,1]]*model.v_DC[model.A_DC[l,2]]*(model.B12[l]*sin(model.delta_DC[model.A_DC[l,1]]-\
            model.delta_DC[model.A_DC[l,2]])+model.G12[l]*cos(model.delta_DC[model.A_DC[l,1]]-model.delta_DC[model.A_DC[l,2]]))
        def KVL_real_toend(model,l):
            return model.pLto_DC[l] == model.G22[l]*(model.v_DC[model.A_DC[l,2]]**2)+\
            model.v_DC[model.A_DC[l,1]]*model.v_DC[model.A_DC[l,2]]*(model.B21[l]*sin(model.delta_DC[model.A_DC[l,2]]-\
            model.delta_DC[model.A_DC[l,1]])+model.G21[l]*cos(model.delta_DC[model.A_DC[l,2]]-model.delta_DC[model.A_DC[l,1]]))
        self.model.KVL_real_from     = Constraint(self.model.L_DC, rule=KVL_real_fromend)
        self.model.KVL_real_to       = Constraint(self.model.L_DC, rule=KVL_real_toend)
        
        # --- Kirchoff's voltage law on each transformer line ---
        def KVL_real_fromendTransf(model,l):
            return model.pLfromT_DC[l] == model.G11T[l]*(model.v_DC[model.AT_DC[l,1]]**2)+\
            model.v_DC[model.AT_DC[l,1]]*model.v_DC[model.AT_DC[l,2]]*(model.B12T[l]*sin(model.delta_DC[model.AT_DC[l,1]]-\
            model.delta_DC[model.AT_DC[l,2]])+model.G12T[l]*cos(model.delta_DC[model.AT_DC[l,1]]-model.delta_DC[model.AT_DC[l,2]]))
        def KVL_real_toendTransf(model,l):
            return model.pLtoT_DC[l] == model.G22T[l]*(model.v_DC[model.AT_DC[l,2]]**2)+\
            model.v_DC[model.AT_DC[l,1]]*model.v_DC[model.AT_DC[l,2]]*(model.B21T[l]*sin(model.delta_DC[model.AT_DC[l,2]]-\
            model.delta_DC[model.AT_DC[l,1]])+model.G21T[l]*cos(model.delta_DC[model.AT_DC[l,2]]-model.delta_DC[model.AT_DC[l,1]]))
        self.model.KVL_real_fromTransf     = Constraint(self.model.TRANSF_DC, rule=KVL_real_fromendTransf)
        self.model.KVL_real_toTransf       = Constraint(self.model.TRANSF_DC, rule=KVL_real_toendTransf)
        
        
        def voltage_to_constraint(model, l):
            return model.pLto_DC[l] == model.poles_DC[l] * (1/model.r_DC[l]) * model.v_DC[model.A_DC[l,1]] * (model.v_DC[model.A_DC[l,1]] - model.v_DC[model.A_DC[l,2]])
        self.model.V_to = Constraint(self.model.L_DC, rule=voltage_to_constraint)
        
        def voltage_from_constraint(model, l):
            return model.pLfrom_DC[l] == model.poles_DC[l] * (1/model.r_DC[l]) * model.v_DC[model.A_DC[l,2]] * (model.v_DC[model.A_DC[l,2]] - model.v_DC[model.A_DC[l,1]])
        self.model.V_from = Constraint(self.model.L_DC, rule=voltage_from_constraint)
        
        
        