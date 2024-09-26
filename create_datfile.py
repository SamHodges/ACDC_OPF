# opf code let's go!
# import oats
import os
import imp
import pandas as pd
import datetime
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
import logging
import math
import json
from pyomo.util.infeasible import log_infeasible_constraints



def selecttestcase(test, ac_mode):
    data_flags = {'storage':1,'ts':1,'shunt':1}
    xl = pd.ExcelFile(test)
                      # ,engine='openpyxl')

    df_bus         = xl.parse("bus")
    df_demand      = xl.parse("demand")
    df_branch      = xl.parse("branch")
    df_generators  = xl.parse("generator")
    df_transformer = xl.parse("transformer")
    df_wind        = xl.parse("wind")
    df_baseMVA     = xl.parse("baseMVA")
    df_zone        = xl.parse("zone")
    df_zonalNTC    = xl.parse("zonalNTC")
    if ac_mode:
        df_hvdc        = xl.parse("hvdc")
        extra_data_name = "hvdc"
        extra_data = df_hvdc.dropna(how='all')
    else:
        df_ac_links    = xl.parse("ac_links")
        extra_data_name = "ac_links"
        extra_data = df_ac_links.dropna(how='all')

    data = {
    "bus": df_bus.dropna(how='all'),
    "demand": df_demand.dropna(how='all'),
    "branch": df_branch.dropna(how='all'),
    "generator": df_generators.dropna(how='all'),
    "transformer": df_transformer.dropna(how='all'),
    "wind": df_wind.dropna(how='all'),
    "baseMVA": df_baseMVA.dropna(how='all'),
    "zone":df_zone.dropna(how='all'),
    "zonalNTC":df_zonalNTC.dropna(how='all'),
    extra_data_name: extra_data,
    "flags":data_flags
    }
    try:
        df_storage   = xl.parse("storage")
        data.update( {"storage" : df_storage.dropna(how='all')} )
    except:
        data["flags"]['storage'] = 0
    try:
        df_ts    = xl.parse("timeseries",header=[0,1])
        data.update( {"timeseries" : df_ts.dropna(how='all')} )
    except:
        data["flags"]['ts'] = 0
    try:
        df_ts    = xl.parse("shunt")
        data.update( {"shunt" : df_ts.dropna(how='all')} )
    except:
        data["flags"]['shunt'] = 0

    return data





class printdata(object):
    def __init__(self,datfile,data,options, opf_case):
        self.datfile = datfile
        self.data    = data
        self.model   = "ACDC"
        self.options = options
        self.opf_case = opf_case

    def reducedata(self):
        self.data["demand"]      = self.data["demand"].drop(self.data["demand"][self.data["demand"]['stat'] == 0].index.tolist())
        self.data["branch"]      = self.data["branch"].drop(self.data["branch"][self.data["branch"]['stat'] == 0].index.tolist())
        if self.data["flags"]["shunt"]:
            self.data["shunt"]       = self.data["shunt"].drop(self.data["shunt"][self.data["shunt"]['stat'] == 0].index.tolist())
        if self.data["flags"]["storage"]:
            self.data["storage"]     = self.data["storage"].drop(self.data["storage"][self.data["storage"]['stat'] == 0].index.tolist())
        self.data["transformer"] = self.data["transformer"].drop(self.data["transformer"][self.data["transformer"]['stat'] == 0].index.tolist())
        self.data["wind"]        = self.data["wind"].drop(self.data["wind"][self.data["wind"]['stat'] == 0].index.tolist())
        self.data["generator"]   = self.data["generator"].drop(self.data["generator"][self.data["generator"]['stat'] == 0].index.tolist())
    def printheader(self):
        f = open(self.datfile, 'w')
        #####PRINT HEADER--START
        f.write('#This is Python generated data file for Pyomo model DCLF.py\n')
        f.write('#Time stamp: '+ str(datetime.datetime.now())+'\n')
        f.close()
    def printkeysets(self, ac_mode):
        if ac_mode:
            mode_add_on = "_AC"
        else:
            mode_add_on = "_DC"
        f = open(self.datfile, 'a')
        ##===sets===
        #---set of buses---
        f.write('set B' + mode_add_on + ':=\n')
        for i in self.data["bus"].index.tolist():
            f.write(str(self.data["bus"]["name"][i])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_A" +"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_B" +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) +"\n")
        f.write(';\n')
        #---set of generators---
        f.write('set G' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" \n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen_A" +"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen_B" +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen" +"\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["name"][i]) +"\n")
        f.write(';\n')
        #---set of hvdc-----
        if ac_mode:
            f.write('set HVDC_Pairs:=\n')
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write("(" + str(self.data["hvdc"]["name"][i]) + "_gen_A, ")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen_B)" + "\n")
            f.write(';\n')
            f.write('set HVDC_CONV:=\n')
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen_A" +"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen_B" +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + "_gen" +"\n")
            f.write(';\n')
        #---set of demands---
        f.write('set D' + mode_add_on + ':=\n')
        for i in self.data["demand"]["name"].unique():
            f.write(str(i)+"\n")
        f.write(';\n')
        #---set of wind generators---
        if not(self.data["wind"].empty):
            f.write('set WIND' + mode_add_on + ':=\n')
            for i in self.data["wind"]["name"].unique():
                f.write(str(i)+"\n")
            f.write(';\n')
        #===parameters===
        #---Real power demand---
        f.write('param PD' + mode_add_on + ':=\n')
        for i in self.data["demand"].index.tolist():
            print("")
            f.write(str(self.data["demand"]["name"][i])+" "+str(float(self.data["demand"]["real"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        # set of negative demands
        f.write('set DNeg' + mode_add_on + ':=\n')
        for i in self.data["demand"].index.tolist():
            if float(self.data["demand"]["real"][i]) < 0:
                f.write(str(self.data["demand"]["name"][i]) + "\n")
        f.write(';\n')
        f.write('param VOLL' + mode_add_on + ':=\n')
        for i in self.data["demand"].index.tolist():
            f.write(str(self.data["demand"]["name"][i])+" "+str(float(self.data["demand"]["VOLL"][i]))+"\n")
        f.write(';\n')
        f.write('param baseMVA' + mode_add_on + ':=\n')
        f.write(str(self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        f.close()
    def printnetwork(self, ac_mode):
        if ac_mode:
            mode_add_on = "_AC"
        else:
            mode_add_on = "_DC"
        f = open(self.datfile, 'a')
        f.write('set LE' + mode_add_on + ':=\n 1 \n 2\n;\n')
        #set of transmission lines
        f.write('set L' + mode_add_on + ':=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a" +"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b" +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) +"\n")
        f.write(';\n')
        #set of transformers
        if not(self.data["transformer"].empty):
            f.write('set TRANSF' + mode_add_on + ':= \n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+"\n")
            f.write(';\n')
        #---set of generator-bus mapping (gen_bus, gen_ind)---
        f.write('set Gbs' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["busname"][i]) + " "+str(self.data["generator"]["name"][i])+" \n")

        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_A "+str(self.data["hvdc"]["name"][i])+ "_gen_A" + "\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_B "+str(self.data["hvdc"]["name"][i])+ "_gen_B" + "\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " "+str(self.data["hvdc"]["name"][i])+ "_gen" + "\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["busname"][i]) + " "+str(self.data["ac_links"]["name"][i]) + "\n")

        f.write(';\n')
        #---set of wind generator-bus mapping (windgen_bus, gen_ind)---
        if not(self.data["wind"].empty):
            f.write('set Wbs' + mode_add_on + ':=\n')
            for i in self.data["wind"].index.tolist():
                f.write(str(self.data["wind"]["busname"][i]) + " "+str(self.data["wind"]["name"][i])+"\n")
            f.write(';\n')
        #---set of demand-bus mapping (demand_bus, demand_ind)---
        f.write('set Dbs' + mode_add_on + ':=\n')
        for i in self.data["demand"].index.tolist():
            f.write(str(self.data["demand"]["busname"][i]) + " "+str(self.data["demand"]["name"][i])+"\n")
        f.write(';\n')
        #---set of reference bus---
        f.write('set b0' + mode_add_on + ':=\n')
        slackbus = self.data["generator"]["busname"][self.data["generator"]["type"]==3].tolist()
        for i in slackbus:
            f.write(str(i)+""+"\n")
        f.write(';\n')
        #---param defining system topolgy---
       
        f.write('param A' + mode_add_on + ':=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+"1"+" "+str(self.data["branch"]["from_busname"][i])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_a "+"1"+" "+  str(self.data["hvdc"]["name"][i]) + "_A" +"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_b "+"1"+" "+ str(self.data["hvdc"]["name"][i]) + "_B"  +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+" "+"1"+" "+ str(self.data["hvdc"]["name"][i]) +"\n")
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+"2"+" "+str(self.data["branch"]["to_busname"][i])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_a "+"2"+" "+str(self.data["hvdc"]["from_busname"][i])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_b "+"2"+" "+str(self.data["hvdc"]["to_busname"][i])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+" "+"2"+" "+str(self.data["hvdc"]["to_busname"][i])+"\n")

        f.write(';\n')
        #---Transformers---
        if not(self.data["transformer"].empty):
            f.write('param AT' + mode_add_on + ':= \n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+"1"+" "+str(self.data["transformer"]["from_busname"][i])+"\n")
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+"2"+" "+str(self.data["transformer"]["to_busname"][i])+"\n")
            f.write(';\n')
        f.close()

    
    def printOPF(self, ac_mode=False, ac_results=None):
        f = open(self.datfile, 'a')
        if ac_mode:
            mode_add_on = "_AC"
        else:
            mode_add_on = "_DC"
        #---Real power generation bounds---
        f.write('param PGmin' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["PGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(-float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(-float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(-float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["name"][i])+" "+str(-float(self.data["ac_links"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")

        f.write(';\n')
        f.write('param PGmax' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["PGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["name"][i])+" "+str(float(self.data["ac_links"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")

        f.write(';\n')
        #---Real power wind generation bounds---
        if not(self.data["wind"].empty):
            f.write('param WGmin' + mode_add_on + ':=\n')
            for i in self.data["wind"].index.tolist():
                f.write(str(self.data["wind"]["name"][i])+" "+str(float(self.data["wind"]["PGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
            f.write('param WGmax' + mode_add_on + ':=\n')
            for i in self.data["wind"].index.tolist():
                f.write(str(self.data["wind"]["name"][i])+" "+str(float(self.data["wind"]["PGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
        #---Tranmission line bounds---
        f.write('param SLmax' + mode_add_on + ':=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+str(float(self.data["branch"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_a "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_b "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+" "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        #---Transformer chracteristics---
        if not(self.data["transformer"].empty):
            f.write('param SLmaxT' + mode_add_on + ':=\n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+str(float(self.data["transformer"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
        #---cost data---
        f.write('param c2' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc2"][i]))+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(0))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(0))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(float(0))+"\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["name"][i])+" "+str(0)+"\n")
        f.write(';\n')
        f.write('param c1' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc1"][i]))+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(0))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(0))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(float(self.data["hvdc"]["marginal_cost"][i]))+"\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["name"][i])+" "+str(0)+"\n")
        f.write(';\n')
        f.write('param c0' + mode_add_on + ':=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc0"][i]))+"\n")
        if ac_mode:
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(0)+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(0)+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(0)+"\n")
        else:
            for i in self.data["ac_links"].index.tolist():
                f.write(str(self.data["ac_links"]["name"][i])+" "+str(0)+"\n")

        f.write(';\n')
        f.close()
    def printACOPF(self):
        f = open(self.datfile, 'a')
        
        #set of shunts
        if self.data["flags"]["shunt"] and not(self.data["shunt"].empty):
            f.write('set SHUNT_AC:=\n')
            for i in self.data["shunt"].index.tolist():
                f.write(str(self.data["shunt"]["name"][i])+"\n")
            f.write(';\n')
            f.write('set SHUNTbs_AC:=\n')
            for i in self.data["shunt"].index.tolist():
                f.write(str(self.data["shunt"]["busname"][i])+" "+str(self.data["shunt"]["name"][i])+"\n")
            f.write(';\n')
            f.write('param GB_AC:=\n')
            for i in self.data["shunt"].index.tolist():
                f.write(str(self.data["shunt"]["name"][i])+" "+str(float(self.data["shunt"]["GL"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
            f.write('param BB_AC:=\n')
            for i in self.data["shunt"].index.tolist():
                f.write(str(self.data["shunt"]["name"][i])+" "+str(float(self.data["shunt"]["BL"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
        #---Reactive power demand---
        if self.opf_case != "linear":
            f.write('param QD_AC:=\n')
            for i in self.data["demand"].index.tolist():
                f.write(str(self.data["demand"]["name"][i])+" "+str(float(self.data["demand"]["reactive"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')

            f.write('param G11:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(self.data["branch"]["r"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2))+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
            f.write(';\n')
            f.write('param G12:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(-self.data["branch"]["r"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2))+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(-self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(-self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(-self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
            f.write(';\n')
            f.write('param G21:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(-self.data["branch"]["r"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2))+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(-self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(-self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(-self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
            f.write(';\n')
            f.write('param G22:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(self.data["branch"]["r"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2))+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(self.data["hvdc"]["r"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
            f.write(';\n')
            f.write('param B11:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(-self.data["branch"]["x"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(-self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(-self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(-self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
            f.write(';\n')
            f.write('param B12:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(self.data["branch"]["x"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2))+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
            f.write(';\n')
            f.write('param B21:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(self.data["branch"]["x"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2))+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2))+"\n")
            f.write(';\n')
            f.write('param B22:=\n')
            for i in self.data["branch"].index.tolist():
                f.write(str(self.data["branch"]["name"][i])+" "+str(-self.data["branch"]["x"][i]/(self.data["branch"]["r"][i]**2+self.data["branch"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_a " +str(-self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_b " +str(-self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " +str(-self.data["hvdc"]["x"][i]/(self.data["hvdc"]["r"][i]**2+self.data["hvdc"]["x"][i]**2)+0.5*self.data["branch"]["b"][i])+"\n")
            f.write(';\n')

            #derived transformer parameters
            if not(self.data["transformer"].empty):
                f.write('param G11T:=\n')
                for i in self.data["transformer"].index.tolist():
                    temp     = self.data["transformer"]["r"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+str(temp/(self.data["transformer"]["TapRatio"][i]**2))+"\n")
                f.write(';\n')
                f.write('param G12T:=\n')
                for i in self.data["transformer"].index.tolist():
                    tempG     = self.data["transformer"]["r"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    tempB     = -self.data["transformer"]["x"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+\
                    str(-1/(self.data["transformer"]["TapRatio"][i])*(tempG*math.cos(self.data["transformer"]["PhaseShift"][i])-\
                    tempB*math.sin(self.data["transformer"]["PhaseShift"][i])))+"\n")
                f.write(';\n')
                f.write('param G21T:=\n')
                for i in self.data["transformer"].index.tolist():
                    tempG     = self.data["transformer"]["r"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    tempB     = -self.data["transformer"]["x"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+\
                    str(-1/(self.data["transformer"]["TapRatio"][i])*(tempG*math.cos(self.data["transformer"]["PhaseShift"][i])+\
                    tempB*math.sin(self.data["transformer"]["PhaseShift"][i])))+"\n")
                f.write(';\n')

                f.write('param G22T:=\n')
                for i in self.data["transformer"].index.tolist():
                    temp     = self.data["transformer"]["r"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+str(temp)+"\n")
                f.write(';\n')
                f.write('param B11T:=\n')
                for i in self.data["transformer"].index.tolist():
                    temp     = -self.data["transformer"]["x"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+str(temp/(self.data["transformer"]["TapRatio"][i]**2))+"\n")
                f.write(';\n')
                f.write('param B12T:=\n')
                for i in self.data["transformer"].index.tolist():
                    tempG     = self.data["transformer"]["r"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    tempB     = -self.data["transformer"]["x"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+\
                    str(-1/(self.data["transformer"]["TapRatio"][i])*(tempB*math.cos(self.data["transformer"]["PhaseShift"][i])+\
                    tempG*math.sin(self.data["transformer"]["PhaseShift"][i])))+"\n")
                f.write(';\n')
                f.write('param B21T:=\n')
                for i in self.data["transformer"].index.tolist():
                    tempG     = self.data["transformer"]["r"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    tempB     = -self.data["transformer"]["x"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+\
                    str(-1/(self.data["transformer"]["TapRatio"][i])*(-tempG*math.sin(self.data["transformer"]["PhaseShift"][i])+\
                    tempB*math.cos(self.data["transformer"]["PhaseShift"][i])))+"\n")
                f.write(';\n')
                f.write('param B22T:=\n')
                for i in self.data["transformer"].index.tolist():
                    temp     = -self.data["transformer"]["x"][i]/(self.data["transformer"]["r"][i]**2+self.data["transformer"]["x"][i]**2)
                    f.write(str(self.data["transformer"]["name"][i])+" "+str(temp)+"\n")
                f.write(';\n')
                        
            #---Reactive power generation bounds---
            f.write('param QGmin_AC:=\n')
            for i in self.data["generator"].index.tolist():
                f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["QGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(0)+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(0)+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(0)+"\n")
            f.write(';\n')
            f.write('param QGmax_AC:=\n')
            for i in self.data["generator"].index.tolist():
                f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["QGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i])+"_gen "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
            if not (self.data["wind"].empty):
                f.write('param WGQmin_AC:=\n')
                for i in self.data["wind"].index.tolist():
                    f.write(str(self.data["wind"]["name"][i])+" "+str(float(self.data["wind"]["QGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                f.write(';\n')
                f.write('param WGQmax_AC:=\n')
                for i in self.data["wind"].index.tolist():
                    f.write(str(self.data["wind"]["name"][i])+" "+str(float(self.data["wind"]["QGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                f.write(';\n')

            #---Voltage bounds---
            f.write('param Vmin_AC:=\n')
            for i in self.data["bus"].index.tolist():
                f.write(str(self.data["bus"]["name"][i])+" "+str(self.data["bus"]["VNLB"][i])+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_A" + " " + str(0.9) + "\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_B" + " " + str(0.9) +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " + str(0.9) +"\n")
            f.write(';\n')
            
            f.write('param Vmax_AC:=\n')
            for i in self.data["bus"].index.tolist():
                f.write(str(self.data["bus"]["name"][i])+" "+str(self.data["bus"]["VNUB"][i])+"\n")
            for i in self.data["hvdc"].index.tolist():
                if str(self.data["hvdc"]["type"][i]) == "GB":
                    f.write(str(self.data["hvdc"]["name"][i]) + "_A" + " " + str(1.1) + "\n")
                    f.write(str(self.data["hvdc"]["name"][i]) + "_B" + " " + str(1.1) +"\n")
                else:
                    f.write(str(self.data["hvdc"]["name"][i]) + " " + str(1.1) +"\n")
            f.write(';\n')
            f.close()
    def printDCOPF(self):
        f = open(self.datfile, 'a')
        #---Tranmission line chracteristics---
        f.write('param BL_DC:=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+str(-1/float(self.data["branch"]["x"][i]))+"\n")
        f.write(';\n')
        #---Transformer chracteristics---
        if not(self.data["transformer"].empty):
            f.write('param BLT_DC:=\n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+str(-float(1/self.data["transformer"]["x"][i]))+"\n")
            f.write(';\n')
             
        f.close()
        
def connectACDC(ac_data, dc_data, datfile):
    f = open(datfile, 'a')
    f.write('set ACDC_Links:=\n')
    for i in ac_data["hvdc"].index.tolist():
        if str(ac_data["hvdc"]["type"][i]) == "MTDC":
            f.write("(" + str(ac_data["hvdc"]["name"][i]) + "_gen,")
            f.write(str(ac_data["hvdc"]["name"][i]) + ") \n")
    f.write(';\n')
        