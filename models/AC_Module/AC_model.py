from __future__ import division
from pyomo.environ import *

class AC_model:
    def __init__(self, solver, testcase, model):
         self.solver = solver
         self.testcase = testcase
         self.model = model
         
    def create_ac_opf(self):
        self.basic_setup()
        self.extra_setup()
        self.basic_constraints()
        self.extra_constraints()
        
    def basic_setup(self):
        self.model.B_AC      = Set()  # set of buses
        self.model.G_AC      = Set()  # set of generators
        self.model.WIND_AC   = Set()  # set of wind generators
        self.model.D_AC      = Set()  # set of demands
        self.model.DNeg_AC   = Set()  # set of demands
        self.model.L_AC      = Set()  # set of lines
        self.model.SHUNT_AC  = Set()  # set of shunts
        self.model.LE_AC     = Set()  # line-to and from ends set (1,2)
        self.model.TRANSF_AC = Set()  # set of transformers
        self.model.b0_AC     = Set(within=self.model.B_AC)  # set of reference buses

        # generators, buses, loads linked to each bus b
        self.model.Gbs_AC = Set(within=self.model.B_AC * self.model.G_AC)    # generator-bus mapping
        self.model.Dbs_AC = Set(within=self.model.B_AC * self.model.D_AC)    # demand-bus mapping
        self.model.Wbs_AC = Set(within=self.model.B_AC * self.model.WIND_AC) # wind-bus mapping
        self.model.SHUNTbs_AC = Set(within=self.model.B_AC * self.model.SHUNT_AC)# shunt-bus mapping
        
        # --- parameters ---
        # line matrix
        self.model.A_AC = Param(self.model.L_AC*self.model.LE_AC,within=Any)       # bus-line
        self.model.AT_AC = Param(self.model.TRANSF_AC*self.model.LE_AC,within=Any) # bus-transformer

        # demands
        self.model.PD_AC = Param(self.model.D_AC, within=Reals)  # real power demand
        self.model.VOLL_AC    = Param(self.model.D_AC, within=Reals) #value of lost load

        # generators
        self.model.PGmax_AC    = Param(self.model.G_AC, within=NonNegativeReals) # max real power of generator
        self.model.PGmin_AC    = Param(self.model.G_AC, within=Reals)            # min real power of generator
        
        #wind generators
        self.model.WGmax_AC    = Param(self.model.WIND_AC,  within=NonNegativeReals) # max real power of wind generator
        self.model.WGmin_AC    = Param(self.model.WIND_AC,  within=NonNegativeReals) # min real power of wind generator
        
        # lines
        self.model.SLmax_AC = Param(self.model.L_AC, within=NonNegativeReals) # max real power limit on flow in a line
        self.model.BL_AC = Param(self.model.L_AC, within=Reals)
        self.model.SLmaxT_AC = Param(self.model.TRANSF_AC, within=NonNegativeReals) # max real power flow limit
        self.model.BLT_AC    = Param(self.model.TRANSF_AC, within=Reals)

        #shunt
        self.model.GB_AC = Param(self.model.SHUNT_AC, within=Reals) #  shunt conductance
        self.model.BB_AC = Param(self.model.SHUNT_AC, within=Reals) #  shunt susceptance

        # cost
        self.model.c2_AC = Param(self.model.G_AC, within=NonNegativeReals)# generator cost coefficient c2 (*pG^2)
        self.model.c1_AC = Param(self.model.G_AC, within=NonNegativeReals)# generator cost coefficient c1 (*pG)
        self.model.c0_AC = Param(self.model.G_AC, within=NonNegativeReals)# generator cost coefficient c0
        self.model.baseMVA_AC = Param(within=NonNegativeReals)# base MVA

        #constants
        self.model.eps_AC = Param(within=NonNegativeReals)

        # --- variables ---
        self.model.pG_AC       = Var(self.model.G_AC, domain= NonNegativeReals)# real power output of generator
        self.model.pW_AC       = Var(self.model.WIND_AC, domain= Reals) #real power generation from wind
        self.model.pD_AC       = Var(self.model.D_AC, domain= Reals)# real power absorbed by demand
        self.model.delta_AC  = Var(self.model.B_AC, domain= Reals, initialize=0.0) # voltage phase angle at bus b, rad
        self.model.alpha_AC  = Var(self.model.D_AC, initialize=1.0, domain= NonNegativeReals)# proportion to supply of load d

    def extra_setup(self):
        pass
            
    def basic_constraints(self):
        # --- generator power limits ---
        def Real_Power_Max(model,g):
            return model.pG_AC[g] <= model.PGmax_AC[g]
        def Real_Power_Min(model,g):
            return model.pG_AC[g] >= model.PGmin_AC[g]
        self.model.PGmaxC_AC = Constraint(self.model.G_AC, rule=Real_Power_Max)
        self.model.PGminC_AC = Constraint(self.model.G_AC, rule=Real_Power_Min)

        # ---wind generator power limits ---
        def Wind_Real_Power_Max(model,w):
            return model.pW_AC[w] <= model.WGmax_AC[w]
        def Wind_Real_Power_Min(model,w):
            return model.pW_AC[w] >= model.WGmin_AC[w]
        self.model.WGmaxC_AC  = Constraint(self.model.WIND_AC, rule=Wind_Real_Power_Max)
        self.model.WGminC_AC  = Constraint(self.model.WIND_AC, rule=Wind_Real_Power_Min)

        def alpha_BoundUB(model,d):
            return model.alpha_AC[d] <= 1
        self.model.alphaBoundUBC = Constraint(self.model.D_AC, rule=alpha_BoundUB)
        
        # --- reference bus constraint ---
        def ref_bus_def(model,b):
            return model.delta_AC[b]==0
        self.model.refbus = Constraint(self.model.b0_AC, rule=ref_bus_def)

        
    def extra_constraints():
        pass