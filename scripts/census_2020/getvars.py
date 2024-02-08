# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 11:54:59 2022

Example of reading variables from census website, and writing and reading to CSV
"""

import requests,csv

#Set variables
year='2020'
dsource='dec'
dname='dp'
varfile=dsource+year+dname+'_variables.csv'
#varfile1=dsource1+dsource2+year+dname+'_variables1.csv'

vars_url=f'https://api.census.gov/data/{year}/{dsource}/{dname}/variables.json'
response=requests.get(vars_url)

#"variables" is top key in the file - reference it to flatten the file so individual variables become keys 
variables=response.json()['variables']
variables

#Get the info we want out of the nested dictionaries into a nested list
vlist=[]
for k,v in variables.items(): 
    record=[]
    record.append(k)
    if v['label'].startswith('Count!!') or v['label'].startswith('Percent!!'):
        record.append(v['concept'])
        record.append(v['label'])
        record.append(v['predicateType'])
        vlist.append(record)
    else:
        pass

slist=sorted(vlist)
 
#Write out nested list to CSV    
with open(varfile, 'w', newline='') as writefile:
    writer = csv.writer(writefile, quoting=csv.QUOTE_ALL, delimiter=',')
    writer.writerows(slist)

#Read certain variables back in from CSV to nested list
# keepvars=[]
# with open(varfile1, 'r', newline='') as readfile:
#     reader = csv.reader(readfile, quoting=csv.QUOTE_ALL, delimiter=',')
#     for record in reader:
#         if record[0]=='1':
#             keepvars.append(record[1])
#     else:
#         pass



