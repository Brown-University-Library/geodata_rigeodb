---
# TITLE
dct_title_s: Ocean State Spatial Database, Rhode Island, 2023

# DESCRIPTION
dct_description_sm:
- The Ocean State Spatial Database (OSSDB) is a geodatabase created by the Brown University Library for conducting basic geographic analysis and thematic mapping within the State of Rhode Island. It is intended to serve as a basic foundation for contemporary mapping projects, and as an educational tool for supporting GIS coursework and introducing spatial databases and SQL. It contains geographic features and data compiled from several public sources. A subset of the Census Bureau's TIGER/LINE water features were used to create a base map of coastal water, which was used to clip and create land-based areas for census geographies including counties, county subdivisions, census tracts, and ZCTAs. Census data from the 2020 Census and American Community Survey (ACS) are stored in tables that can be easily related to geographic features. Point data for public facilities like schools and libraries were gathered from several state and federal agencies and transformed into spatial data that can be used for reference mapping, or analysis for measuring distance, drawing buffers, or counting features within areas. Objects in the database are labelled with a prefix that groups them into categories - 'a' objects are land-area features to be used for thematic mapping, 'b' objects are boundaries for reference mapping, 'c' objects are census data tables that can be joined to 'a' features, and 'd' objects consist of other point, line, and polygon features.  The data is appropriate for thematic mapping at a state, county, and town-level, and reference mapping at a state and county level. While it can be used for creating reference maps at the town level, it is not ideal for this purpose given the degree of generalization in the TIGER/LINE files. All of the features were transformed to share a common coordinate reference system, Rhode Island State Plane (ft-US), EPSG 3438.

# LANGUAGE
dct_language_sm:
- eng

# CREATOR
dct_creator_sm:
- Brown University Library

# PUBLISHER
dct_publisher_sm:
- Brown University Library
- U.S. Census Bureau
- Institute of Museum and Library Services
- Rhode Island Department of Education
- Rhode Island Department of Health
- Rhode Island Department of Transportation
- OpenStreetMap

# PROVIDER
schema_provider_s: Brown

# RESOURCE CLASS
gbl_resourceClass_sm: 
- Datasets

# RESOURCE TYPE
gbl_resourceType_sm:
- Polygon data
- Point data
- Line data
- Table data

# LC SUBJECT
dct_subject_sm:
- Geographic information systems
- Geospatial data
- Population geography

# ISO THEME
dcat_theme_sm:
- Boundaries
- Economy
- Health
- Society
- Structure
- Transportation

# TEMPORAL
dct_temporal_sm:
- '2023'
- 21st century

# DATE ISSUED
dct_issued_s: '2023-07'

# SPATIAL
dct_spatial_sm:
- Rhode Island, United States

# BOUNDING BOX
dcat_bbox: 'ENVELOPE(-71.9073,-71.0886,42.0189,41.0958)'

# RIGHTS
dct_rights_sm: 
- The data are licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. You are free to share and to adapt the work as long as you cite the source, do not use it for commercial purposes, and release adaptations under the same license.
- Disclaimer. Every effort was made to insure that the data, which was compiled from public sources, was processed and presented accurately. The creators and Brown University disclaim any liability for errors, inaccuracies, or omissions that may be contained therein or for any damages that may arise from the foregoing. Users should independently verify the accuracy and fitness of the data for their purposes.

# LICENSE
dct_license_sm:
- https://creativecommons.org/licenses/by-nc-sa/4.0/

# ACCESS RIGHTS
dct_accessRights_s: Public

# FILE FORMAT
dct_format_s: SQLite

# UNIQUE ID
id: brown-11182022AAC

# IDENTIFIER
dct_identifier_sm:
- https://github.com/Brown-University-Library/geodata_ossdb

# METADATA MODIFIED
gbl_mdModified_dt: '2023-07-12'

# METADATA VERSION
gbl_mdVersion_s: Aardvark

# GEOREFERENCED
gbl_georeferenced_b: True