# -*- coding: utf-8 -*-
"""
Process RI Dept of Education Directory Data to create spatial layers
for schools and colleges, using the RIDOT address locator

Output coordinates are in RI State Plane

Frank Donnelly / Head of GIS & Data Services / Brown University Library
Mar 15, 2023 revised Mar 19, 2024
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
keepcols=['org_ID','parent_ID', 'code', 'name', 'name_short_30',
          'name_short_15', 'org_type_ID', 'org_type',
          'location_address1','location_address2', 'location_city',
          'location_state', 'location_zip', 'grade_span', 'sch_sub_type_ID',
          'sch_sub_type_name', 'source']

unicols=keepcols.copy() # Colleges and Ind Higher Ed don't have grade span column
unicols.remove('grade_span')

typecols={'org_ID':str,'parent_ID':str,'code':str,'location_zip':str, 'sch_sub_type_ID':str}

# *** READING INPUT AND CLEANING ***

# Each file is stored in a df, added to a list, and concatenated into one df
stypes=[]
dflist=[]
for dfile in os.listdir(infolder):
    if dfile.endswith('.csv'):
        stype=(dfile.split('_')[4]) # Portion of file name indicating school type
        stypes.append(stype)
        edfile=os.path.join(infolder,dfile)
        if stype in ['Colleges','IndependentHigherEd']:
            ucols=unicols # Use column list without grade span
        else:
            ucols=keepcols      
        df=pd.read_csv(edfile,usecols=ucols,dtype=typecols)
        df['reptsource']=stype
        # Fix vanity addresses begining with One instead of 1
        df['location_address1'] = df['location_address1'].str.replace('One','1')
        dflist.append(df)
            
df_all=pd.concat(dflist,axis=0,ignore_index=True)     

# CLEANING - Subset records
   
print('All records:',df_all.shape[0])
df_all.drop(df_all[df_all.org_type_ID != 2].index, inplace=True)  # Not schools
print('After dropping non-schools:',df_all.shape[0]) 
df_all.drop(df_all[df_all.location_state != 'RI'].index, inplace=True) # Not in RI
print('After dropping outside RI:',df_all.shape[0])
#  Have to handle Metro Career differently, as multiple campuses have same ID
dfmetro=df_all.loc[df_all['org_ID']=='1521'].copy(deep=True)
df_all.drop(df_all.loc[df_all['org_ID']=='1521'].index, inplace=True)
dfmetro.drop_duplicates(subset=['location_address1','location_address2'],keep='first',inplace=True)
# Drop duplicate ID records, data comes from a directory with repeats for differemt admins
df_all.drop_duplicates(subset=['org_ID', 'code'], keep='first',inplace=True)
df_sch=pd.concat([df_all,dfmetro],ignore_index=True) # After handling dupes, recombine metro with others     
print('After dropping duplicates:',df_sch.shape[0])
# Remove trailing and leading whitespace
df_sch['name']=df_sch['name'].str.strip()
df_sch['location_address1']=df_sch['location_address1'].str.strip()

# Read in a file with addresses for records known to not match
with open(fixfile, mode="r") as jfile:
    fix_address = json.load(jfile)

# Replace bad addresses with good ones - look for discrepancies!
df_sch['add_orig']=pd.Series(dtype='str') # column to hold bad address
fixfile='fixaddress_report_'+today+'.txt' # file for storing report
for k,v in fix_address.items():
    with open(fixfile,'a') as f:
        if k in df_sch['org_ID'].values:
            # Store the bad address in a new column
            add_cols = ['location_address1','location_city','location_zip']
            series_list = [df_sch[c] for c in add_cols]
            df_sch.loc[df_sch['org_ID'] == k, 'add_orig'] = series_list[0].str.cat(series_list[1:], sep=' ')
            # Update existing address
            print('\n Updating address for record \n',
                  df_sch.loc[df_sch['org_ID']==k,['org_ID','name','add_orig']].values,
                  '\n To new address:',v['add'],v['city'],v['zip'],'\n',file=f)
            
            df_sch.loc[df_sch['org_ID'] == k, 'location_address1'] = v['add']
            df_sch.loc[df_sch['org_ID'] == k, 'location_city'] = v['city']
            df_sch.loc[df_sch['org_ID'] == k, 'location_zip'] = v['zip']
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
for idx in df_sch.index:
    address=df_sch['location_address1'][idx].replace('#','')
    city=df_sch['location_city'][idx]
    state=df_sch['location_state'][idx]
    zipcode=df_sch['location_zip'][idx]
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
df_final=df_sch.join(df_match)

# This block handles missing RI E911 address for Warwick Neck School
# DELETE in future if system is updated with this address
if '1299' in df_final['org_ID'].values:
    idx = df_final.loc[df_final['org_ID']=='1299'].index[0]
    if 'NO MATCHES' in df_final.loc[df_final.index==idx].values:
        df_final.loc[df_final.index == idx, 'xcoord'] = '361389'
        df_final.loc[df_final.index == idx, 'ycoord'] = '221204'
        df_final.loc[df_final.index == idx, 'match_note'] = 'MANUAL MATCH'
        print('Manual fix applied for Warwick Neck School')
    else:
        print('No fix applied for Warwick Neck School: already has a matching address.')
else:
    print('No fix applied for Warwick Neck School: record not in the dataset.')

# Get summary of match counts
print(df_final.match_note.value_counts())
match_count=df_final['match_note'].value_counts().to_dict()

# Write Output to CSV

colnew={'name_short_30':'name_30','name_short_15':'name_15','org_type_ID':'orgtype_ID',
        'location_address1':'address1','location_address2':'address2', 
        'location_city':'city','location_state':'state', 'location_zip':'zipcode',
        'sch_sub_type_ID':'subtype_ID','sch_sub_type_name':'subtype_nm'}

df_final.rename(columns = colnew, inplace = True) # Rename columns to 10 chars or less
df_final.index.name='seqid'
today=str(date.today()).replace('-','_')
outfile='schools_ri_'+today+'.csv'
outpath=os.path.join(outfolder,outfile)
df_final.to_csv(outpath)

mfile=outfile.split('.')[0]+'_MULTIPLES.txt'
with open(os.path.join(outfolder,mfile), 'w', newline='') as writefile:
    writer = csv.writer(writefile, quoting=csv.QUOTE_ALL, delimiter=',')
    writer.writerows(multiples)
 
# Create shapefiles and write

slist=['1','3','4','5','6','7','11','12','22','23'] # codes pk-12 schools
clist=['9','10','24'] # codes colleges and universities

if 'NO MATCHES' in match_count: # Must delete records with no matched coordinates
    idxnames=df_final[df_final['match_note'] == 'NO MATCHES'].index
    df_final.drop(idxnames, inplace = True)
    print('*** Warning: unmatched records written to CSV but not to shapefile')
gdf_sch = gpd.GeoDataFrame(df_final,geometry=gpd.points_from_xy(df_final['xcoord'],df_final['ycoord']),crs = 'EPSG:3438')
outshape='schools_ri_'+today+'.shp'
gdf_sch.to_file(os.path.join(outfolder,outshape))

# Shapefiles for subsets of schools, pk12 and colleges
gdf_pk12=gdf_sch.loc[gdf_sch['subtype_ID'].isin(slist)]
outshape='schools_pk12_ri_'+today+'.shp'
gdf_pk12.to_file(os.path.join(outfolder,outshape))
gdf_col=gdf_sch.loc[gdf_sch['subtype_ID'].isin(clist)]
outshape='colleges_ri_'+today+'.shp'
gdf_col.to_file(os.path.join(outfolder,outshape))
print('Done, wrote match, multiples, and shape files')