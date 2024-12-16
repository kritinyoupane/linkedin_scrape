import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://www.pythonscraping.com/pages/page3.html'

#first requests the given url and get response
response = requests.get(url)

#if we do response.text it is just a string thus we convert string into bs4 object
bsObj = BeautifulSoup(response.text,'html.parser')

header_column = bsObj.find_all("th")
header_list = [column.text.strip() for column in header_column]

items = bsObj.find_all("td")
items_list = [item.text.strip() for item in items]
items_rows = [items_list[i:i+4] for i in range(0,len(items_list),4)]

df = pd.DataFrame(items_rows, columns=header_list)
df = df.drop(columns='Image')

df.to_csv("table_data.csv")

print("CSV file created successfully!")