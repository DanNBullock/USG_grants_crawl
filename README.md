# USG Grants Crawl

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/newGrantChord.PNG?raw=true)

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
- [pickle](https://docs.python.org/3/library/pickle.html)

#### Packages
- [xmltodict](https://pypi.org/project/xmltodict/)
- [numpy](https://pypi.org/project/numpy/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [pandas](https://pypi.org/project/pandas/)
- [d3blocks](https://pypi.org/project/d3blocks/)
- [notebook](https://pypi.org/project/notebook/) (Jupyter Notebook)
- [gensim](https://pypi.org/project/gensim/)
- [nltk](https://pypi.org/project/nltk/)
- [pyLDAvis](https://pypi.org/project/pyLDAvis/)

## Project / Codebase overview

This repository contains a series of jupyter notebooks (stored under notebooks) which deail portions of the data anlysis process associated with our overarching endeavor (i.e. exploring US Government funding of Open Science-Related endeavors, via grants).

### Chapter overviews

Broadly speaking, this collection of notebooks is intended to guide users through an increasingly complex analysis of data derived from grants.gov, as it relates to open science infrastructure.

<font size="20">**For descriptions of the specific chapters, see [the `README` file contained within the `notebooks/` directory](https://github.com/DanNBullock/USG_grants_crawl/tree/main/notebooks)**</font>

### Relevant modules
Within the [`src/` directory](https://github.com/DanNBullock/USG_grants_crawl/blob/main/src/) the [`grantsGov_utilities.py` file](https://github.com/DanNBullock/USG_grants_crawl/blob/main/src/grantsGov_utilities.py) contains a number of thouroughly documented functions that are used throughout the notebooks.  Feel free to search through these, as later notbooks opt towards cleaner and more succinct code as opposed to rehashing code that has already been used.

### Other relevant content
TBD
## Project / codebase provenance
This project's main components are comprised of jupyter notebooks. A number of re-occuring functions (which would also take up substantial page-space, in addition to be repetitive) are stored in the [`src/` directory](https://github.com/DanNBullock/USG_grants_crawl/tree/main/src) in the [`grantsGov_utilities.py`](https://github.com/DanNBullock/USG_grants_crawl/blob/main/src/grantsGov_utilities.py) file.

### Support elements

#### Authors

[Daniel Bullock](https://dannbullock.github.io/), [AAAS](https://www.aaas.org/) [STPF](https://www.aaas.org/programs/science-technology-policy-fellowships) Fellow

#### Contributors

[Ann Stapleton](https://www.nifa.usda.gov/ann-e-stapleton), National Program Leader USDA

#### References

[Lee, Jae Yun, and EunKyung Chung. "Mapping open science research using a keyword bibliographic coupling analysis network." (2022).](https://doi.org/10.47989/irpaper949)
