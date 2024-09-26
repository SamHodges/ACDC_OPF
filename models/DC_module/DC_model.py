from __future__ import division
from pyomo.environ import *

class DC_model:
    def __init__(self, solver, testcase, model):
         self.solver = solver
         self.testcase = testcase
         self.model = model
         
    def create_dc_opf(self):
        self.basic_setup()
        self.extra_setup()
        self.basic_constraints()
        self.extra_constraints()
        
    def basic_setup(self):
        self.model.B_DC      = Set()  # set of buses
        self.model.G_DC      = Set()  # set of generators
        self.model.WIND_DC   = Set()  # set of wind generators
        self.model.D_DC      = Set()  # set of demands
        self.model.DNeg_DC   = Set()  # set of demands
        self.model.L_DC      = Set()  # set of lines
        self.model.SHUNT_DC  = Set()  # set of shunts
        self.model.LE_DC     = Set()  # line-to and from ends set (1,2)
        self.model.TRANSF_DC = Set()  # set of transformers
        self.model.b0_DC     = Set(within=self.model.B_DC)  # set of reference buses

        # generators, buses, loads linked to eDCh bus b
        self.model.Gbs_DC = Set(within=self.model.B_DC * self.model.G_DC)    # generator-bus mapping
        self.model.Dbs_DC = Set(within=self.model.B_DC * self.model.D_DC)    # demand-bus mapping
        self.model.Wbs_DC = Set(within=self.model.B_DC * self.model.WIND_DC) # wind-bus mapping
        self.model.SHUNTbs_DC = Set(within=self.model.B_DC * self.model.SHUNT_DC)# shunt-bus mapping
        
        # --- parameters ---
        # line matrix
        self.model.A_DC = Param(self.model.L_DC*self.model.LE_DC,within=Any)       # bus-line
        self.model.AT_DC = Param(self.model.TRANSF_DC*self.model.LE_DC,within=Any) # bus-transformer

        # demands
        self.model.PD_DC = Param(self.model.D_DC, within=Reals)  # real power demand
        self.model.VOLL_DC    = Param(self.model.D_DC, within=Reals) #value of lost load

        # generators
        self.model.PGmax_DC    = Param(self.model.G_DC, within=NonNegativeReals) # max real power of generator
        self.model.PGmin_DC    = Param(self.model.G_DC, within=Reals)            # min real power of generator
        
        #wind generators
        self.model.WGmax_DC    = Param(self.model.WIND_DC,  within=NonNegativeReals) # max real power of wind generator
        self.model.WGmin_DC    = Param(self.model.WIND_DC,  within=NonNegativeReals) # min real power of wind generator
        
        # lines
        self.model.SLmax_DC = Param(self.model.L_DC, within=NonNegativeReals) # max real power limit on flow in a line
        self.model.BL_DC = Param(self.model.L_DC, within=Reals)
        self.model.SLmaxT_DC = Param(self.model.TRANSF_DC, within=NonNegativeReals) # max real power flow limit
        self.model.BLT_DC    = Param(self.model.TRANSF_DC, within=Reals)

        #shunt
        self.model.GB_DC = Param(self.model.SHUNT_DC, within=Reals) #  shunt conductance
        self.model.BB_DC = Param(self.model.SHUNT_DC, within=Reals) #  shunt susceptance

        # cost
        self.model.c2_DC = Param(self.model.G_DC, within=NonNegativeReals)# generator cost coefficient c2 (*pG^2)
        self.model.c1_DC = Param(self.model.G_DC, within=NonNegativeReals)# generator cost coefficient c1 (*pG)
        self.model.c0_DC = Param(self.model.G_DC, within=NonNegativeReals)# generator cost coefficient c0
        self.model.baseMVA_DC = Param(within=NonNegativeReals)# base MVA

        #constants
        self.model.eps_DC = Param(within=NonNegativeReals)

        # --- variables ---
        self.model.pG_DC       = Var(self.model.G_DC, domain= NonNegativeReals)# real power output of generator
        self.model.pW_DC       = Var(self.model.WIND_DC, domain= Reals) #real power generation from wind
        self.model.pD_DC       = Var(self.model.D_DC, domain= Reals)# real power absorbed by demand
        self.model.alpha_DC  = Var(self.model.D_DC, initialize=1.0, domain= NonNegativeReals)# proportion to supply of load d
        self.model.delta_DC  = Var(self.model.B_DC, domain= Reals, initialize=0.0) # voltage phase angle at bus b, rad


    def extra_setup(self):
        pass
            
    def basic_constraints(self):   
        # --- demand model ---
        def demand_model(model,d):
            return model.pD_DC[d] == model.alpha_DC[d]*model.PD_DC[d]
        def demand_LS_bound_Max(model,d):
            return model.alpha_DC[d] <= 1
        self.model.demandmodelC_DC = Constraint(self.model.D_DC, rule=demand_model)
        self.model.demandalphaC_DC = Constraint(self.model.D_DC, rule=demand_LS_bound_Max)

        # --- generator power limits ---
        def Real_Power_Max(model,g):
            return model.pG_DC[g] <= model.PGmax_DC[g]
        def Real_Power_Min(model,g):
            return model.pG_DC[g] >= model.PGmin_DC[g]
        self.model.PGmaxC_DC = Constraint(self.model.G_DC, rule=Real_Power_Max)
        self.model.PGminC_DC = Constraint(self.model.G_DC, rule=Real_Power_Min)

        # ---wind generator power limits ---
        def Wind_Real_Power_Max(model,w):
            return model.pW_DC[w] <= model.WGmax_DC[w]
        def Wind_Real_Power_Min(model,w):
            return model.pW_DC[w] >= model.WGmin_DC[w]
        self.model.WGmaxC_DC  = Constraint(self.model.WIND_DC, rule=Wind_Real_Power_Max)
        self.model.WGminC_DC  = Constraint(self.model.WIND_DC, rule=Wind_Real_Power_Min)

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

        # --- reference bus constraint ---
        def ref_bus_def(model,b):
            return model.delta_DC[b]==0
        self.model.refbus_DC = Constraint(self.model.b0_DC, rule=ref_bus_def)
     
    def extra_constraints(self):
        pass