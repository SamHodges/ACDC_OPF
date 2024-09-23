import pandas as pd
import os 
import requests
import numpy
from geojson import Point, Feature, FeatureCollection, dump

# https://github.com/andrewlyden/PyPSA-GB/blob/master/data/storage_data.csv

access_key = "pk.eyJ1Ijoic2FtaG9kZ2VzIiwiYSI6ImNseGJ1cHlidTAyc2MybHM1b2ppY3M2aHgifQ.i0jxsdT4BQilGZQlFueQeg"

def create_geojson(file_path=os.path.join(".", "data", "PyPSA_case9_combined.xlsx")):
    data = pd.ExcelFile(file_path)
    bus_list = pd.read_excel(data, "bus")
    max_long = max(bus_list["x"])
    min_long = min(bus_list["x"]) 
    max_lat = max(bus_list["y"])
    min_lat = min(bus_list["y"])

    coordinate_info = []
    for index, row in bus_list.iterrows():
        coordinate =[row["x"], row["y"]]
        coordinate_info.append(coordinate)

    # line_info = []
    # line_list = pd.read_excel(data, "branch")
    # for index, row in line_list.iterrows():
    #     start = bus_list[bus_list["name"] == row["from_busname"]]
    #     end = bus_list[bus_list["name"] == row["to_busname"]]
    #     line_info.append([[start["x"].iloc[0], start["y"].iloc[0]], [end["x"].iloc[0], end["y"].iloc[0]]])

    # hvdc_lines = pd.read_excel(data, "hvdc")
    # for index, row in hvdc_lines.iterrows():
    #     start = bus_list[bus_list["name"] == row["from_busname"]]
    #     end = bus_list[bus_list["name"] == row["to_busname"]]
    #     line_info.append([[start["x"].iloc[0], start["y"].iloc[0]], [end["x"].iloc[0], end["y"].iloc[0]]])


    features = []
    
    for bus_coordinates in coordinate_info:
        features.append(Feature(geometry=Point(bus_coordinates)))
        
    feature_collection = FeatureCollection(features)

    with open('myfile.geojson', 'w') as f:
        dump(feature_collection, f)

create_geojson()