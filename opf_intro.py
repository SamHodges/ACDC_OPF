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

def dcopf(tc='default',solver='ipopt',neos=True,out=0):
    
    #options
    opt=({'neos':neos,\
    'solver':solver,'out':out})
    testcase = os.path.join(".", "data", "case9.xlsx")
    model ='DCOPF'
    # ==log==
    runcase(testcase,model,opt)
    modelf = imp.load_source(model, 'model.py')
    model = modelf.model

    datfile = 'datafile.dat'

    instance       = model.create_instance(datfile)
    solveroptions  = SolverFactory(opt['solver'])
    solver_manager = SolverManagerFactory('neos')
    solver_manager.solve(instance, opt=solveroptions)

    # logging.info("Solver selected: "+opt['solver'])
    # logging.info("Testcase selected: "+testcase)
    # logging.info("Model selected: "+model)
    # runcase(testcase,model,opt)
    # logging.info("Done!")


    results = {}

    for v in instance.component_data_objects(Var):
        split_key = str(v).split("[")
        try:
            results[split_key[0]][split_key[1][:-1]] =  value(v)
        except:
            results[split_key[0]] = {}
            results[split_key[0]][split_key[1][:-1]] =  value(v)

    print(results)
    return results



def runcase(testcase,mod,opt=None):
    oats_dir = os.path.dirname(os.path.realpath(__file__))
    if 'user_def_model' in opt:
        modelf = imp.load_source(mod, mod+'.py')
        model = modelf.model
    else:
        try:
            modelf = imp.load_source(mod, os.path.join('.', 'model.py'))
            model = modelf.model
        except Exception:
            raise
    try:
        ptc = selecttestcase(testcase) #read test case
    except Exception:
        raise
    datfile = 'datafile.dat'
    r = printdata(datfile,ptc,mod,opt)
    r.reducedata()
    r.printheader()
    
    r.printkeysets()
    r.printnetwork()
    #'OPF' or 'LF'
    if 'OPF' in mod:
        r.printOPF()
    #'AC' or 'DC

    r.printDCOPF()



def selecttestcase(test):
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
    df_hvdc        = xl.parse("hvdc")

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
    "hvdc":df_hvdc.dropna(how='all'),
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
    def __init__(self,datfile,data,model,options):
        self.datfile = datfile
        self.data    = data
        self.model   = model
        self.options = options

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
        f.write('#_author_:W. Bukhsh\n')
        f.write('#Time stamp: '+ str(datetime.datetime.now())+'\n')
        f.close()
    def printkeysets(self):
        f = open(self.datfile, 'a')
        ##===sets===
        #---set of buses---
        f.write('set B:=\n')
        for i in self.data["bus"].index.tolist():
            f.write(str(self.data["bus"]["name"][i])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i]) + "_A" +"\n")
                f.write(str(self.data["hvdc"]["name"][i]) + "_B" +"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i]) + "_INT" +"\n")
        f.write(';\n')
        #---set of generators---
        f.write('set G:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" \n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i]) + "_gen_A" +"\n")
                f.write(str(self.data["hvdc"]["name"][i]) + "_gen_B" +"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i]) + "_gen_INT" +"\n")
        f.write(';\n')
        #---set of hvdc-----
        f.write('set HVDC_Pairs:=\n')
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write("(" + str(self.data["hvdc"]["name"][i]) + "_gen_A, ")
                f.write(str(self.data["hvdc"]["name"][i]) + "_gen_B)" + "\n")
        f.write(';\n')
        #---set of demands---
        f.write('set D:=\n')
        for i in self.data["demand"]["name"].unique():
            f.write(str(i)+"\n")
        f.write(';\n')
        #---set of wind generators---
        if not(self.data["wind"].empty):
            f.write('set WIND:=\n')
            for i in self.data["wind"]["name"].unique():
                f.write(str(i)+"\n")
            f.write(';\n')
        #===parameters===
        #---Real power demand---
        f.write('param PD:=\n')
        for i in self.data["demand"].index.tolist():
            f.write(str(self.data["demand"]["name"][i])+" "+str(float(self.data["demand"]["real"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        # set of negative demands
        f.write('set DNeg:=\n')
        for i in self.data["demand"].index.tolist():
            if float(self.data["demand"]["real"][i]) < 0:
                f.write(str(self.data["demand"]["name"][i]) + "\n")
        f.write(';\n')
        f.write('param VOLL:=\n')
        for i in self.data["demand"].index.tolist():
            f.write(str(self.data["demand"]["name"][i])+" "+str(float(self.data["demand"]["VOLL"][i]))+"\n")
        f.write(';\n')
        f.write('param baseMVA:=\n')
        f.write(str(self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        f.close()
    def printnetwork(self):
        f = open(self.datfile, 'a')
        f.write('set LE:=\n 1 \n 2;\n')
        #set of transmission lines
        f.write('set L:=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i]) + "_a" +"\n")
                f.write(str(self.data["hvdc"]["name"][i]) + "_b" +"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i]) + "_int" +"\n")
        f.write(';\n')
        #set of transformers
        if not(self.data["transformer"].empty):
            f.write('set TRANSF:= \n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+"\n")
            f.write(';\n')
        #---set of generator-bus mapping (gen_bus, gen_ind)---
        f.write('set Gbs:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["busname"][i]) + " "+str(self.data["generator"]["name"][i])+" \n")

        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i]) + "_A "+str(self.data["hvdc"]["name"][i])+ "_gen_A" + "\n")
                f.write(str(self.data["hvdc"]["name"][i]) + "_B "+str(self.data["hvdc"]["name"][i])+ "_gen_B" + "\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i]) + "_INT "+str(self.data["hvdc"]["name"][i])+ "_gen_INT" + "\n")
        f.write(';\n')
        #---set of wind generator-bus mapping (windgen_bus, gen_ind)---
        if not(self.data["wind"].empty):
            f.write('set Wbs:=\n')
            for i in self.data["wind"].index.tolist():
                f.write(str(self.data["wind"]["busname"][i]) + " "+str(self.data["wind"]["name"][i])+"\n")
            f.write(';\n')
        #---set of demand-bus mapping (demand_bus, demand_ind)---
        f.write('set Dbs:=\n')
        for i in self.data["demand"].index.tolist():
            f.write(str(self.data["demand"]["busname"][i]) + " "+str(self.data["demand"]["name"][i])+"\n")
        f.write(';\n')
        #---set of reference bus---
        f.write('set b0:=\n')
        slackbus = self.data["generator"]["busname"][self.data["generator"]["type"]==3].tolist()
        for i in slackbus:
            f.write(str(i)+""+"\n")
        f.write(';\n')
        #---param defining system topolgy---
       
        f.write('param A:=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+"1"+" "+str(self.data["branch"]["from_busname"][i])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_a "+"1"+" "+  str(self.data["hvdc"]["name"][i]) + "_A" +"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_b "+"1"+" "+ str(self.data["hvdc"]["name"][i]) + "_B"  +"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_int "+"1"+" "+ str(self.data["hvdc"]["name"][i]) + "_INT"  +"\n")
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+"2"+" "+str(self.data["branch"]["to_busname"][i])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_a "+"2"+" "+str(self.data["hvdc"]["from_busname"][i])+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_b "+"2"+" "+str(self.data["hvdc"]["to_busname"][i])+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_int "+"2"+" "+str(self.data["hvdc"]["to_busname"][i])+"\n")

        f.write(';\n')
        #---Transformers---
        if not(self.data["transformer"].empty):
            f.write('param AT:= \n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+"1"+" "+str(self.data["transformer"]["from_busname"][i])+"\n")
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+"2"+" "+str(self.data["transformer"]["to_busname"][i])+"\n")
            f.write(';\n')
        f.close()

    
    def printOPF(self):
        f = open(self.datfile, 'a')
        #---Real power generation bounds---
        f.write('param PGmin:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["PGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(-float(self.data["hvdc"]["ShortTermRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(-float(self.data["hvdc"]["ShortTermRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_INT "+str(-float(self.data["hvdc"]["ShortTermRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        f.write('param PGmax:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["PGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(self.data["hvdc"]["ShortTermRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(self.data["hvdc"]["ShortTermRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_INT "+str(float(self.data["hvdc"]["ShortTermRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")

        f.write(';\n')
        #---Real power wind generation bounds---
        if not(self.data["wind"].empty):
            f.write('param WGmin:=\n')
            for i in self.data["wind"].index.tolist():
                f.write(str(self.data["wind"]["name"][i])+" "+str(float(self.data["wind"]["PGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
            f.write('param WGmax:=\n')
            for i in self.data["wind"].index.tolist():
                f.write(str(self.data["wind"]["name"][i])+" "+str(float(self.data["wind"]["PGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
        #---Tranmission line bounds---
        f.write('param SLmax:=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+str(float(self.data["branch"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_a "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_b "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_int "+str(float(self.data["hvdc"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
        f.write(';\n')
        #---Transformer chracteristics---
        if not(self.data["transformer"].empty):
            f.write('param SLmaxT:=\n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+str(float(self.data["transformer"]["ContinousRating"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
            f.write(';\n')
        #---cost data---
        f.write('param c2:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc2"][i]))+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(0))+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(0))+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_INT "+str(float(0))+"\n")
        f.write(';\n')
        f.write('param c1:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc1"][i]))+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(float(0))+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(float(0))+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_INT "+str(float(self.data["hvdc"]["marginal_cost"][i]))+"\n")

        f.write(';\n')
        f.write('param c0:=\n')
        for i in self.data["generator"].index.tolist():
            f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc0"][i]))+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_A "+str(0)+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_B "+str(0)+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_gen_INT "+str(0)+"\n")

        f.write(';\n')
        f.close()
    def printDCOPF(self):
        f = open(self.datfile, 'a')
        #---Tranmission line chracteristics---
        f.write('param BL:=\n')
        for i in self.data["branch"].index.tolist():
            f.write(str(self.data["branch"]["name"][i])+" "+str(-1/float(self.data["branch"]["x"][i]))+"\n")
        for i in self.data["hvdc"].index.tolist():
            if str(self.data["hvdc"]["type"][i]) == "GB":
                f.write(str(self.data["hvdc"]["name"][i])+"_a "+str(-1/float(self.data["hvdc"]["x"][i]))+"\n")
                f.write(str(self.data["hvdc"]["name"][i])+"_b "+str(-1/float(self.data["hvdc"]["x"][i]))+"\n")
            else:
                f.write(str(self.data["hvdc"]["name"][i])+"_int "+str(-1/float(self.data["hvdc"]["x"][i]))+"\n")
        f.write(';\n')
        #---Transformer chracteristics---
        if not(self.data["transformer"].empty):
            f.write('param BLT:=\n')
            for i in self.data["transformer"].index.tolist():
                f.write(str(self.data["transformer"]["name"][i])+" "+str(-float(1/self.data["transformer"]["x"][i]))+"\n")
            f.write(';\n')
        f.close()


