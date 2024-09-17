import pandas as pd
import os 
import requests
import numpy

file_path = os.path.join(".", "data", "case9.xlsx")
data = pd.ExcelFile(file_path)

bus_list = pd.read_excel(data, "bus")
bus_names = list(bus_list["name"].copy())
bus_list["name"] = list(range(len(bus_list["name"])))
bus_dict = dict(zip(bus_names, list(range(len(bus_names)))))

hvdc = pd.read_excel(data, "hvdc")
branch = pd.read_excel(data, "branch")
generator = pd.read_excel(data, "generator")
demand = pd.read_excel(data, "demand")


converted = pd.DataFrame(index=range(450))
converted['hvdc_from'] = hvdc['from_busname'].map(bus_dict)
converted['hvdc_to'] = hvdc['to_busname'].map(bus_dict)
converted['branch_from'] = branch['from_busname'].map(bus_dict)
converted['branch_to'] = branch['to_busname'].map(bus_dict)
converted['generator'] = generator['busname'].map(bus_dict)
converted['demand'] = demand['busname'].map(bus_dict)
print(demand['busname'], branch['from_busname'], bus_dict)


converted.to_excel("output.xlsx")  