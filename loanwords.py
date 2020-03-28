import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df_complete = pd.read_csv('./data/forms.csv', encoding='utf8')
df = df_complete[['ID', 'Language_ID', 'Parameter_ID', 'Form',
                  'BorrowedScore']]
# print(df.head(10))

concept = dict()
for index, row in df.iterrows():
    if row['BorrowedScore'] > 0.7:
        try:
            concept[row['Parameter_ID']].append(row['Language_ID'])
        except KeyError:
            concept[row['Parameter_ID']] = [row['Language_ID']]

print(len(concept))
print(concept['1-1'])
