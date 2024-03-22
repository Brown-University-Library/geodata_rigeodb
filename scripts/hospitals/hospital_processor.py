# -*- coding: utf-8 -*-
"""
Process RIDOH license data  to create spatial layers
for hospitals, using the RIDOT address locator

Output coordinates are in RI State Plane

Frank Donnelly / GIS and Data Librarian / Brown University
Mar 23, 2023, Revised Apr 5, 2023
"""

import csv, os, sys, requests, json, pandas as pd, geopandas as gpd
from datetime import date
from time import sleep

# *** VARIABLES ***

geocode=True # TYPE True to geocode, False to exit to verify addresses are correct

infolder='input_03_2024' # UPDATE input directory
outfolder='output_03_2024'# UPDATE output directory
fixfile='fixed_addresses.json'
today=str(date.today()).replace('-','_')

# Columns in the input file to keep
keepcols=['Name','License No', 'Profession', 'License Type', 'Address Line 1',
          'Address Line 2', 'Address Line 3', 'City',
          'State','Zip', 'Total Capacity Beds']

typecols={'Zip':str}

# *** READING INPUT AND CLEANING ***

# Each file is stored in a df, added to a list, and concatenated into one df
dflist=[]
for dfile in os.listdir(infolder):
    if dfile.endswith('.csv'):
        edfile=os.path.join(infolder,dfile)    
        df=pd.read_csv(edfile,usecols=keepcols,dtype=typecols)
        dflist.append(df)
            
df_all=pd.concat(dflist,axis=0,ignore_index=True)     

# CLEANING
   
print('All records:',df_all.shape[0])
# Remove trailing and leading whitespace
df_all['Name']=df_all['Name'].str.strip()
df_all['Address Line 1']=df_all['Address Line 1'].str.strip()
# Add current year for each record
df_all['year']=today.split('_')[0]

# Read in a file with addresses for records known to not match
with open(fixfile, mode="r") as jfile:
    fix_address = json.load(jfile)

# Replace bad addresses with good ones - look for discrepancies!
df_all['add_orig']=pd.Series(dtype='str') # column to hold bad address
fixfile='fixaddress_report_'+today+'.txt' # file for storing report
for k,v in fix_address.items():
    with open(fixfile,'a') as f:
        if k in df_all['License No'].values:
            # Store the bad address in a new column
            add_cols = ['Address Line 1','City','Zip']
            series_list = [df_all[c] for c in add_cols]
            df_all.loc[df_all['License No'] == k, 'add_orig'] = series_list[0].str.cat(series_list[1:], sep=' ')
            # Update existing address
            print('\n Updating address for record \n',
                  df_all.loc[df_all['License No']==k,['License No','Name','add_orig']].values,
                  '\n To new address:',v['add'],v['city'],v['zip'],'\n',file=f)   
            df_all.loc[df_all['License No'] == k, 'Address Line 1'] = v['add']
            df_all.loc[df_all['License No'] == k, 'City'] = v['city']
            df_all.loc[df_all['License No'] == k, 'Zip'] = v['zip']
print('Wrote address fix list \n')

# *** GEOCODING ***

if geocode is True:
    pass
else:
    print('Geocoding is off, ending program.')
    sys.exit()

matches=[] # Holds geocoded output
multiples=[] # For debugging, saves results from multiple matches
newfields=['uid','match_note','score','match_add','xcoord','ycoord']
matches.append(newfields)

# Geocoding begins here, loop through records in df
base_url_ad='https://risegis.ri.gov/gpserver/rest/services/E911_Sites_AddressLocator/GeocodeServer/findAddressCandidates?'
for idx in df_all.index:
    address=df_all['Address Line 1'][idx].replace('#','')
    city=df_all['City'][idx]
    state=df_all['State'][idx]
    zipcode=df_all['Zip'][idx]
    try:
        add_url=f'Street={address}&City={city}&State={state}&ZIP={zipcode}'
        data_url = f'{base_url_ad}{add_url}&maxLocations=5&matchOutOfRange=true&f=pjson'
        response=requests.get(data_url)
        add_data=response.json()['candidates'] #Collapse the dictionary by one level
        if len(add_data)==0:
            matches.append([idx,'NO MATCHES','','','',''])
        elif len(add_data)==1:
            score=add_data[0]['score']
            matadd=add_data[0]['address']
            x=add_data[0]['location']['x']
            y=add_data[0]['location']['y']    
            matches.append([idx,'ONE MATCH',score,matadd,x,y])
        else:        
            all_scores=[]
            for m in add_data:
                all_scores.append(m['score'])
                multiples.append([idx,m['score'],m['address'],
                                  m['location']['x'],m['location']['y']]) # Keep track of multiples
            maxs=max(all_scores) # Find highest score
            maxs_idx=all_scores.index(maxs) # And its index (takes 1st highest value if several are equal)
            # Get data for highest match and store
            score=add_data[maxs_idx]['score']
            matadd=add_data[maxs_idx]['address']
            x=add_data[maxs_idx]['location']['x']
            y=add_data[maxs_idx]['location']['y']
            matches.append([idx,'MULTIPLE MATCHES',score,matadd,x,y])         
        if idx % 100 == 0:
            print('Geocoded',idx,'records so far...')
            sleep(2)
    except Exception as e:
            print(str(e))
print('Finished geocoding',idx+1,'records','\n')

# Convert match list to df, join to input data using index value
df_match = pd.DataFrame(matches[1:], columns=matches[0]).set_index('uid')
df_final=df_all.join(df_match)

print(df_match.match_note.value_counts())
match_count=df_match['match_note'].value_counts().to_dict()

# This block handles hospitals that have coordinates returned that do a poor job
# of representing the center of the hospital complex.

hosp_xyfix={'HOS00133':{'name':'ROGER WILLIAMS MED CNTR','x':'345765.18902292347','y':'273771.30659775337'},
            'HOS00121':{'name':'RI HOSPITAL','x':'352862.434986831','y':'265450.9228263157'}}

for k, v in hosp_xyfix.items():
    if k in df_final['License No'].values:
        idx = df_final.loc[df_final['License No']==k].index[0]
        df_final.loc[df_final.index == idx, 'xcoord'] = v['x']
        df_final.loc[df_final.index == idx, 'ycoord'] = v['y']
        df_final.loc[df_final.index == idx, 'match_note'] = 'MANUAL MATCH'
        print('Manual fix applied for',v['name'])
    else:
        print('No fix applied for',k,', ID in dictionary not in dframe.')

# Write Output to CSV

colnew={'Name':'name','License No':'license_id','Profession':'factype',
        'License Type':'lictype','Address Line 1':'address1', 
        'Address Line 2':'address2', 'Address Line 3':'address3', 
        'City':'city','State':'state', 'Zip':'zipcode',
        'Total Capacity Beds':'hosp_beds'}

df_final.rename(columns = colnew, inplace = True) # Rename columns to 10 chars or less
df_final.index.name='seqid'
today=str(date.today()).replace('-','_')
outfile='hospitals_ri_'+today+'.csv'
outpath=os.path.join(outfolder,outfile)
df_final.to_csv(outpath)

mfile=outfile.split('.')[0]+'_MULTIPLES.txt'
with open(os.path.join(outfolder,mfile), 'w', newline='') as writefile:
    writer = csv.writer(writefile, quoting=csv.QUOTE_ALL, delimiter=',')
    writer.writerows(multiples)
 
# Create shapefiles and write

if 'NO MATCHES' in match_count: # Must delete records with no matched coordinates
    idxnames=df_final[df_final['match_note'] == 'NO MATCHES'].index
    df_final.drop(idxnames, inplace = True)
    print('*** Warning: unmatched records written to CSV but not to shapefile')
gdf_all = gpd.GeoDataFrame(df_final,geometry=gpd.points_from_xy(df_final['xcoord'],df_final['ycoord']),crs = 'EPSG:3438')
outshape='hospitals_ri_'+today+'.shp'
gdf_all.to_file(os.path.join(outfolder,outshape),index=True)
