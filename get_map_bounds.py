import pandas as pd
import os 
import requests
import numpy

# https://github.com/andrewlyden/PyPSA-GB/blob/master/data/storage_data.csv

access_key = "pk.eyJ1Ijoic2FtaG9kZ2VzIiwiYSI6ImNseGJ1cHlidTAyc2MybHM1b2ppY3M2aHgifQ.i0jxsdT4BQilGZQlFueQeg"

def reload_image(file_path=os.path.join(".", "data", "case9 - Copy.xlsx")):
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

    line_info = []
    line_list = pd.read_excel(data, "branch")
    # for index, row in line_list.iterrows():
    #     start = bus_list[bus_list["name"] == row["from_busname"]]
    #     end = bus_list[bus_list["name"] == row["to_busname"]]
    #     line_info.append([[start["x"].iloc[0], start["y"].iloc[0]], [end["x"].iloc[0], end["y"].iloc[0]]])

    hvdc_lines = pd.read_excel(data, "hvdc")
    for index, row in hvdc_lines.iterrows():
        start = bus_list[bus_list["name"] == row["from_busname"]]
        end = bus_list[bus_list["name"] == row["to_busname"]]
        line_info.append([[start["x"].iloc[0], start["y"].iloc[0]], [end["x"].iloc[0], end["y"].iloc[0]]])


    # request_url = "https://api.mapbox.com/styles/v1/mapbox/light-v11/static/[" + str(min_long) + "," + str(min_lat) + ","+ str(max_long) + "," + str(max_lat) + "]/1280x1280?padding=0&access_token=" + access_key
    request_url = "https://api.mapbox.com/styles/v1/mapbox/light-v11/static/" +\
        "geojson({\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"properties\":{\"marker-size\":\"small\",\"marker-symbol\":\"airport\"},\"geometry\":{\"type\":\"MultiLineString\",\"coordinates\":" +\
        str(line_info) + "}}]})" +\
        "/[" + str(min_long) + "," + str(min_lat) + ","+ str(max_long) + "," + str(max_lat) + "]" +\
        "/1280x1280?access_token=" + access_key
    
    print("URL!!!", request_url)
    image = requests.get(request_url)
    with open(os.path.join("data", "image2.png"), 'wb') as f:
        f.write(image.content)


def bbox_corners(bus_list):
    max_long = max(bus_list["x"])
    min_long = min(bus_list["x"]) 
    max_lat = max(bus_list["y"])
    min_lat = min(bus_list["y"])

def coordinate_map(bus_list):
    max_long = max(bus_list["x"])
    min_long = min(bus_list["x"]) 
    max_lat = max(bus_list["y"])
    min_lat = min(bus_list["y"])
    
    long_distance = abs(max_long - min_long)
    lat_distance = abs(max_lat - min_lat)

    pic_length = 1280
    bus_list["long"] = bus_list["x"].apply(lambda x: pic_length/long_distance * (long_distance - (max_long - x)))
    bus_list["lat"] = bus_list["y"].apply(lambda y: pic_length- (pic_length/lat_distance * (lat_distance - (max_lat - y))))
    # print("lat???", pic_length, "-(", pic_length, "/", lat_distance, "* (", lat_distance, "- (", max_lat, "- y")
    # print("long???", pic_length, "/", long_distance, "* (", long_distance, "- (", max_long, "- x")

    # print(bus_list)
    return bus_list



