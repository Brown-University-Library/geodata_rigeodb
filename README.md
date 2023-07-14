# Ocean State Spatial Database

## Introduction

The Ocean State Spatial Database (OSSDB) is a geodatabase created by the Brown University Library [GeoData@SciLi](https://libguides.brown.edu/geodata/) team, for conducting basic geographic analysis and thematic mapping within the State of Rhode Island. It is intended to serve as a basic foundation for contemporary mapping projects, and as an educational tool for supporting GIS coursework and introducing spatial databases and SQL. It contains geographic features and data compiled from several public sources. A subset of the Census Bureau's TIGER/LINE water features were used to create a base map of coastal water, which was used to clip and create land-based areas for census geographies including counties, county subdivisions, census tracts, and ZCTAs. Census data from the 2020 Census and American Community Survey (ACS) are stored in tables that can be easily related to geographic features. Point data for public facilities like schools and libraries were gathered from several state and federal agencies and transformed into spatial data that can be used for reference mapping, or analysis for measuring distance, drawing buffers, or counting features within areas. Objects in the database are labelled with a prefix that groups them into categories:

- 'a' objects are land-area features to be used for thematic mapping

- 'b' objects are boundaries for reference mapping

- 'c' objects are census data tables that can be joined to 'a' features

- 'd' objects consist of other point, line, and polygon features. 

The data is appropriate for thematic mapping at a state, county, and town-level, and reference mapping at a state and county level. While it can be used for creating reference maps at the town level, it is not ideal for this purpose given the degree of generalization in the TIGER/LINE files. All of the features were transformed to share a common coordinate reference system, Rhode Island State Plane (ft-US), EPSG 3438.

This repository includes the spatial database in a SQLite / Spatialite format and an ESRI file geodatabase format, metadata in the OSM Aardvark standard, documentation, and Python scripts for generating certain data layers and tables that will be updated annually.

## Rights and Use

The database and associated documentation are licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/) CC BY-NC-SA ![CC BY-NC-SA](/images/cc_license.png). You are free to share and to adapt the work as long as you cite the source, do not use it for commercial purposes, and release adaptations under the same license.

*Disclaimer: Every effort was made to insure that the data, which was compiled from public sources, was processed and presented accurately. The creators and Brown University disclaim any liability for errors, inaccuracies, or omissions that may be contained therein or for any damages that may arise from the foregoing. Users should independently verify the accuracy and fitness of the data for their purposes.*

## Downloads

<u>CURRENT VERSION</u>: ossdb_2023_07

- [OSSDB SQLite](https://github.com/Brown-University-Library/geodata_ossdb/raw/main/current_db/ossdb_sqlite.zip): the primary database, a SQLite / Spatialite database that can be used in desktop GIS packages such as QGIS and ArcGIS Pro, and SQL database tools like the QGIS DB Manager, Spatialite GUI, and DB Browser for SQLite

- [OSSDB File Geodatabase](https://github.com/Brown-University-Library/geodata_ossdb/raw/main/current_db/ossdb_esri_gdb.zip): a copy of the database in the ESRI File Geodatabase format, which can be edited in ArcGIS Pro (the Spatialite format in ArcGIS Pro is read only)

- [Summary](https://raw.githubusercontent.com/Brown-University-Library/geodata_ossdb/main/current_db/bul_ossdb_summary.pdf): a two-page summary of the database with instructions on how to connect to it in QGIS and ArcGIS Pro (included with the database download)

- [Documentation](https://raw.githubusercontent.com/Brown-University-Library/geodata_ossdb/main/current_db/bul_ossdb_guide.pdf): in-depth documentation that describes database updates, contents, structure, and instructions for accessing via GIS and database software (included with the database download)

- [Metadata](https://github.com/Brown-University-Library/geodata_ossdb/tree/main/current_db/metadata): one record for each feature and table in the database; click on the markdown (.md) copy for a readable version (included with the database download)

## Features

- State, counties, county subdivisions (cities and towns), ZIP Code Tabulation Areas (ZCTAs), census tracts, census tract population centroids. "a" features for thematic mapping.

- Legal / statistical boundaries for the same areas. "b" features for reference mapping.

- 5-year American Community Survey (ACS) socio-economic, population, and housing tables (updated annually), and 2020 census tables for county subdivisions, ZCTAs, and tracts. Variables can be identified using the lookup table for each dataset. Each ACS variable comes with four columns: an estimate, a margin of error, a percent total, and a margin of error for the percent total. "c" tables can be joined to "a" features using GEOIDLONG columns.

- Point features for colleges and universities, preK-12 schools, public libraries, and hospitals. "d" features updated annually.

- Roads, passenger railroads, train stations, major lakes and rivers, coastal water, the Narragansett Reservation. "d" features.

## Connect with QGIS

1. Download the OSSDB for SQLite file, move it to a folder, and unzip the zip file.

2. In the QGIS *Browser panel*, scroll down to the *Spatialite* option. Select it, right click, and choose *New Connection*. Browse to the folder where the ossdb.sqlite database is located, select it, and hit *Open* to establish a connection.

3. In the *Browser panel*, hit the dropdown arrow beside the *Spatialite* option, and then the dropdown arrow below the database to see the layers and tables.

4. Click on a layer or table to select it, hold down the left mouse button, and drag it into the map view to add it to your project.

5. You can overlay and symbolize the layers (right click on the layer in the *Layers panel -* *Properties - Symbology*), view attributes (right click on layer, choose *Open Attribute Table*) and use the analytical tools in the menus and toolbars just like you would any other vector layer.

6. To interpret the data in the "c" census data tables, add the lookup table to the project, and open it as an attribute table. This table correlates variable identifiers with variable names. To map the data, add the table and its matching geospatial "a" feature to a project. Select the "a" feature in the *Layers panel*, right click, and choose *Properties*. On the *Joins tab*, hit the green plus symbol to add a new join. Join the "c" table to the "a" feature using the GEOIDLONG identifier that they share in common. Confirm the join, and then you can access the *Symbology tab* of the "a" features to make a graduated area map from columns stored in the "c" table.
   
   ![QGIS](/images/qgis_example.png)

## Connect with QGIS DB Manager

1. Follow steps 1 and 2 in the previous section.

2. On the menu bar, choose *Database - DB Manager*.

3. In the *Providers menu* on the left, hit the dropdown arrow beside the *Spatialite* option, and the dropdown arrow beside the database to see the layers and tables. The objects that appear prior to the "a" features are internal system tables that you can ignore.

4. Click on a layer or table to select it, making it active. The window on the right will display metadata about the layer and how it was created (*Info tab*), the records in the attribute table (*Table tab*), and a preview of the feature's geometry (*Preview tab*).

5. You can add a layer or table to a project by selecting it in the *Providers menu*, right clicking, and choosing *Add to Canvas*.

6. The *SQL Window* button at the top will allow you to execute SQL and spatial SQL queries. Hit the button, and type your SQL query in the top window. Hit the *Execute* button to see the results in the bottom menu. You can load the result as a new, temporary layer to the map window to view it, and can save the result either as a view or a new table in the database.

![QGIS DB Manager](/images/qgis_dbm_example.png)

## Connect with ArcGIS Pro

1. Download the OSSDB File Geoadatabase, move it to a folder, and unzip the zip file. You may want to store the database in your user\documents\ArcGIS folder, as that's the default location for project files.

2. In ArcGIS Pro, use the *Catalog pane* (*View - Catalog Pane*), select the *Databases object*, right click and choose *Add Database*. Navigate to the folder where the database is stored, select it, and hit *OK* to establish a connection. 

3. In the *Catalog pane*, hit the dropdown arrow beside the *Database object*, and then the dropdown arrow below the database to see the layers and tables.

4. Click on a layer or table to select it, hold down the left mouse button, and drag it into the *Map panel* to add it to your project. 

5. You can overlay and symbolize the layers (right click on the layer in the *Contents pane -  symbology*), view attributes (right click on layer, choose *Attribute Table*) and use the analytical tools in the menus and toolbars just like you would any other vector layer.

6. To interpret the data in the "c" census data tables, add the lookup table to the project, and open it as an attribute table. This table correlates variable identifiers with variable names. To map the data, add the table and its matching geospatial "a" feature to a project. Select the "a" feature in the *Contents pane*, right click, and choose* Joins and Relates - Joins*. Join the "c" table to the "a" feature using the GEOIDLONG identifier that they share in common. Confirm the join, and then you can access the *Symbology* of the "a" features to make a graduated area or symbol map from columns stored in the "c" table.

![ArcGIS Pro](/images/arcgis_example.png)
