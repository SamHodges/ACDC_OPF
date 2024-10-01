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
        self.model.L_DC      = Set()  # set of lines
        self.model.SHUNT_DC  = Set()  # set of shunts
        self.model.LE_DC     = Set()  # line-to and from ends set (1,2)
        self.model.TRANSF_DC = Set()  # set of transformers
        self.model.b0_DC     = Set(within=self.model.B_DC)  # set of reference buses

        # generators, buses, loads linked to eDCh bus b
        self.model.Gbs_DC = Set(within=self.model.B_DC * self.model.G_DC)    # generator-bus mapping
        self.model.Wbs_DC = Set(within=self.model.B_DC * self.model.WIND_DC) # wind-bus mapping
        self.model.SHUNTbs_DC = Set(within=self.model.B_DC * self.model.SHUNT_DC)# shunt-bus mapping
        
        # --- parameters ---
        # line matrix
        self.model.A_DC = Param(self.model.L_DC*self.model.LE_DC,within=Any)       # bus-line
        self.model.AT_DC = Param(self.model.TRANSF_DC*self.model.LE_DC,within=Any) # bus-transformer


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
        self.model.delta_DC  = Var(self.model.B_DC, domain= Reals, initialize=0.0) # voltage phase angle at bus b, rad


    def extra_setup(self):
        pass
            
    def basic_constraints(self):   

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

        # --- reference bus constraint ---
        def ref_bus_def(model,b):
            return model.delta_DC[b]==0
        self.model.refbus_DC = Constraint(self.model.b0_DC, rule=ref_bus_def)
     
    def extra_constraints(self):
        pass