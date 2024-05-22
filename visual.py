
# First networkx library is imported  
# along with matplotlib 
import networkx as nx 
import matplotlib.pyplot as plt 
import pandas as pd
import os
import opf_intro
import numpy as np

  
# Defining a Class 
class GraphVisualisation: 
   
    def __init__(self): 
        self.edges = [] 
        self.weights = []
          

    def add_weighted_edge(self, point_a, point_b, weight): 
        edge = [point_a, point_b, weight] 
        self.edges.append(edge) 

   
    def visualise(self): 
        G = nx.DiGraph() 
        G.add_weighted_edges_from(self.edges) 

        colors = np.linspace(0, 1, len(G.nodes))
        pos = nx.shell_layout(G)

        nx.draw(
            G, pos, node_size=1000, node_color=colors
        ) 

        
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
        plt.show() 
  
# Driver code 
G = GraphVisualisation() 

data = pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))



# solve opf
results = opf_intro.dcopf()

graph_data = pd.read_excel(data, 'branch')
for index, row in graph_data.iterrows():
    G.add_weighted_edge(row["from_busname"], row["to_busname"], round(results["pL"][row["name"]], 2))


# G.visualise() 
G.visualise()

