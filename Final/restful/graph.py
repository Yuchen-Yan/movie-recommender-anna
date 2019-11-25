import numpy as np  
import matplotlib.mlab as mlab  
import matplotlib.pyplot as plt  
import pandas as pd
    # draw a graph
df_report = pd.read_csv("log.csv")
df_data = df_report.groupby(['request_url'],as_index=False)['request_url'].agg({'cnt':'count'})
df_data['request_url'] = df_data['request_url'].str.replace("http://127.0.0.1:5000","")
label = df_data['request_url'].to_list()
number =  df_data['cnt'].to_list()
fig = plt.figure()
plt.pie(number,labels=label)
plt.title("Pie chart")
plt.show()