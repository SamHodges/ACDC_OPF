from matplotlib import image 
from matplotlib import pyplot as plt 
import os
import pandas as pd
import opf_intro

  
map = image.imread(os.path.join("data", "glasgow_map.png")) 
data = pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))

def draw_nodes(data):
    node_list = pd.read_excel(data, "bus")
    for index, row in node_list.iterrows():
        if row["name"] in list(pd.read_excel(data, "demand")["busname"]):
            colour = "red"
        elif row["name"] in list(pd.read_excel(data, "generator")["busname"]):
            colour = "green"
        else:
            colour = "white"
        # print("x, y", int(row["x"]), int(row["y"]))
        plt.plot(row["x"], row["y"], marker='v', color=colour) 

def draw_lines(data):
    line_list = pd.read_excel(data, "branch")
    node_list = pd.read_excel(data, "bus")
    for index, row in line_list.iterrows():
        start = node_list[node_list["name"] == row["from_busname"]]
        end = node_list[node_list["name"] == row["to_busname"]]
        plt.plot([start["x"], end["x"]], [start["y"], end["y"]], color="black", linewidth=2) 

    hvdc_lines = pd.read_excel(data, "hvdc")
    for index, row in hvdc_lines.iterrows():
        start = node_list[node_list["name"] == row["from_busname"]]
        end = node_list[node_list["name"] == row["to_busname"]]
        # print("x: ", int(start["x"]), int(end["x"]))
        # print("y: ", int(start["y"]), int(end["y"]))
        plt.plot([start["x"], end["x"]], [start["y"], end["y"]], color="blue", linewidth=3) 



# load in coordinates for everything
draw_lines(data)
draw_nodes(data)

# send off to opf_solver
results = opf_intro.dcopf()

  
# display *everything*
plt.imshow(map) 
plt.show() 
