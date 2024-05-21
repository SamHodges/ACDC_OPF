import pandas as pd
import os

output_datafile = "output_data.json"
input_datafile =  pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))

def get_relevant_info(self, input_datafile):
    output_data = {}

    bus_data = pd.read_excel(input_datafile, "bus")
    output_data["Bus"] = bus_data["name"]

    baseMVA_data = pd.read_excel(input_datafile, "baseMVA")
    output_data["Base_MVA"] = baseMVA_data["baseMVA"][0]

    generator_data = pd.read_excel(input_datafile, "generator")
    output_data["Generator"] = {}
    output_data["Generator"]["Name"] = generator_data["name"]    
    output_data["Generator"]["Bus_Name"] = generator_data["busname"] 
    output_data["Generator"]["Slack_Bus"] = generator_data[generator_data["type"] == 3]   
    output_data["Generator"]["Min_Power"] = generator_data["PGLB"]/output_data["Base_MVA"]
    output_data["Generator"]["Max_Power"] = generator_data["PGUB"]/output_data["Base_MVA"]
    output_data["Generator"]["C2"] = generator_data["costc2"]
    output_data["Generator"]["C1"] = generator_data["costc1"]
    output_data["Generator"]["C0"] = generator_data["costc0"]
    
    wind_data = pd.read_excel(input_datafile, "wind")
    if not(len(wind_data["busname"] == 0)):
        output_data["Wind"] = {}
        output_data["Wind"]["Name"] = wind_data["name"]
        output_data["Wind"]["Bus_Name"] = wind_data["busname"]
        output_data["Wind"]["Min_Wind"] = wind_data["PGLB"]/output_data["Base_MVA"]
        output_data["Wind"]["Max_Wind"] = wind_data["PGUB"]/output_data["Base_MVA"]
        
    demand_data = pd.read_excel(input_datafile, "demand")
    output_data["Demand"] = {}
    output_data["Demand"]["Name"] = demand_data["name"]
    output_data["Demand"]["Bus_Name"] = demand_data["busname"]
    output_data["Demand"]["Power_Demand"] = (demand_data["real"] / output_data["Base_MVA"])
    output_data["Demand"]["Negative_Demand"] = demand_data[demand_data["real"] < 0]["name"]
    output_data["Demand"]["Volume_of_Lost_Load"] = demand_data["VOLL"] 

    branch_data = pd.read_excel(input_datafile, "branch")
    output_data["Line_Sets"] = {}
    output_data["Line_Sets"]["Name"] = branch_data["name"]
    output_data["Line_Sets"]["Susceptance (BL)"] = -1/branch_data["x"]
    output_data["Line_Sets"]["Real_Power_Limit"] = branch_data["ContinousRating"]/output_data["Base_MVA"]

    transformer_data = pd.read_excel(input_datafile, "transformer")
    if not (len(transformer_data["name"] == 0)):
        output_data["Transformer"]["Name"] = transformer_data["name"]
        output_data["Transformer"]["From"] = transformer_data["from_busname"]
        output_data["Transformer"]["To"] = transformer_data["to_busname"]
        output_data["Transformer"]["Susceptance_(BLT)"] = -1/transformer_data["x"]
        output_data["Transformer"]["Transformer_Real_Power_Limit"] = transformer_data["ContinousRating"]/output_data["Base_MVA"]
    
    return output_data