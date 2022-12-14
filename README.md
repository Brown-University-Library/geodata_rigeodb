# RI Geodatabase 
This repository includes a collection of scripts used to generate layers and census data tables for the RI Geodatabase, which is a collection of spatial layers and attributes for mapping and analyzing data in Rhode Island.

Most of the database layers are relatively static and only need to be updated once every ten years, as they are based on the decennial TIGER Line files and census data.  Some features are updated on an annual basis, where older data is swapped for the most recent release.  Scripts for these layers will be included in this repo:

1) Point features from that include colleges, libraries, hospitals, private schools, and public schools.

2) 5-year Census American Community Survey data for census tracts, Zip Code Tabulation Areas (ZCTAs) and County Subdivisions.

3) Census ZIP Code Business Patterns data that includes total counts of establishments, employees, and wages, and counts of establishments by two-digit sector level NAICS codes at the ZCTA level (the script aggregates source data from ZIP Code-level).

Geodatabase features and tables that are meant to be updated every ten years were created manually. 
