import pandas as pd
from Simulator import Simulator

arr1 = {'HP_1':[4,3,2,1,0],'Hits_1':[8,6,4,2,0]}
arr2 = {'HP_2':[3,2,1],'Hits_2':[9,6,3]}
arr = [arr1, arr2]

df = pd.DataFrame([arr1, arr2])

exit()
df = pd.DataFrame(arr1)
df2 = pd.DataFrame(arr2)

print(df.columns.values)

df = pd.concat([df, df2],axis=1)# ,names=[*df.columns.values,*df2.columns.values])
df = df.fillna(0)
print(df)