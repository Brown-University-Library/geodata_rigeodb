# -*- coding: utf-8 -*-
"""
Process IMLS public library outlet data  to create spatial layers
for libraries, using the RIDOT address locator

Output coordinates are in RI State Plane

Frank Donnelly / GIS and Data Librarian / Brown University
Mar 28, 2023, revised Apr 3, 2023
"""

import csv, os, sys, requests, json, pandas as pd, geopandas as gpd
from datetime import date
from time import sleep

# *** VARIABLES ***

geocode=True # TYPE True to geocode, False to exit to verify addresses are correct

infolder='input_pls_fy2021_csv' # UPDATE input directory
outfolder='output_pls_fy2021_csv'# UPDATE output directory
fixfile='fixed_addresses.json'
today=str(date.today()).replace('-','_')

# Columns in the input file to keep
keepcols=['STABR','FSCSKEY', 'FSCS_SEQ', 'LIBID',
          'LIBNAME', 'ADDRESS', 'CITY', 'ZIP', 'CNTY',
          'C_OUT_TY','SQ_FEET', 'F_SQ_FT', 'HOURS', 'F_HOURS',
          'WKS_OPEN', 'F_WKSOPN','YR_SUB','LOCALE']

typecols={'FSCS_SEQ':str,'ZIP':str, 'LOCALE':str}

# *** READING INPUT AND CLEANING ***

# Each file is stored in a df, added to a list, and concatenated into one df

for dfile in os.listdir(infolder):
    if dfile.split('_')[2] == 'outlet':
        libfile=os.path.join(infolder,dfile)    
        df_all=pd.read_csv(libfile,usecols=keepcols,dtype=typecols,encoding_errors='ignore')

# CLEANING
   
print('All records:',df_all.shape[0])
df_all.drop(df_all[df_all.STABR != 'RI'].index, inplace=True) # Not in RI
print('After dropping outside RI:',df_all.shape[0])
# Not central CE or branch BR libraries (drop bookmobiles BS and Books by mail BM)
df_all.drop(df_all[df_all.C_OUT_TY.isin(['BS','BM'])].index, inplace=True)  
print('After bookmobiles and books by mail:',df_all.shape[0]) 
df_all.reset_index(drop=True, inplace=True)
# Remove trailing and leading whitespace
df_all['LIBNAME']=df_all['LIBNAME'].str.strip()
df_all['ADDRESS']=df_all['ADDRESS'].str.strip()

# Read in a file with addresses for records known to not match
with open(fixfile, mode="r") as jfile:
    fix_address = json.load(jfile)

# # Replace bad addresses with good ones - look for discrepancies!
df_all['add_orig']=pd.Series(dtype='str') # column to hold bad address
fixfile='fixaddress_report_'+today+'.txt' # file for storing report
for k,v in fix_address.items():
    with open(fixfile,'a') as f:
        if k in df_all['LIBID'].values:
            # Store the bad address in a new column
            add_cols = ['ADDRESS','CITY','ZIP']
            series_list = [df_all[c] for c in add_cols]
            df_all.loc[df_all['LIBID'] == k, 'add_orig'] = series_list[0].str.cat(series_list[1:], sep=' ')
            # Update existing address
            print('\n Updating address for record \n',
                  df_all.loc[df_all['LIBID']==k,['LIBID','LIBNAME','add_orig']].values,
                  '\n To new address:',v['add'],v['city'],v['zip'],'\n',file=f)   
            df_all.loc[df_all['LIBID'] == k, 'ADDRESS'] = v['add']
            df_all.loc[df_all['LIBID'] == k, 'CITY'] = v['city']
            df_all.loc[df_all['LIBID'] == k, 'ZIP'] = v['zip']
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
    address=df_all['ADDRESS'][idx].replace('#','')
    city=df_all['CITY'][idx]
    state=df_all['STABR'][idx]
    zipcode=df_all['ZIP'][idx]
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

# Write Output to CSV

newcols={}
for c in list(df_final):
    newcols[c]=c.lower()
df_final.rename(columns = newcols, inplace = True) # Rename columns to 10 chars or less
df_final.index.name='seqid'
today=str(date.today()).replace('-','_')
outfile='public_libraries_ri_'+today+'.csv'
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
outshape='public_libraries_ri_'+today+'.shp'
gdf_all.to_file(os.path.join(outfolder,outshape),index=True)
