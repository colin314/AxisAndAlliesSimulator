import pandas as pd
from colorama import Fore

print ('|' + '1'.rjust(10," ") + '|')
print ('|' + '1'.ljust(10," ") + '|')

df = pd.DataFrame({'Count': [1, 5, 6]}, index=["Infantry", "Artillery", "Tank"])

df2 = pd.DataFrame({'Count': [1, 5, 6]}, index=["Infantry", "Artillery", "Tank"])

dfJoin = pd.concat([df, df2], axis=1, join="outer", keys=["Before", "After"])
print(dfJoin)
print('Applying Formatting')
#dfJoin.loc[:,'Count'] = dfJoin['Before']['Count'].apply(lambda x: x + 1) #(lambda x: str(x) + " " + Fore.WHITE + ( '█' * x ) + ' ')
dfJoin.columns = [f"{i}" for i, j in dfJoin.columns]
dfJoin['Before'] = dfJoin['Before'].apply(lambda x: str(x) + " " + Fore.WHITE + ( '█' * x ) + ' ')
dfJoin['After'] = dfJoin['After'].apply(lambda x: str(x) + " " + Fore.WHITE + ( '█' * x ) + ' ')


print(dfJoin)
df = dfJoin.infer_objects(copy=False).fillna(0).reset_index()
print(df)
#df.Count = df.Count.astype(int)