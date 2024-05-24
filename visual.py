
# First networkx library is imported  
# along with matplotlib 
import networkx as nx 
import matplotlib.pyplot as plt 
import pandas as pd
import os
import opf_intro
import numpy as np
import pydot
import time

  
# Defining a Class 
class GraphVisualisation: 
   
    def __init__(self): 
        self.edges = [] 
        self.weights = []
        self.node_type = [[], [], []]
          

    def add_weighted_edge(self, point_a, point_b, weight): 
        edge = [point_a, point_b, weight] 
        if weight < 0:
            edge = [point_b, point_a, -weight] 
        self.edges.append(edge) 

    def assign_node_types(self, G, generator_nodes, demand_nodes):
        for node in G.nodes():
            if node in generator_nodes:
                self.node_type[0].append(node)
            elif node in demand_nodes:
                self.node_type[1].append(node)
            else:
                self.node_type[2].append(node)

    def assign_node_labels(self, G, demand_data, generator_nodes, results):
        node_labels = {}
        demand_nodes = list(demand_data["busname"])

        for node in G.nodes:
            if node in demand_nodes:
                node_demand = round(results["pD"][demand_data[demand_data["busname"]==node]["name"].iloc[0]], 2)
                node_labels[node] = str(node) + ": \n" + str(node_demand)
            else:
                node_labels[node] = node

        return node_labels
    
   
    def visualise(self, results, generator_nodes, demand_data, graph_data): 
        demand_nodes = list(demand_data["busname"])

        max_node = max(max(graph_data["from_busname"]), max(graph_data["to_busname"]))
        for index, row in graph_data.iterrows():
            self.add_weighted_edge(row["from_busname"], row["to_busname"], round(results["pL"][row["name"]], 2))
            

        G = nx.DiGraph() 
        G.add_weighted_edges_from(self.edges) 

        self.assign_node_types(G, generator_nodes, demand_nodes)

        pos = nx.shell_layout(G)

        nx.draw(G, pos, nodelist=self.node_type[0], node_size=1000, node_color="green", node_shape="8") 
        nx.draw(G, pos, nodelist=self.node_type[1], node_size=1000, node_color="red", node_shape="s") 
        nx.draw(G, pos, nodelist=self.node_type[2], node_size=1000, node_color="grey", node_shape="o") 

        node_labels = self.assign_node_labels(G, demand_data, generator_nodes, results)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

        
        weight_labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=weight_labels)
        plt.show(block=False) 

    def close(self):
        plt.close()
  
# Driver code 
G = GraphVisualisation() 
data = pd.ExcelFile(os.path.join(".", "data", "case9_backup.xlsx"))

# solve opf
results = opf_intro.dcopf()
graph_data = pd.read_excel(data, 'branch')


demand_data = pd.read_excel(data, 'demand')
generator_data = pd.read_excel(data, 'generator')
G.visualise(results, list(generator_data["busname"]), demand_data, graph_data)

"""
To do:
separate out opf-intro file

extra colour vibes:
alpha- proportion demand met on demand nodes
deltaL- phase angle differences on lines
delta- phase angles at different nodes
"""