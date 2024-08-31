import pandas as pd

xl = pd.read_excel("UnitProfiles.xlsx",sheet_name="BasicD12",index_col=0)
print(xl['Unit'])
print(xl[xl["Unit"]=="Infantry"][["Attack","Defense"]])