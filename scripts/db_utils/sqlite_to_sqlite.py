#Copy new tables from temporary SQLite database to permanent one and
#drop old tables from permanent database
#Recreates and renames tables and inserts records to preserve keys and constraints

import sqlite3, os, sys
os.chdir('..')

#MODIFY these values to pull from the right sources
#db1 should be the original db - store in folder above this script
db1='ossdb_2024_05_WORKING.sqlite'
# tabdrop=['c_acs2021_lookup',
#           'c_csubdivs_acs2021_pophous','c_csubdivs_acs2021_socecon',
#           'c_tracts_acs2021_pophous','c_tracts_acs2021_socecon',
#           'c_zctas_acs2021_pophous','c_zctas_acs2021_socecon']
tabdrop=['c_zctas_zbp2021_emp','c_zctas_zbp2021_ind','c_zbp2021_indcodes',
         'c_zip2zcta2022']

#db2 should be the test database
#Keys (k) are the test db table names, values (v) will be the new table names
db2=os.path.join('census_zbp','outputs','testdb.sqlite')
# tabadd={'acs2022_lookup':'c_acs2022_lookup',
#         'county_subdivs_acs2022_pophousing': 'c_csubdivs_acs2022_pophous',
#         'county_subdivs_acs2022_socialecon': 'c_csubdivs_acs2022_socecon',
#         'tracts_acs2022_pophousing': 'c_tracts_acs2022_pophous',
#         'tracts_acs2022_socialecon': 'c_tracts_acs2022_socecon',
#         'zctas_acs2022_pophousing': 'c_zctas_acs2022_pophous',
#         'zctas_acs2022_socialecon': 'c_zctas_acs2022_socecon',
#         }
tabadd={'zbp2021_emp':'c_zctas_zbp2021_emp',
        'zbp2021_ind': 'c_zctas_zbp2021_ind',
        'zbp2021_indcodes': 'c_zbp2021_indcodes',
        'zip2zcta_2022': 'c_zip2zcta2022'}

def table_exists(dbalias,dbname,tablist):
    for t in tablist:
        cur.execute("SELECT name FROM {}.sqlite_master WHERE type='table' AND name = '{}'".format(dbalias,t))
        tabgrab = cur.fetchone()
        if tabgrab == None:
            print('There is no table in',dbname,'named',t)
            print('EXITING PROGRAM, no changes made \n')
            con.close()
            sys.exit(0)
        else:
            pass

#Main script begins here
con = sqlite3.connect(db1)
cur = con.cursor()

cur.execute("ATTACH '{}' AS db2;".format(db2))

#Check to make sure tables exist / are spelled correctly in both dbs
table_exists('main',db1,tabdrop)
table_exists('db2',db2,tabadd.keys())

print('You are about to drop the following tables from',db1)
for i in tabdrop:
    print(i) 
print('\nAnd add these tables from',db2)
for j in tabadd.keys():
    print(j) 
answer = input('Are you sure you want to do this? (y/n): ')

if answer=='y':
    for t in tabdrop:
        cur.execute('DROP TABLE {};'.format(t))
        print('Dropped table',t)
    for k, v in tabadd.items():
        cur.execute("SELECT sql FROM db2.sqlite_master WHERE type='table' AND name = '{}';".format(k))
        create = cur.fetchone()[0].replace(k,v)
        cur.execute("SELECT * FROM db2.{};".format(k))
        rows=cur.fetchall()
        colcount=len(rows[0])
        pholder='?,'*colcount
        newholder=pholder[:-1]
        cur.execute(create)
        cur.executemany("INSERT INTO {} VALUES ({});".format(v, newholder),rows)
        con.commit() 
        print('Added table',v)
else:
    print('\nEXITING PROGRAM, no changes made \n')
    con.close()
    sys.exit(0)
    
con.commit()
con.close()
