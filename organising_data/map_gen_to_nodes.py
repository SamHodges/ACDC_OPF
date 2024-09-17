import pandas as pd
import os
import math


bus_file_path = os.path.join(".", "data", "case9 - Copy.xlsx")
bus_data = pd.ExcelFile(bus_file_path)
bus_list = pd.read_excel(bus_data, "bus")

gen_file_path = os.path.join(".", "data", "power_stations_locations_2020.csv")
gen_list = pd.read_csv(gen_file_path)

all_local_nodes = []
for index, row in gen_list.iterrows():
    min_distance = math.inf
    local_node = None
    for index_2, row_2 in bus_list.iterrows():
        distance = ((row["x"] - row_2["x"])**2 + (row["y"] - row_2["y"])**2)**0.5
        if distance < min_distance:
            min_distance = distance
            local_node = row_2["name"]
    
    print(row["Station Name"], " is by ", local_node)
    all_local_nodes.append(local_node)

print(all_local_nodes)
print(len(set(all_local_nodes)))

