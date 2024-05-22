
# First networkx library is imported  
# along with matplotlib 
import networkx as nx 
import matplotlib.pyplot as plt 
import pandas as pd
import os
import opf_intro

  
# Defining a Class 
class GraphVisualisation: 
   
    def __init__(self): 
        self.visual = [] 
        self.labels = []
          

    def add_edge(self, a, b): 
        edge = [a, b] 
        self.visual.append(edge) 


    def visualise(self): 
        G = nx.Graph() 
        G.add_edges_from(self.visual) 
        nx.draw_networkx_labels(G, labels, font_size=22, font_color="whitesmoke")
        nx.draw_networkx(G) 
        plt.show() 
  
# Driver code 
G = GraphVisualisation() 

data = pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))
graph_data = pd.read_excel(data, 'branch')

for index, row in graph_data.iterrows():
    G.add_edge(row["from_busname"], row["to_busname"])


# solve opf
results = opf_intro.dcopf()

# G.visualise() 
G.visualise()

