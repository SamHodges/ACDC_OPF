from tkinter import *
import pandas as pd
import os
import visual

ws = Tk()
data = pd.ExcelFile(os.path.join(".", "data", "case9.xlsx"))
demand_data = pd.read_excel(data, 'demand')



# Make the Entry widgets and make a list of them.
entries = []

# for i in range(8):
#     e = Entry(ws)
#     e.pack()
#     entries.append(e)


def callback(demand_data):
    # contents = []
    # for e in entries:
    #     contents.append(e.get())
    # print(contents)
    real_power = input("Real Power: ")
    reactive_power = input("Reactive Power: ")
    stat = input("Stat: ")
    voll = input("VOLL: ")
    new_demand = pd.DataFrame(["D4", 10, real_power, reactive_power, stat, voll]).T
    demand_data = pd.concat([demand_data, new_demand], ignore_index=True)
    print(demand_data)




b = Button(ws, text = "Add Demand", width = 10, command = callback(demand_data))
b.pack()

# e.focus_set()



mainloop()


