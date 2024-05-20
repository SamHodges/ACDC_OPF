import pandas as pd
import os

output_datafile = "output_data.csv"
input_datafile =  pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))



def printkeysets(self, input_datafile):
    output_data = pd.DataFrame()
    # data = csv input file
    ##===sets===
    #---set of buses---
    bus_data = pd.read_excel(input_datafile, "bus")
    output_data["Bus"] = bus_data["name"]

    #---set of generators---
    generator_data = pd.read_excel(input_datafile, "generator")
    output_data["Generator"] = generator_data["name"]
    
    #---set of demands---
    demand_data = pd.read_excel(input_datafile, "demand")
    output_data["Demand"] = demand_data["name"].unique()
    
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
        f.write(str(self.data["generator"]["busname"][i]) + " "+str(self.data["generator"]["name"][i])+"\n")
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
    for i in self.data["branch"].index.tolist():
        f.write(str(self.data["branch"]["name"][i])+" "+"2"+" "+str(self.data["branch"]["to_busname"][i])+"\n")
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

def printDC(self):
    f = open(self.datfile, 'a')
    #---Tranmission line chracteristics for DC load flow---
    f.write('param BL:=\n')
    for i in self.data["branch"].index.tolist():
        f.write(str(self.data["branch"]["name"][i])+" "+str(-1/float(self.data["branch"]["x"][i]))+"\n")
    f.write(';\n')
    #---Transformer chracteristics---
    if not(self.data["transformer"].empty):
        f.write('param BLT:=\n')
        for i in self.data["transformer"].index.tolist():
            f.write(str(self.data["transformer"]["name"][i])+" "+str(-float(1/self.data["transformer"]["x"][i]))+"\n")
        f.write(';\n')
    f.close()
def printOPF(self):
    f = open(self.datfile, 'a')
    #---Real power generation bounds---
    f.write('param PGmin:=\n')
    for i in self.data["generator"].index.tolist():
        f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["PGLB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
    f.write(';\n')
    f.write('param PGmax:=\n')
    for i in self.data["generator"].index.tolist():
        f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["PGUB"][i])/self.data["baseMVA"]["baseMVA"][0])+"\n")
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
    f.write(';\n')
    f.write('param c1:=\n')
    for i in self.data["generator"].index.tolist():
        f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc1"][i]))+"\n")
    f.write(';\n')
    f.write('param c0:=\n')
    for i in self.data["generator"].index.tolist():
        f.write(str(self.data["generator"]["name"][i])+" "+str(float(self.data["generator"]["costc0"][i]))+"\n")
    f.write(';\n')
    f.close()
def printDCOPF(self):
    f = open(self.datfile, 'a')
    #---Tranmission line chracteristics---
    f.write('param BL:=\n')
    for i in self.data["branch"].index.tolist():
        f.write(str(self.data["branch"]["name"][i])+" "+str(-1/float(self.data["branch"]["x"][i]))+"\n")
    f.write(';\n')
    #---Transformer chracteristics---
    if not(self.data["transformer"].empty):
        f.write('param BLT:=\n')
        for i in self.data["transformer"].index.tolist():
            f.write(str(self.data["transformer"]["name"][i])+" "+str(-float(1/self.data["transformer"]["x"][i]))+"\n")
        f.write(';\n')
    f.close()