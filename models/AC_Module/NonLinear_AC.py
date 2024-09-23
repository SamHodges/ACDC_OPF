from __future__ import division
from pyomo.environ import *
from models.AC_Module.AC_model import AC_model

class NonLinear_AC(AC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
         
    def extra_setup(self):
        self.model.QD_AC = Param(self.model.D_AC, within=Reals)  # reactive power demand
        self.model.QGmax_AC    = Param(self.model.G_AC, within=NonNegativeReals) # max reactive power of generator
        self.model.QGmin_AC    = Param(self.model.G_AC, within=Reals)            # min reactive power of generator
        self.model.WGQmax_AC   = Param(self.model.WIND_AC,  within=NonNegativeReals) # max reactive power of wind generator
        self.model.WGQmin_AC   = Param(self.model.WIND_AC,  within=Reals)            # min reactive power of wind generator
        self.model.GL_AC = Param(self.model.L_AC, within=Reals)
        self.model.BC_AC = Param(self.model.L_AC, within=Reals)
        
        
        #emergency ratings
        self.model.SLmax_E_AC = Param(self.model.L_AC, within=NonNegativeReals)       # max emergency real power flow limit
        self.model.SLmaxT_E_AC = Param(self.model.TRANSF_AC, within=NonNegativeReals) # max emergency real power flow limit

        #transformers
        self.model.Tap_AC          = Param(self.model.TRANSF_AC, within=NonNegativeReals)  # turns ratio of a transformer
        self.model.TapLB_AC        = Param(self.model.TRANSF_AC, within=NonNegativeReals)  # lower bound on turns ratio
        self.model.TapUB_AC        = Param(self.model.TRANSF_AC, within=NonNegativeReals)  # upper bound on turns ratio
        self.model.Deltashift_AC   = Param(self.model.TRANSF_AC) #  phase shift of transformer, rad
        self.model.DeltashiftLB_AC = Param(self.model.TRANSF_AC) #  lower bound on phase shift of transformer, rad
        self.model.DeltashiftUB_AC = Param(self.model.TRANSF_AC) #  upper bound on phase shift of transformer, rad
        self.model.GLT_AC    = Param(self.model.TRANSF_AC, within=Reals)
 
        # derived line parameters
        self.model.G11 = Param(self.model.L_AC, within=Reals)
        self.model.G12 = Param(self.model.L_AC, within=Reals)
        self.model.G21 = Param(self.model.L_AC, within=Reals)
        self.model.G22 = Param(self.model.L_AC, within=Reals)
        self.model.B11 = Param(self.model.L_AC, within=Reals)
        self.model.B12 = Param(self.model.L_AC, within=Reals)
        self.model.B21 = Param(self.model.L_AC, within=Reals)
        self.model.B22 = Param(self.model.L_AC, within=Reals)
        ## derived transformer parameters
        self.model.G11T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.G12T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.G21T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.G22T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.B11T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.B12T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.B21T = Param(self.model.TRANSF_AC, within=Reals)
        self.model.B22T = Param(self.model.TRANSF_AC, within=Reals)
        
         # buses
        self.model.Vmax_AC = Param(self.model.B_AC, within=NonNegativeReals) #  max voltage angle
        self.model.Vmin_AC = Param(self.model.B_AC, within=NonNegativeReals) #  min voltage angle

        self.model.qG_AC       = Var(self.model.G_AC, domain= Reals)# reactive power output of generator
        self.model.qW_AC       = Var(self.model.WIND_AC, domain= Reals) #reactive power generation from wind
        self.model.qD_AC       = Var(self.model.D_AC, domain= Reals)# reactive power absorbed by demand
        self.model.qLfrom_AC   = Var(self.model.L_AC, domain= Reals) # reactive power injected at b onto line
        self.model.qLto_AC     = Var(self.model.L_AC, domain= Reals) # reactive power injected at b' onto line
        self.model.qLfromT_AC  = Var(self.model.TRANSF_AC, domain= Reals) # reactive power injected at b onto transformer
        self.model.qLtoT_AC    = Var(self.model.TRANSF_AC, domain= Reals) # reactive power injected at b' onto transformer

        self.model.pLfrom_AC   = Var(self.model.L_AC, domain= Reals) # real power injected at b onto line
        self.model.pLto_AC     = Var(self.model.L_AC, domain= Reals) # real power injected at b' onto line
        self.model.pLfromT_AC  = Var(self.model.TRANSF_AC, domain= Reals) # real power injected at b onto transformer
        self.model.pLtoT_AC    = Var(self.model.TRANSF_AC, domain= Reals) # real power injected at b' onto transformer
        self.model.v_AC      = Var(self.model.B_AC, domain= NonNegativeReals, initialize=1.0) # voltage magnitude at bus b, rad

    def extra_constraints(self):
        # --- Kirchoff's current law at each bus b ---
        def KCL_real_def(model, b):
            return sum(model.pG_AC[g] for g in model.G_AC if (b,g) in model.Gbs_AC) +\
            sum(model.pW_AC[w] for w in model.WIND_AC if (b,w) in model.Wbs_AC)==\
            sum(model.pD_AC[d] for d in model.D_AC if (b,d) in model.Dbs_AC)+\
            sum(model.pLfrom_AC[l] for l in model.L_AC if model.A_AC[l,1]==b)+ \
            sum(model.pLto_AC[l] for l in model.L_AC if model.A_AC[l,2]==b)+\
            sum(model.pLfromT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,1]==b)+ \
            sum(model.pLtoT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,2]==b)+\
            sum(model.GB_AC[s]*model.v_AC[b]**2 for s in model.SHUNT_AC if (b,s) in model.SHUNTbs_AC)

        self.model.KCL_real     = Constraint(self.model.B_AC, rule=KCL_real_def)

        # --- Kirchoff's voltage law on each line ---
        def KVL_real_fromend(model,l):
            return model.pLfrom_AC[l] == model.G11[l]*(model.v_AC[model.A_AC[l,1]]**2)+\
            model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.B12[l]*sin(model.delta_AC[model.A_AC[l,1]]-\
            model.delta_AC[model.A_AC[l,2]])+model.G12[l]*cos(model.delta_AC[model.A_AC[l,1]]-model.delta_AC[model.A_AC[l,2]]))
        def KVL_real_toend(model,l):
            return model.pLto_AC[l] == model.G22[l]*(model.v_AC[model.A_AC[l,2]]**2)+\
            model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.B21[l]*sin(model.delta_AC[model.A_AC[l,2]]-\
            model.delta_AC[model.A_AC[l,1]])+model.G21[l]*cos(model.delta_AC[model.A_AC[l,2]]-model.delta_AC[model.A_AC[l,1]]))
        self.model.KVL_real_from     = Constraint(self.model.L_AC, rule=KVL_real_fromend)
        self.model.KVL_real_to       = Constraint(self.model.L_AC, rule=KVL_real_toend)

        # --- Kirchoff's voltage law on each transformer line ---
        def KVL_real_fromendTransf(model,l):
            return model.pLfromT_AC[l] == model.G11T[l]*(model.v_AC[model.AT_AC[l,1]]**2)+\
            model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.B12T[l]*sin(model.delta_AC[model.AT_AC[l,1]]-\
            model.delta_AC[model.AT_AC[l,2]])+model.G12T[l]*cos(model.delta_AC[model.AT_AC[l,1]]-model.delta_AC[model.AT_AC[l,2]]))
        def KVL_real_toendTransf(model,l):
            return model.pLtoT_AC[l] == model.G22T[l]*(model.v_AC[model.AT_AC[l,2]]**2)+\
            model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.B21T[l]*sin(model.delta_AC[model.AT_AC[l,2]]-\
            model.delta_AC[model.AT_AC[l,1]])+model.G21T[l]*cos(model.delta_AC[model.AT_AC[l,2]]-model.delta_AC[model.AT_AC[l,1]]))
        self.model.KVL_real_fromTransf     = Constraint(self.model.TRANSF_AC, rule=KVL_real_fromendTransf)
        self.model.KVL_real_toTransf       = Constraint(self.model.TRANSF_AC, rule=KVL_real_toendTransf)

        def KCL_reactive_def(model, b):
            return sum(model.qG_AC[g] for g in model.G_AC if (b,g) in model.Gbs_AC) +\
            sum(model.qW_AC[w] for w in model.WIND_AC if (b,w) in model.Wbs_AC)== \
            sum(model.qD_AC[d] for d in model.D_AC if (b,d) in model.Dbs_AC)+\
            sum(model.qLfrom_AC[l] for l in model.L_AC if model.A_AC[l,1]==b)+ \
            sum(model.qLto_AC[l] for l in model.L_AC if model.A_AC[l,2]==b)+\
            sum(model.qLfromT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,1]==b)+ \
            sum(model.qLtoT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,2]==b)-\
            sum(model.BB_AC[s]*model.v_AC[b]**2 for s in model.SHUNT_AC if (b,s) in model.SHUNTbs_AC)
        self.model.KCL_reactive = Constraint(self.model.B_AC, rule=KCL_reactive_def)
    
        def KVL_reactive_fromend(model,l):
            return model.qLfrom_AC[l] == -model.B11[l]*(model.v_AC[model.A_AC[l,1]]**2)+\
            model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.G12[l]*sin(model.delta_AC[model.A_AC[l,1]]-\
            model.delta_AC[model.A_AC[l,2]])-model.B12[l]*cos(model.delta_AC[model.A_AC[l,1]]-model.delta_AC[model.A_AC[l,2]]))
        def KVL_reactive_toend(model,l):
            return model.qLto_AC[l] == (-model.B22[l]*(model.v_AC[model.A_AC[l,2]]**2)+\
            model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.G21[l]*sin(model.delta_AC[model.A_AC[l,2]]-\
            model.delta_AC[model.A_AC[l,1]])-model.B21[l]*cos(model.delta_AC[model.A_AC[l,2]]-model.delta_AC[model.A_AC[l,1]])))
        self.model.KVL_reactive_from = Constraint(self.model.L_AC, rule=KVL_reactive_fromend)
        self.model.KVL_reactive_to   = Constraint(self.model.L_AC, rule=KVL_reactive_toend)
        
        def KVL_reactive_fromendTransf(model,l):
            return model.qLfromT_AC[l] == -model.B11T[l]*(model.v_AC[model.AT_AC[l,1]]**2)+\
            model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.G12T[l]*sin(model.delta_AC[model.AT_AC[l,1]]-\
            model.delta_AC[model.AT_AC[l,2]])-model.B12T[l]*cos(model.delta_AC[model.AT_AC[l,1]]-model.delta_AC[model.AT_AC[l,2]]))
        def KVL_reactive_toendTransf(model,l):
            return model.qLtoT_AC[l] == -model.B22T[l]*(model.v_AC[model.AT_AC[l,2]]**2)+\
            model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.G21T[l]*sin(model.delta_AC[model.AT_AC[l,2]]-\
        model.delta_AC[model.AT_AC[l,1]])-model.B21T[l]*cos(model.delta_AC[model.AT_AC[l,2]]-model.delta_AC[model.AT_AC[l,1]]))
        self.model.KVL_reactive_fromTransf = Constraint(self.model.TRANSF_AC, rule=KVL_reactive_fromendTransf)
        self.model.KVL_reactive_toTransf   = Constraint(self.model.TRANSF_AC, rule=KVL_reactive_toendTransf)
        
        def Reactive_Power_Max(model,g):
            return model.qG_AC[g] <= model.QGmax_AC[g]
        def Reactive_Power_Min(model,g):
            return model.qG_AC[g] >= model.QGmin_AC[g]
        self.model.QGmaxC = Constraint(self.model.G_AC, rule=Reactive_Power_Max)
        self.model.QGminC = Constraint(self.model.G_AC, rule=Reactive_Power_Min)
        
        def Wind_Reactive_Power_Max(model,w):
            return model.qW_AC[w] <= model.WGQmax_AC[w]
        def Wind_Reactive_Power_Min(model,w):
            return model.qW_AC[w] >= model.WGQmin_AC[w]
        self.model.WGQmaxC = Constraint(self.model.WIND_AC, rule=Wind_Reactive_Power_Max)
        self.model.WGQminC = Constraint(self.model.WIND_AC, rule=Wind_Reactive_Power_Min)

        def Load_Shed_reactive(model,d):
            return model.qD_AC[d] == model.alpha_AC[d]*model.QD_AC[d]
        self.model.LoadShed_reactive = Constraint(self.model.D_AC, rule=Load_Shed_reactive)
        
        # --- demand and load shedding ---
        def Load_Shed_real(model,d):
            return model.pD_AC[d] == model.alpha_AC[d]*model.PD_AC[d]
        def alpha_FixNegDemands(model,d):
            return model.alpha_AC[d] == 1
        self.model.LoadShed_real     = Constraint(self.model.D_AC, rule=Load_Shed_real)
        self.model.alphaFix          = Constraint(self.model.DNeg_AC, rule=alpha_FixNegDemands)
        
        def alpha_BoundLB(model,d):
            return model.alpha_AC[d] >= 0
        self.model.alphaBoundLBC = Constraint(self.model.D_AC, rule=alpha_BoundLB)
        
        # --- line power limits ---
        def line_lim1_def(model,l):
            return model.pLfrom_AC[l]**2+model.qLfrom_AC[l]**2 <= model.SLmax_AC[l]**2
        def line_lim2_def(model,l):
            return model.pLto_AC[l]**2+model.qLto_AC[l]**2 <= model.SLmax_AC[l]**2
        self.model.line_lim1_AC = Constraint(self.model.L_AC, rule=line_lim1_def)
        self.model.line_lim2_AC = Constraint(self.model.L_AC, rule=line_lim2_def)
        
        # --- power flow limits on transformer lines---
        def transf_lim1_def(model,l):
            return model.pLfromT_AC[l]**2+model.qLfromT_AC[l]**2 <= model.SLmaxT_AC[l]**2
        def transf_lim2_def(model,l):
            return model.pLtoT_AC[l]**2+model.qLtoT_AC[l]**2 <= model.SLmaxT_AC[l]**2
        self.model.transf_lim1_AC = Constraint(self.model.TRANSF_AC, rule=transf_lim1_def)
        self.model.transf_lim2_AC = Constraint(self.model.TRANSF_AC, rule=transf_lim2_def)
        
        # --- voltage constraints ---
        def bus_max_voltage(model,b):
            return model.v_AC[b] <= model.Vmax_AC[b]
        def bus_min_voltage(model,b):
            return model.v_AC[b] >= model.Vmin_AC[b]
        self.model.Vmaxc = Constraint(self.model.B_AC, rule=bus_max_voltage)
        self.model.Vminc = Constraint(self.model.B_AC, rule=bus_min_voltage)
