# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:00:44 2022

@author: ACER
"""
# Import Necessary Libraries
import pandas as pd
import os

# Task #1: Merge data from each month into one CSV
path = "C:/Users/ACER/Downloads/Pandas-Data-Science-Tasks-master/SalesAnalysis/Sales_Data"
files = [file for file in os.listdir(path) if not file.startswith('.')] # Ignore hidden files

all_months_data = pd.DataFrame()

for file in files:
    current_data = pd.read_csv(path+"/"+file)
    all_months_data = pd.concat([all_months_data, current_data])
    
all_months_data.to_csv("all_data.csv", index=False)    
# Task #2: Read in updated dataframe
all_data = pd.read_csv("all_data.csv")

#****************************************************************************#
# Clean the data

# Find NAN
nan_df = all_data[all_data.isna().any(axis=1)]
all_data = all_data.dropna(how='all')

# Get rid of text in order date column
all_data = all_data[all_data['Order Date'].str[0:2]!='Or']

# Make columns correct type
all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])
all_data['Price Each'] = pd.to_numeric(all_data['Price Each'])

#****************************************************************************#
# Augment data with additional columns

# Task#1: Add Month column
all_data['Month'] = all_data['Order Date'].str[0:2]
all_data['Month'] = all_data['Month'].astype('int32')

# Task#2: Add Sales column
all_data['Sales'] = all_data['Quantity Ordered'].astype('int')*all_data['Price Each'].astype('float')
sales_monthly = all_data.groupby(['Month']).sum()

# Task#3: Add City column
def get_city(address):
    return address.split(",")[1].strip(" ")

def get_state(address):
    return address.split(",")[2].split(" ")[1]

all_data['City'] = all_data['Purchase Address'].apply(lambda x: f"{get_city(x)}({get_state(x)})")

#****************************************************************************#
# EDA Analysis
import seaborn as sns
import matplotlib.pyplot as plt

# Question 1: What was the best month for sales? How much was earned that month?
temp2 = all_data.groupby(['Month']).sum()['Sales'].reset_index()
Months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 
          'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax = sns.barplot(x=Months, y="Sales", 
            data=temp2, order=Months, palette='Set3')
plt.ticklabel_format(style='plain', axis='y')
ax.set(xlabel='Month', ylabel='Sales in USD ($)')

# Question 2: What city had the highest number of sales?
result = all_data.groupby('City').sum().reset_index()
sns.set(rc={'figure.figsize':(10,12)})
ax = sns.barplot(y="City",x="Sales", data=result,palette="GnBu_d", 
            order=result.sort_values('Sales',ascending = False).City)
plt.ticklabel_format(style='plain', axis='x')
ax.set(xlabel='Sales in USD ($)')

# Question 3: What time should we display advertisemens to maximize the likelihood of customer’s buying product?
# Extract hour and minute
all_data['Order Date'] = pd.to_datetime(all_data["Order Date"])
all_data['Hour'] = all_data['Order Date'].dt.hour
all_data['Minute'] = all_data['Order Date'].dt.minute

temp = all_data.groupby('Hour').count().reset_index()
ax = sns.relplot(
    data=temp, 
    x="Hour", y="Sales", 
    kind="line",
    height=5, aspect=2 
)
plt.xticks(temp["Hour"])
ax.set(ylabel='Number of Orders')

# Question 4: What products are most often sold together?
df = all_data[all_data["Order ID"].duplicated(keep=False)]
df["Grouped"] = df.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))
df = df[['Order ID','Grouped']].drop_duplicates(keep='first')

from itertools import combinations
from collections import Counter 

count = Counter()
for row in df["Grouped"]:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))
    
lst = []
lst2 = []   
for key, value in count.most_common(10):
    lst.append(key)
    lst2.append(value)

lst1 = [', '.join(map(str, x)) for x in lst]
    
Grouped_products = pd.DataFrame(list(zip(lst1, lst2)),
               columns =['Group of Product', 'Count'])

ax1 = sns.barplot(x='Count', y='Group of Product',palette="rocket",
                  data=Grouped_products.reset_index())

# Question 5: What product sold the most? Why do you think it sold the most?
product_group = all_data.groupby('Product').sum().reset_index()
product_group = product_group.sort_values(by="Quantity Ordered")

prices = all_data.groupby('Product').mean()['Price Each'].reset_index()

ax2 = sns.barplot(data=product_group, x="Product", y="Quantity Ordered", 
            palette='crest', ci=None)
ax2.set_xticklabels(ax2.get_xticklabels(),rotation = 90)
ax3 = ax2.twinx()
sns.lineplot(color='maroon',ax=ax3,data=prices['Price Each'])
ax2.set_xlabel('Product Name')
ax2.set_ylabel('Quantity Ordered', color = 'midnightblue')
ax3.set_ylabel('Price ($)', color = 'maroon')


