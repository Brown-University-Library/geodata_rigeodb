# -*- coding: utf-8 -*-
"""
Process RI Dept of Education Directory Data to create spatial layers
for schools and colleges, using the RIDOT address locator

Output coordinates are in RI State Plane

Frank Donnelly / GIS and Data Librarian / Brown University
Feb 23, 2023
"""

import csv, os, sys, requests, json, pandas as pd, geopandas as gpd
from datetime import date
from time import sleep

# *** VARIABLES ***

process='s' # TYPE c to process colleges, s to process schools
geocode=False # TYPE True to geocode, False to exit to verify addresses are correct

infolder='input_02_2023' # UPDATE input directory
outfolder='output_02_2023'# UPDATE output directory
fixfile='fixed_addresses2.json'

# Columns in the input file to keep
keepcols=['org_ID','parent_ID', 'code', 'name', 'name_short_30',
          'name_short_15', 'org_type_ID', 'org_type',
          'location_address1','location_address2', 'location_city',
          'location_state', 'location_zip', 'grade_span', 'sch_sub_type_ID',
          'sch_sub_type_name', 'source']

typecols={'org_ID':str,'parent_ID':str,'code':str,'location_zip':str}

# *** READING INPUT AND CLEANING ***

# Schools: each file is stored in a df, added to a list, and concatenated into one df
if process=='s':
    fname='schools'
    stypes=['Catholic','CharterSchools','EduDir','Independents']
    dflist=[]
    for dfile in os.listdir(infolder):
        if dfile.endswith('.csv'):
            if dfile.split('_')[4] in stypes:
                edfile=os.path.join(infolder,dfile)
                df=pd.read_csv(edfile,usecols=keepcols,dtype=typecols)
                dflist.append(df)
    df_sch=pd.concat(dflist,axis=0,ignore_index=True)     
# Colleges: drop missing cols, one file to read, replace vanity address value of One
elif process=='c':
    fname='colleges'
    keepcols.remove('grade_span')
    for dfile in os.listdir(infolder):
        if dfile.endswith('.csv'):
            if dfile.split('_')[4] == 'Colleges':
                edfile=os.path.join(infolder,dfile)
                df_sch=pd.read_csv(edfile,usecols=keepcols,dtype=typecols)
                df_sch['location_address1'] = df_sch['location_address1'].str.replace('One','1')
else:
    print('Must specify "c" to process colleges or "s" for schools')
    sys.exit()

# Delete records that are not schools, outside RI, or duplicates (as source is a person directory)    
print('All records:',df_sch.shape[0])
df_sch.drop(df_sch[df_sch.org_type_ID != 2].index, inplace=True)  
print('After dropping non-schools:',df_sch.shape[0]) 
df_sch.drop(df_sch[df_sch.location_state != 'RI'].index, inplace=True)
print('After dropping outside RI:',df_sch.shape[0])
df_sch.drop_duplicates(subset=['org_ID', 'code'], keep='first',inplace=True, ignore_index=True)      
print('After dropping duplicates:',df_sch.shape[0])
# Remove trailing and leading whitespace
df_sch['name']=df_sch['name'].str.strip()
df_sch['location_address1']=df_sch['location_address1'].str.strip()

# Read in a file with addresses for records known to not match
with open(fixfile, mode="r") as jfile:
    fix_address = json.load(jfile)

# Replace bad addresses with good ones - look for discrepancies!
for k,v in fix_address.items():
    if k in df_sch['org_ID'].values:
        print('\n Updating address for record \n',
              df_sch.loc[df_sch['org_ID']==k,['org_ID','name','location_address1']].values,
              '\n to new address:',v['add'],'\n') 
        df_sch.loc[df_sch['org_ID'] == k, 'location_address1'] = v['add']
        df_sch.loc[df_sch['org_ID'] == k, 'location_city'] = v['city']
        df_sch.loc[df_sch['org_ID'] == k, 'location_zip'] = v['zip']
 
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
    address=df_sch['location_address1'][idx]
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

print(df_match.match_note.value_counts())
match_count=df_match['match_note'].value_counts().to_dict()

# *** WRITING OUTPUT ***

colnew={'name_short_30':'name_30','name_short_15':'name_15','org_type_ID':'orgtype_ID',
        'location_address1':'address1','location_address2':'address2', 
        'location_city':'city','location_state':'state', 'location_zip':'zipcode',
        'sch_sub_type_ID':'subtype_ID','sch_sub_type_name':'subtype_nm'}

df_final.rename(columns = colnew, inplace = True) # Rename columns to 10 chars or less
today=str(date.today()).replace('-','_')
outfile=fname+'_ri_'+today+'.csv'
outpath=os.path.join(outfolder,outfile)
df_final.to_csv(outpath, index_label='seqid')

mfile=outfile.split('.')[0]+'_MULTIPLES.txt'
with open(os.path.join(outfolder,mfile), 'w', newline='') as writefile:
    writer = csv.writer(writefile, quoting=csv.QUOTE_ALL, delimiter=',')
    writer.writerows(multiples)
 
# Create shapefile and write

if 'NO MATCHES' in match_count: # Must delete records with no matched coordinates
    idxnames=df_final[df_final['match_note'] == 'NO MATCHES'].index
    df_final.drop(idxnames, inplace = True)
    print('*** Warning: unmatched records were written to CSV but not to shapefile')
gdf_sch = gpd.GeoDataFrame(df_final,geometry=gpd.points_from_xy(df_final['xcoord'],df_final['ycoord']),crs = 'EPSG:3438')
outshape=fname+'_ri_'+today+'.shp'
gdf_sch.to_file(os.path.join(outfolder,outshape))
print('Done, wrote match, multiples, and shape files')