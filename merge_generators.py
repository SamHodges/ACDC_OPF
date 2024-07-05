import pandas as pd
import os 
import requests
import numpy

file_path = os.path.join(".", "data", "case9.xlsx")
data = pd.ExcelFile(file_path)

generator = pd.read_excel(data, "generator")


df_new = generator.groupby(generator["name"]).aggregate({'PG': 'mean', 'PGUB': 'mean', 'QGUB': 'mean', 'costc1': 'mean'})
df_new.to_excel("output.xlsx")  