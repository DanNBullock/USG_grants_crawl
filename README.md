# USG Grants Crawl

(branding & badges go here)

## Overview description

An exploration of federal (and some non-federal) grants targeting [Open Science](https://open.science.gov/), using python & jupyter notebooks.  Technically, no longer implemented as a crawl/scrape based usage of [grants.gov APIs](https://www.grants.gov/web/grants/s2s/grantor/web-services.html), and instead uses the [XML Extract](https://www.grants.gov/xml-extract.html) to download and work with the grant database locally.

### Keywords

keywords: [grants.gov](https://www.grants.gov/), grants, open science

## Installlation

### Dependencies

#### Built-ins
- [json](https://docs.python.org/3/library/json.html)
- [re](https://docs.python.org/3/library/re.html)
- [itertools](https://docs.python.org/3/library/itertools.html) 

#### Packages
- [bs4](https://pypi.org/project/bs4/)
- [xmltodict](https://pypi.org/project/xmltodict/)
- [numpy](https://pypi.org/project/numpy/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [pandas](https://pypi.org/project/pandas/)
- [d3blocks](https://pypi.org/project/d3blocks/)
- [notebook](https://pypi.org/project/notebook/) (Jupyter Notebook)


## Project / Codebase overview

This repository contains a series of jupyter notebooks (stored under notebooks) which deail portions of the data anlysis process associated with our overarching endeavor (i.e. exploring US Government funding of Open Science-Related endeavors, via grants).

### Chapter overviews

#### XML Ingest
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/GrantsDotGov_XML_ingest.ipynb)

In this chapter we load up the XML file downloaded from grants.gov, look at the general data schema, and do a summary glance of the data by agency.

#### Open Science Overview
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/GrantsDotGov_Open_Science_Overview.ipynb)

In this chapter we take a closer look at the data, within the context of open science.  Specifically, we look at the co-occurrence of terms from a list of terms we generate.

#### Agency-specific
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/GrantsDotGov_Agency.ipynb)

In this chapter we build upon our initial overview, by looking at how open science-related terms are used in an agency-specific fashion.

#### Agency-specific replication from Lee & Chung (2022)
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/GrantsDotGov_Agency-Replication.ipynb)

In this chapter we repeat our previous (agency-specific) analysis, but instead of using a keyword list of our own devising, we use a keyword list emperically derived by [Lee & Chung (2022)](https://doi.org/10.47989/irpaper949).  This keyword list is stored in the GitHub repository, as '[OSterms_LeeChung2022.csv](https://github.com/DanNBullock/USG_grants_crawl/blob/main/OSterms_LeeChung2022.csv)'

#### Co-Occurrence frequency analysis, within-agency
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/GrantsDotGov_Agency-Co-Occurrence.ipynb)

In this chapter we drill even further down, and look at term co-occurrence _within_ agencies, in order to see _how_ these terms are being used.  This culminates in the applicaiton of a cosine distance analysis to determine which agencies are using these terms in similar (or distinct) ways.

### Relevant modules
[Not yet modularized, but may soon be]

### Other relevant contents
TBD
## Project / codebase provenance
This project's main components are comprised of jupyter notebooks. A future version of this will likely functionalize a number of re-occuring functions, and store these in a repository-specific package (to help with notebook legibility)

### Support elements

#### Authors

[Daniel Bullock](https://dannbullock.github.io/), AAAS Fellow

#### Contributors

[Ann Stapleton](https://www.nifa.usda.gov/ann-e-stapleton), National Program Leader USDA

#### References

[Lee, Jae Yun, and EunKyung Chung. "Mapping open science research using a keyword bibliographic coupling analysis network." (2022).](https://doi.org/10.47989/irpaper949)
