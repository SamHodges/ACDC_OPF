from matplotlib import image 
from matplotlib import pyplot as plt 
import os
import pandas as pd
import opf_intro
from get_map_bounds import reload_image, coordinate_map

data = pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))
# reload_image(data)
map = image.imread(os.path.join("data", "image.png")) 

# load in coordinates for everything
node_list = coordinate_map(pd.read_excel(data, "bus"))

# send off to opf_solver
results = opf_intro.dcopf()

  
# display *everything*
plt.imshow(map) 
plt.show() 
