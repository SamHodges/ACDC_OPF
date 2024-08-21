#==================================================================
# ACOPF.mod
# PYOMO model file of "AC" optimal power flow problem (ACOPF)
# ---Author---
# W. Bukhsh,
# wbukhsh@gmail.com
# OATS
# Copyright (c) 2015 by W Bukhsh, Glasgow, Scotland
# OATS is distributed under the GNU GENERAL PUBLIC LICENSE license. (see LICENSE file for details).
#==========Import==========
from __future__ import division
from pyomo.environ import *
#==========================

model = AbstractModel()
# --- sets ---
# buses, generators, loads, lines, sections
# model.ACDC_Links   = Set(dimen=2)  # set of HVDC

# model.B_AC      = Set()  # set of buses
# model.G_AC      = Set()  # set of generators
# model.HVDC_Pairs   = Set(dimen=2)  # set of HVDC
# model.HVDC_CONV = Set(within=model.G_AC)
# model.WIND_AC   = Set()  # set of wind generators
# model.D_AC      = Set()  # set of demands
# model.DNeg_AC   = Set()  # set of demands
# model.L_AC      = Set()  # set of lines
# model.SHUNT_AC  = Set()  # set of shunts
# model.LE_AC     = Set()  # line-to and from ends set (1,2)
# model.TRANSF_AC = Set()  # set of transformers
# model.b0_AC     = Set(within=model.B_AC)  # set of reference buses

model.B_DC      = Set()  # set of buses
model.G_DC      = Set()  # set of generators
model.WIND_DC   = Set()  # set of wind generators
model.D_DC      = Set()  # set of demands
model.DNeg_DC   = Set()  # set of demands
model.L_DC      = Set()  # set of lines
model.SHUNT_DC  = Set()  # set of shunts
model.b0_DC     = Set(within=model.B_DC)  # set of reference buses
model.LE_DC     = Set()  # line-to and from ends set (1,2)
model.TRANSF_DC = Set()  # set of transformers

# generators, buses, loads linked to each bus b
# model.Gbs_AC = Set(within=model.B_AC * model.G_AC)    # generator-bus mapping
# model.Dbs_AC = Set(within=model.B_AC * model.D_AC)    # demand-bus mapping
# model.Wbs_AC = Set(within=model.B_AC * model.WIND_AC) # wind-bus mapping
# model.SHUNTbs_AC = Set(within=model.B_AC * model.SHUNT_AC)# shunt-bus mapping

model.Gbs_DC     = Set(within=model.B_DC * model.G_DC)    # set of generator-bus mapping
model.Wbs_DC     = Set(within=model.B_DC * model.WIND_DC) # set of wind-bus mapping
model.Dbs_DC     = Set(within=model.B_DC * model.D_DC)    # set of demand-bus mapping
model.SHUNTbs_DC = Set(within=model.B_DC*model.SHUNT_DC)  # set of shunt-bus mapping

# --- parameters ---
# line matrix
# model.A_AC = Param(model.L_AC*model.LE_AC,within=Any)       # bus-line
# model.AT_AC = Param(model.TRANSF_AC*model.LE_AC,within=Any) # bus-transformer

model.A_DC     = Param(model.L_DC*model.LE_DC)       # bus-line matrix
model.AT_DC    = Param(model.TRANSF_DC*model.LE_DC)  # bus-transformer matrix

# demands
# model.PD_AC = Param(model.D_AC, within=Reals)  # real power demand
# model.QD_AC = Param(model.D_AC, within=Reals)  # reactive power demand
# model.VOLL_AC    = Param(model.D_AC, within=Reals) #value of lost load

model.PD_DC      = Param(model.D_DC, within=Reals)  # real power demand
model.VOLL_DC    = Param(model.D_DC, within=Reals)  # value of lost load

# generators
# model.PGmax_AC    = Param(model.G_AC, within=NonNegativeReals) # max real power of generator
# model.PGmin_AC    = Param(model.G_AC, within=Reals)            # min real power of generator
# model.QGmax_AC    = Param(model.G_AC, within=NonNegativeReals) # max reactive power of generator
# model.QGmin_AC    = Param(model.G_AC, within=Reals)            # min reactive power of generator

model.PGmax_DC    = Param(model.G_DC, within=NonNegativeReals) # max real power of generator, p.u.
model.PGmin_DC    = Param(model.G_DC, within=Reals)            # min real power of generator, p.u.
model.PG_DC       = Param(model.G_DC, within=Reals) # FPN
model.WGmax_DC    = Param(model.WIND_DC, within=NonNegativeReals) # max real power of wind generator, p.u.
model.WGmin_DC    = Param(model.WIND_DC, within=NonNegativeReals) # min real power of wind generator, 

#wind generators
# model.WGmax_AC    = Param(model.WIND_AC,  within=NonNegativeReals) # max real power of wind generator
# model.WGmin_AC    = Param(model.WIND_AC,  within=NonNegativeReals) # min real power of wind generator
# model.WGQmax_AC   = Param(model.WIND_AC,  within=NonNegativeReals) # max reactive power of wind generator
# model.WGQmin_AC   = Param(model.WIND_AC,  within=Reals)            # min reactive power of wind generator

# lines
# model.SLmax_AC = Param(model.L_AC, within=NonNegativeReals) # max real power limit on flow in a line
# model.GL_AC = Param(model.L_AC, within=Reals)
# model.BL_AC = Param(model.L_AC, within=Reals)
# model.BC_AC = Param(model.L_AC, within=Reals)

model.SLmax_DC  = Param(model.L_DC, within=NonNegativeReals)      # real power line limit
model.SLmaxT_DC = Param(model.TRANSF_DC, within=NonNegativeReals) # real power transformer limit
model.BL_DC     = Param(model.L_DC, within=Reals)       # susceptance of a line
model.BLT_DC    = Param(model.TRANSF_DC, within=Reals)  # susceptance of a transformer

#emergency ratings
# model.SLmax_E_AC = Param(model.L_AC, within=NonNegativeReals)       # max emergency real power flow limit
# model.SLmaxT_E_AC = Param(model.TRANSF_AC, within=NonNegativeReals) # max emergency real power flow limit

#transformers
# model.Tap_AC          = Param(model.TRANSF_AC, within=NonNegativeReals)  # turns ratio of a transformer
# model.TapLB_AC        = Param(model.TRANSF_AC, within=NonNegativeReals)  # lower bound on turns ratio
# model.TapUB_AC        = Param(model.TRANSF_AC, within=NonNegativeReals)  # upper bound on turns ratio
# model.Deltashift_AC   = Param(model.TRANSF_AC) #  phase shift of transformer, rad
# model.DeltashiftLB_AC = Param(model.TRANSF_AC) #  lower bound on phase shift of transformer, rad
# model.DeltashiftUB_AC = Param(model.TRANSF_AC) #  upper bound on phase shift of transformer, rad

# model.SLmaxT_AC = Param(model.TRANSF_AC, within=NonNegativeReals) # max real power flow limit
# model.GLT_AC    = Param(model.TRANSF_AC, within=Reals)
# model.BLT_AC    = Param(model.TRANSF_AC, within=Reals)

# derived line parameters
# model.G11 = Param(model.L_AC, within=Reals)
# model.G12 = Param(model.L_AC, within=Reals)
# model.G21 = Param(model.L_AC, within=Reals)
# model.G22 = Param(model.L_AC, within=Reals)
# model.B11 = Param(model.L_AC, within=Reals)
# model.B12 = Param(model.L_AC, within=Reals)
# model.B21 = Param(model.L_AC, within=Reals)
# model.B22 = Param(model.L_AC, within=Reals)
# ## derived transformer parameters
# model.G11T = Param(model.TRANSF_AC, within=Reals)
# model.G12T = Param(model.TRANSF_AC, within=Reals)
# model.G21T = Param(model.TRANSF_AC, within=Reals)
# model.G22T = Param(model.TRANSF_AC, within=Reals)
# model.B11T = Param(model.TRANSF_AC, within=Reals)
# model.B12T = Param(model.TRANSF_AC, within=Reals)
# model.B21T = Param(model.TRANSF_AC, within=Reals)
# model.B22T = Param(model.TRANSF_AC, within=Reals)

# buses
# model.Vmax_AC = Param(model.B_AC, within=NonNegativeReals) #  max voltage angle
# model.Vmin_AC = Param(model.B_AC, within=NonNegativeReals) #  min voltage angle

# #shunt
# model.GB_AC = Param(model.SHUNT_AC, within=Reals) #  shunt conductance
# model.BB_AC = Param(model.SHUNT_AC, within=Reals) #  shunt susceptance

model.GB_DC = Param(model.SHUNT_DC, within=Reals) #  shunt conductance
model.BB_DC = Param(model.SHUNT_DC, within=Reals) #  shunt susceptance

# cost
# model.c2_AC = Param(model.G_AC, within=NonNegativeReals)# generator cost coefficient c2 (*pG^2)
# model.c1_AC = Param(model.G_AC, within=NonNegativeReals)# generator cost coefficient c1 (*pG)
# model.c0_AC = Param(model.G_AC, within=NonNegativeReals)# generator cost coefficient c0

# model.baseMVA_AC = Param(within=NonNegativeReals)# base MVA

model.c2_DC    = Param(model.G_DC, within=NonNegativeReals)# generator cost coefficient c2 (*pG^2)
model.c1_DC    = Param(model.G_DC, within=NonNegativeReals)# generator cost coefficient c1 (*pG)
model.c0_DC    = Param(model.G_DC, within=NonNegativeReals)# generator cost coefficient c0

model.baseMVA_DC = Param(within=NonNegativeReals)# base MVA


#constants
# model.eps_AC = Param(within=NonNegativeReals)
model.eps_DC = Param(within=NonNegativeReals)

# --- variables ---
# model.pG_AC       = Var(model.G_AC, domain= NonNegativeReals)# real power output of generator
# model.qG_AC       = Var(model.G_AC, domain= Reals)# reactive power output of generator
# model.pW_AC       = Var(model.WIND_AC, domain= Reals) #real power generation from wind
# model.qW_AC       = Var(model.WIND_AC, domain= Reals) #reactive power generation from wind
# model.pD_AC       = Var(model.D_AC, domain= Reals)# real power absorbed by demand
# model.qD_AC       = Var(model.D_AC, domain= Reals)# reactive power absorbed by demand
# model.pLfrom_AC   = Var(model.L_AC, domain= Reals) # real power injected at b onto line
# model.pLto_AC     = Var(model.L_AC, domain= Reals) # real power injected at b' onto line
# model.qLfrom_AC   = Var(model.L_AC, domain= Reals) # reactive power injected at b onto line
# model.qLto_AC     = Var(model.L_AC, domain= Reals) # reactive power injected at b' onto line
# model.pLfromT_AC  = Var(model.TRANSF_AC, domain= Reals) # real power injected at b onto transformer
# model.pLtoT_AC    = Var(model.TRANSF_AC, domain= Reals) # real power injected at b' onto transformer
# model.qLfromT_AC  = Var(model.TRANSF_AC, domain= Reals) # reactive power injected at b onto transformer
# model.qLtoT_AC    = Var(model.TRANSF_AC, domain= Reals) # reactive power injected at b' onto transformer

model.pG_DC    = Var(model.G_DC,  domain= Reals)  #real power generation
model.pW_DC    = Var(model.WIND_DC, domain= Reals) #real power generation from wind
model.pD_DC    = Var(model.D_DC, domain= Reals) #real power demand delivered
model.alpha_DC = Var(model.D_DC, domain= NonNegativeReals) #propotion of real power demand delivered
model.deltaL_DC  = Var(model.L_DC, domain= Reals)      # angle difference across lines
model.deltaLT_DC = Var(model.TRANSF_DC, domain= Reals) # angle difference across transformers
model.delta_DC   = Var(model.B_DC, domain= Reals, initialize=0.0) # voltage phase angle at bus b, rad
model.pL_DC      = Var(model.L_DC, domain= Reals) # real power injected at b onto line l, p.u.
model.pLT_DC     = Var(model.TRANSF_DC, domain= Reals) # real power injected at b onto transformer line l, 

#model.deltaL = Var(model.L, domain= Reals) # angle difference across lines
# model.delta_AC  = Var(model.B_AC, domain= Reals, initialize=0.0) # voltage phase angle at bus b, rad
# model.v_AC      = Var(model.B_AC, domain= NonNegativeReals, initialize=1.0) # voltage magnitude at bus b, rad
# model.alpha_AC  = Var(model.D_AC, initialize=1.0, domain= NonNegativeReals)# proportion to supply of load d

# --- cost function ---
def objective(model):
    # obj = sum(model.c2_AC[g]*(model.baseMVA_AC*model.pG_AC[g])**2+model.c1_AC[g]*model.baseMVA_AC*model.pG_AC[g]+ model.c0_AC[g] for g in model.G_AC)+\
    # sum(model.VOLL_AC[d]*(1-model.alpha_AC[d])*model.baseMVA_AC*model.PD_AC[d] for d in model.D_AC) +\
    obj = sum(model.c1_DC[g]*(model.baseMVA_DC*model.pG_DC[g])+model.c0_DC[g] for g in model.G_DC) +\
    sum(model.VOLL_DC[d]*(1-model.alpha_DC[d])*model.baseMVA_DC*model.PD_DC[d] for d in model.D_DC)
    return obj
model.OBJ = Objective(rule=objective, sense=minimize)

# --- Kirchoff's current law at each bus b ---
# def KCL_real_def(model, b):
#     return sum(model.pG_AC[g] for g in model.G_AC if (b,g) in model.Gbs_AC) +\
#     sum(model.pW_AC[w] for w in model.WIND_AC if (b,w) in model.Wbs_AC)==\
#     sum(model.pD_AC[d] for d in model.D_AC if (b,d) in model.Dbs_AC)+\
#     sum(model.pLfrom_AC[l] for l in model.L_AC if model.A_AC[l,1]==b)+ \
#     sum(model.pLto_AC[l] for l in model.L_AC if model.A_AC[l,2]==b)+\
#     sum(model.pLfromT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,1]==b)+ \
#     sum(model.pLtoT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,2]==b)+\
#     sum(model.GB_AC[s]*model.v_AC[b]**2 for s in model.SHUNT_AC if (b,s) in model.SHUNTbs_AC)
# def KCL_reactive_def(model, b):
#     return sum(model.qG_AC[g] for g in model.G_AC if (b,g) in model.Gbs_AC) +\
#     sum(model.qW_AC[w] for w in model.WIND_AC if (b,w) in model.Wbs_AC)== \
#     sum(model.qD_AC[d] for d in model.D_AC if (b,d) in model.Dbs_AC)+\
#     sum(model.qLfrom_AC[l] for l in model.L_AC if model.A_AC[l,1]==b)+ \
#     sum(model.qLto_AC[l] for l in model.L_AC if model.A_AC[l,2]==b)+\
#     sum(model.qLfromT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,1]==b)+ \
#     sum(model.qLtoT_AC[l] for l in model.TRANSF_AC if model.AT_AC[l,2]==b)-\
#     sum(model.BB_AC[s]*model.v_AC[b]**2 for s in model.SHUNT_AC if (b,s) in model.SHUNTbs_AC)
# model.KCL_real     = Constraint(model.B_AC, rule=KCL_real_def)
# model.KCL_reactive = Constraint(model.B_AC, rule=KCL_reactive_def)

# --- Kirchoff's voltage law on each line ---
# def KVL_real_fromend(model,l):
#     return model.pLfrom_AC[l] == model.G11[l]*(model.v_AC[model.A_AC[l,1]]**2)+\
#     model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.B12[l]*sin(model.delta_AC[model.A_AC[l,1]]-\
#     model.delta_AC[model.A_AC[l,2]])+model.G12[l]*cos(model.delta_AC[model.A_AC[l,1]]-model.delta_AC[model.A_AC[l,2]]))
# def KVL_real_toend(model,l):
#     return model.pLto_AC[l] == model.G22[l]*(model.v_AC[model.A_AC[l,2]]**2)+\
#     model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.B21[l]*sin(model.delta_AC[model.A_AC[l,2]]-\
#     model.delta_AC[model.A_AC[l,1]])+model.G21[l]*cos(model.delta_AC[model.A_AC[l,2]]-model.delta_AC[model.A_AC[l,1]]))
# def KVL_reactive_fromend(model,l):
#     return model.qLfrom_AC[l] == -model.B11[l]*(model.v_AC[model.A_AC[l,1]]**2)+\
#     model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.G12[l]*sin(model.delta_AC[model.A_AC[l,1]]-\
#     model.delta_AC[model.A_AC[l,2]])-model.B12[l]*cos(model.delta_AC[model.A_AC[l,1]]-model.delta_AC[model.A_AC[l,2]]))
# def KVL_reactive_toend(model,l):
#     return model.qLto_AC[l] == (-model.B22[l]*(model.v_AC[model.A_AC[l,2]]**2)+\
#     model.v_AC[model.A_AC[l,1]]*model.v_AC[model.A_AC[l,2]]*(model.G21[l]*sin(model.delta_AC[model.A_AC[l,2]]-\
#     model.delta_AC[model.A_AC[l,1]])-model.B21[l]*cos(model.delta_AC[model.A_AC[l,2]]-model.delta_AC[model.A_AC[l,1]])))
# model.KVL_real_from     = Constraint(model.L_AC, rule=KVL_real_fromend)
# model.KVL_real_to       = Constraint(model.L_AC, rule=KVL_real_toend)
# model.KVL_reactive_from = Constraint(model.L_AC, rule=KVL_reactive_fromend)
# model.KVL_reactive_to   = Constraint(model.L_AC, rule=KVL_reactive_toend)

# --- Kirchoff's voltage law on each transformer line ---
# def KVL_real_fromendTransf(model,l):
#     return model.pLfromT_AC[l] == model.G11T[l]*(model.v_AC[model.AT_AC[l,1]]**2)+\
#     model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.B12T[l]*sin(model.delta_AC[model.AT_AC[l,1]]-\
#     model.delta_AC[model.AT_AC[l,2]])+model.G12T[l]*cos(model.delta_AC[model.AT_AC[l,1]]-model.delta_AC[model.AT_AC[l,2]]))
# def KVL_real_toendTransf(model,l):
#     return model.pLtoT_AC[l] == model.G22T[l]*(model.v_AC[model.AT_AC[l,2]]**2)+\
#     model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.B21T[l]*sin(model.delta_AC[model.AT_AC[l,2]]-\
#     model.delta_AC[model.AT_AC[l,1]])+model.G21T[l]*cos(model.delta_AC[model.AT_AC[l,2]]-model.delta_AC[model.AT_AC[l,1]]))
# def KVL_reactive_fromendTransf(model,l):
#     return model.qLfromT_AC[l] == -model.B11T[l]*(model.v_AC[model.AT_AC[l,1]]**2)+\
#     model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.G12T[l]*sin(model.delta_AC[model.AT_AC[l,1]]-\
#     model.delta_AC[model.AT_AC[l,2]])-model.B12T[l]*cos(model.delta_AC[model.AT_AC[l,1]]-model.delta_AC[model.AT_AC[l,2]]))
# def KVL_reactive_toendTransf(model,l):
#     return model.qLtoT_AC[l] == -model.B22T[l]*(model.v_AC[model.AT_AC[l,2]]**2)+\
#     model.v_AC[model.AT_AC[l,1]]*model.v_AC[model.AT_AC[l,2]]*(model.G21T[l]*sin(model.delta_AC[model.AT_AC[l,2]]-\
#     model.delta_AC[model.AT_AC[l,1]])-model.B21T[l]*cos(model.delta_AC[model.AT_AC[l,2]]-model.delta_AC[model.AT_AC[l,1]]))
# model.KVL_real_fromTransf     = Constraint(model.TRANSF_AC, rule=KVL_real_fromendTransf)
# model.KVL_real_toTransf       = Constraint(model.TRANSF_AC, rule=KVL_real_toendTransf)
# model.KVL_reactive_fromTransf = Constraint(model.TRANSF_AC, rule=KVL_reactive_fromendTransf)
# model.KVL_reactive_toTransf   = Constraint(model.TRANSF_AC, rule=KVL_reactive_toendTransf)

# # --- generator power limits ---
# def Real_Power_Max(model,g):
#     return model.pG_AC[g] <= model.PGmax_AC[g]
# def Real_Power_Min(model,g):
#     return model.pG_AC[g] >= model.PGmin_AC[g]
# def Reactive_Power_Max(model,g):
#     return model.qG_AC[g] <= model.QGmax_AC[g]
# def Reactive_Power_Min(model,g):
#     return model.qG_AC[g] >= model.QGmin_AC[g]
# def Equal_HVDC(model, g1, g2):
#     return model.pG_AC[g1] == -model.pG_AC[g2]
# def PQ_Circle(model, g):
#     return model.pG_AC[g]**2 + model.qG_AC[g]**2 <= model.PGmax_AC[g]**2
# def ACDC_Link(model, g_AC, g_DC):
#     return model.pG_AC[g_AC] == model.pG_DC[g_DC]
# model.PGmaxC_DC = Constraint(model.G_AC, rule=Real_Power_Max)
# model.PGminC_DC = Constraint(model.G_AC, rule=Real_Power_Min)
# model.QGmaxC = Constraint(model.G_AC, rule=Reactive_Power_Max)
# model.QGminC = Constraint(model.G_AC, rule=Reactive_Power_Min)
# model.equalHVDC = Constraint(model.HVDC_Pairs, rule=Equal_HVDC)
# model.inside_PQ = Constraint(model.HVDC_CONV, rule=PQ_Circle)
# model.link_ACDC = Constraint(model.ACDC_Links, rule=ACDC_Link)


# ---wind generator power limits ---
# def Wind_Real_Power_Max(model,w):
#     return model.pW_AC[w] <= model.WGmax_AC[w]
# def Wind_Real_Power_Min(model,w):
#     return model.pW_AC[w] >= model.WGmin_AC[w]
# def Wind_Reactive_Power_Max(model,w):
#     return model.qW_AC[w] <= model.WGQmax_AC[w]
# def Wind_Reactive_Power_Min(model,w):
#     return model.qW_AC[w] >= model.WGQmin_AC[w]
# model.WGmaxC_AC  = Constraint(model.WIND_AC, rule=Wind_Real_Power_Max)
# model.WGminC_AC  = Constraint(model.WIND_AC, rule=Wind_Real_Power_Min)
# model.WGQmaxC = Constraint(model.WIND_AC, rule=Wind_Reactive_Power_Max)
# model.WGQminC = Constraint(model.WIND_AC, rule=Wind_Reactive_Power_Min)

# --- demand and load shedding ---
# def Load_Shed_real(model,d):
#     return model.pD_AC[d] == model.alpha_AC[d]*model.PD_AC[d]
# def Load_Shed_reactive(model,d):
#     return model.qD_AC[d] == model.alpha_AC[d]*model.QD_AC[d]
# def alpha_FixNegDemands(model,d):
#     return model.alpha_AC[d] == 1

# model.LoadShed_real     = Constraint(model.D_AC, rule=Load_Shed_real)
# model.LoadShed_reactive = Constraint(model.D_AC, rule=Load_Shed_reactive)
# model.alphaFix          = Constraint(model.DNeg_AC, rule=alpha_FixNegDemands)


# def alpha_BoundUB(model,d):
#     return model.alpha_AC[d] <= 1
# def alpha_BoundLB(model,d):
#     return model.alpha_AC[d] >= 0
# model.alphaBoundUBC = Constraint(model.D_AC, rule=alpha_BoundUB)
# model.alphaBoundLBC = Constraint(model.D_AC, rule=alpha_BoundLB)

# # --- line power limits ---
# def line_lim1_def(model,l):
#     return model.pLfrom_AC[l]**2+model.qLfrom_AC[l]**2 <= model.SLmax_AC[l]**2
# def line_lim2_def(model,l):
#     return model.pLto_AC[l]**2+model.qLto_AC[l]**2 <= model.SLmax_AC[l]**2
# model.line_lim1_AC = Constraint(model.L_AC, rule=line_lim1_def)
# model.line_lim2_AC = Constraint(model.L_AC, rule=line_lim2_def)

# --- power flow limits on transformer lines---
# def transf_lim1_def(model,l):
#     return model.pLfromT_AC[l]**2+model.qLfromT_AC[l]**2 <= model.SLmaxT_AC[l]**2
# def transf_lim2_def(model,l):
#     return model.pLtoT_AC[l]**2+model.qLtoT_AC[l]**2 <= model.SLmaxT_AC[l]**2
# model.transf_lim1_AC = Constraint(model.TRANSF_AC, rule=transf_lim1_def)
# model.transf_lim2_AC = Constraint(model.TRANSF_AC, rule=transf_lim2_def)

# --- voltage constraints ---
# def bus_max_voltage(model,b):
#     return model.v_AC[b] <= model.Vmax_AC[b]
# def bus_min_voltage(model,b):
#     return model.v_AC[b] >= model.Vmin_AC[b]
# model.Vmaxc = Constraint(model.B_AC, rule=bus_max_voltage)
# model.Vminc = Constraint(model.B_AC, rule=bus_min_voltage)

# --- reference bus constraint ---
# def ref_bus_def(model,b):
#     return model.delta_AC[b]==0
# model.refbus = Constraint(model.b0_AC, rule=ref_bus_def)


# # ================================== DC ===================================

# --- Kirchoff's current law at each bus b ---
def KCL_def(model, b):
    return sum(model.pG_DC[g] for g in model.G_DC if (b,g) in model.Gbs_DC) +\
    sum(model.pW_DC[w] for w in model.WIND_DC if (b,w) in model.Wbs_DC) == \
    sum(model.pD_DC[d] for d in model.D_DC if (b,d) in model.Dbs_DC)+\
    sum(model.pL_DC[l] for l in model.L_DC if model.A_DC[l,1]==b)- \
    sum(model.pL_DC[l] for l in model.L_DC if model.A_DC[l,2]==b)+\
    sum(model.pLT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,1]==b)- \
    sum(model.pLT_DC[l] for l in model.TRANSF_DC if model.AT_DC[l,2]==b)+\
    sum(model.GB_DC[s] for s in model.SHUNT_DC if (b,s) in model.SHUNTbs_DC)
model.KCL_const = Constraint(model.B_DC, rule=KCL_def)

    with open("modelformulation.txt", "w") as outputfile:
            self.instance.pprint(outputfile)

# --- Kirchoff's voltage law on each line and transformer---
def KVL_line_def(model,l):
    return model.pL_DC[l] == (-model.BL_DC[l])*model.deltaL_DC[l]
def KVL_trans_def(model,l):
    return model.pLT_DC[l] == (-model.BLT_DC[l])*model.deltaLT_DC[l]
model.KVL_line_const     = Constraint(model.L_DC, rule=KVL_line_def)
model.KVL_trans_const    = Constraint(model.TRANSF_DC, rule=KVL_trans_def)

# --- demand model ---
def demand_model(model,d):
    return model.pD_DC[d] == model.alpha_DC[d]*model.PD_DC[d]
def demand_LS_bound_Max(model,d):
    return model.alpha_DC[d] <= 1
model.demandmodelC = Constraint(model.D_DC, rule=demand_model)
model.demandalphaC = Constraint(model.D_DC, rule=demand_LS_bound_Max)

# --- generator power limits ---
def Real_Power_Max(model,g):
    return model.pG_DC[g] <= model.PGmax_DC[g]
def Real_Power_Min(model,g):
    return model.pG_DC[g] >= model.PGmin_DC[g]
    

model.PGmaxC_AC = Constraint(model.G_DC, rule=Real_Power_Max)
model.PGminC_AC = Constraint(model.G_DC, rule=Real_Power_Min)

# # ---wind generator power limits ---
def Wind_Real_Power_Max(model,w):
    return model.pW[w] <= model.WGmax_DC[w]
def Wind_Real_Power_Min(model,w):
    return model.pW[w] >= model.WGmin_DC[w]
model.WGmaxC_DC = Constraint(model.WIND_DC, rule=Wind_Real_Power_Max)
model.WGminC_DC = Constraint(model.WIND_DC, rule=Wind_Real_Power_Min)

# # --- line power limits ---
def line_lim1_def(model,l):
    return model.pL_DC[l] <= model.SLmax_DC[l]
def line_lim2_def(model,l):
    return model.pL_DC[l] >= -model.SLmax_DC[l]
model.line_lim1_DC = Constraint(model.L_DC, rule=line_lim1_def)
model.line_lim2_DC = Constraint(model.L_DC, rule=line_lim2_def)

# # --- power flow limits on transformer lines---
def transf_lim1_def(model,l):
    return model.pLT_DC[l] <= model.SLmaxT_DC[l]
def transf_lim2_def(model,l):
    return model.pLT_DC[l] >= -model.SLmaxT_DC[l]
model.transf_lim1_DC = Constraint(model.TRANSF_DC, rule=transf_lim1_def)
model.transf_lim2_DC = Constraint(model.TRANSF_DC, rule=transf_lim2_def)

# # --- phase angle constraints ---
def phase_angle_diff1(model,l):
    return model.deltaL_DC[l] == model.delta_DC[model.A_DC[l,1]] - \
    model.delta_DC[model.A_DC[l,2]]
model.phase_diff1 = Constraint(model.L_DC, rule=phase_angle_diff1)

# # --- reference bus constraint ---
def ref_bus_def(model,b):
    return model.delta_DC[b]==0
model.refbus_DC = Constraint(model.b0_DC, rule=ref_bus_def)