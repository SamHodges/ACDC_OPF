from tkinter import *
import pandas as pd
import os
import visual
import opf_intro
from openpyxl import load_workbook


ws = Tk()
data = pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))
demand_data = pd.read_excel(data, 'demand')



# Make the Entry widgets and make a list of them.
entries = []




def callback(demand_data, graph_data, bus_data, G, writer):
    connections = []
    more_connections = True
    while more_connections:
        new_connection = input("Connecting node: ")
        connections.append(new_connection)
        more_connections = input("Add another connection? (y/n): ") == "y"
    
    auto = input("Would you like to use automatically chosen values? (y/n): ")

    if not auto:
        real_power = input("Real Power: ")
        reactive_power = input("Reactive Power: ")
        stat = input("Stat: ")
        voll = input("VOLL: ")
        new_demand = pd.DataFrame(["D4", 10, real_power, reactive_power, stat, voll]).T
        demand_data = pd.concat([demand_data, new_demand], ignore_index=True)
        print(demand_data)
    else:
        name = demand_data["name"][:-1]
        print(name)
        busname = max(bus_data["name"]) + 1
        print(busname)

        new_demand = pd.DataFrame(["D4", 10, 100, 50, 1, 100000]).T
        demand_combined = pd.concat([demand_data, new_demand], ignore_index=True)
        demand_combined.to_excel(writer, "demand")

        new_bus = pd.DataFrame([busname, 345, 1, 1, 1, 0, 0.9, 1.1, 0.9, 1.1]).T
        bus_combined = pd.concat([bus_data, new_bus], ignore_index=True)
        bus_combined.to_excel(writer, "bus")

        for bus_connection in connections:
            line_name = "L" + str(bus_connection) + "-" + str(busname)
            new_graph = pd.DataFrame([line_name, busname, bus_connection, 1, 0, 0.0576, 0, 250, 250, -360, 360, 1, 0.0001]).T
            graph_data = graph_data._append(new_graph, ignore_index = True)
        graph_data.to_excel(writer, "graph")

        writer._save()


# Driver code 
G = visual.GraphVisualisation() 
writer = pd.ExcelWriter(os.path.join(".", "data", "case9.xlsx"), engine='openpyxl', mode='a')


# solve opf
results = opf_intro.dcopf()
graph_data = pd.read_excel(data, 'branch')
bus_data = pd.read_excel(data, 'bus')
demand_data = pd.read_excel(data, 'demand')
generator_data = pd.read_excel(data, 'generator')

b = Button(ws, text = "Add Demand", width = 10, command = callback(demand_data, graph_data, bus_data, G, writer))
b.pack()

G.visualise(results, list(generator_data["busname"]), demand_data, graph_data)


mainloop()


