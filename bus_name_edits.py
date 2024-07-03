import pandas as pd
import os 
import requests
import numpy

file_path = os.path.join(".", "data", "case9 - Copy.xlsx")
data = pd.ExcelFile(file_path)

bus_list = pd.read_excel(data, "bus")
bus_names = list(bus_list["name"].copy())
bus_list["name"] = list(range(len(bus_list["name"])))

hvdc = pd.read_excel(data, "hvdc")
print(hvdc)
for line in hvdc.iterrows():
    print(line[1]["from_busname"])
    print(bus_names)
    line[1]["from_busname"] = bus_names.index(line[1]["from_busname"])
    line[1]["to_busname"] = bus_names.index(line[1]["to_busname"])
    
branch = pd.read_excel(data, "branch")
for line in branch.iterrows():
    line[1]["from_busname"] = bus_names.index(line[1]["from_busname"])
    line[1]["to_busname"] = bus_names.index(line[1]["to_busname"])
    
generator = pd.read_excel(data, "generator")
for line in generator.iterrows():
    line[1]["busname"] = bus_names.index(line[1]["busname"])
    
with pd.ExcelWriter(file_path) as writer:  
    hvdc.to_excel(writer, sheet_name='hvdc')
    branch.to_excel(writer, sheet_name='branch')
    generator.to_excel(writer, sheet_name='generator')