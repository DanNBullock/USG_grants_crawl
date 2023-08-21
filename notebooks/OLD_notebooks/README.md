# Open-Science Infrastructure Data Scrape Analysis: Predecessor Version

The following is a guide to the old, separate-notebook, narritive-heavy format of the Open-Science Infrastructure data crawl analysis.  You'll note that it is broken down into separtate components of the workflow, along with separate notebooks for different data sources (e.g, grants.gov or NSF).  The current version is now contained within the superseding directory (`.../USG_grants_crawl/notebooks`) and is entitled `GenericDataSource_processAndFigs.ipynb`.  There are several changes exemplified by this, that will be described briefly below.

## Changes between Predecessor Version and Generic Data Source Version

### Omnibus / unified workflow formatting

Rather than being divided up in to separte notebooks dedicated to particular portions of the processing or analysis workflow, the primary notebook `GenericDataSource_processAndFigs.ipynb` is now self-contaned, and incorporates the entire processing, analysis, and visualization pipeline in to a single notebook.  This also leads to anothe consequence.

### Substantially reduced text and process discussion

In order to prevent the self-contained processing notebook from becoming overly-long and unwieldy, far less text is dedicated to explaining the rationale or process of what is going on in the workflow.  As such, curious users are directed to reference these old notebooks to get a better sense as to the logic and method of what is being done "behind the scenes" in the new, singleton notebook.  This is not the only edit for brevity, though.

### Refactoring of code base to a cleaner, more functionalized form

The Predecessor Version of the notebook was designed to serve as both a form of self documentation and as an ostensible information resource, and so a substantial amount of code was presented within the notebook itself.  As the workflow became more complicated, the amount of space that would have been required to maintain this level of transparency and verboseness became increasingly untennable.  As such, more and more of the codebased was separated into modularized function collections, which can now be found in `.../USG_grants_crawl/src/`, and include:

- [`getData`](https://github.com/DanNBullock/USG_grants_crawl/blob/multiSourceRefactor/src/getData.py):  Functions for automated, html-based query, download, and extraction (if necessary) of the relevant datasets.
- [`processData`](https://github.com/DanNBullock/USG_grants_crawl/blob/multiSourceRefactor/src/processData.py):  Functions for the automated processing, post processing, and (if necessary) repair/curation of the relevant datasets.
- [`analyzeData`](https://github.com/DanNBullock/USG_grants_crawl/blob/multiSourceRefactor/src/analyzeData.py):  Functions for the analysis and quantification of the relevant datasets.  Includes function-sets for comprehensive, iterative regex search, sub-organization-based analyses, and permutation-based null model simulations, for example.
- [`figs`](https://github.com/DanNBullock/USG_grants_crawl/blob/multiSourceRefactor/src/figs.py):  Functions for the production of presentation, or proto-presentation quality figures, as well as the associated utility functions necesssary for this.
- [`unitTests`](https://github.com/DanNBullock/USG_grants_crawl/blob/multiSourceRefactor/src/unitTests.py):  (PRELIMINARY!) Unit test scripting to ensure the reliability and functionality of code throughout the development process.

### Streamlining of multi-datasource methods into single function set

As implied by the `getData` function module, the code base now contains the capacity to automatedly (e.g., with minimal, if any user input) download data from the required data source.  This data can then be processed and used via the functionality provided in `processData` and `analyzeData`, respectively.  With the `GenericDataSource_processAndFigs.ipynb`, the only modification that needs to be made is the setting of the `defaultDataIndex` variable (int-type), which selects one of the dataset options from the list depicted in `dataSources`.  Currently these _may_* include:

| Organization | Link                                                 | Record_Num | Disk_Size |
|--------------|------------------------------------------------------|------------|-----------|
| grants.gov   | [Link](https://www.grants.gov/xml-extract.html)      | ~70,000    | ~250 MB   |
| NIH          | [Link](https://reporter.nih.gov/exporter)            | ~1,150,000 | ~ 7 GB    |
| NSF          | [Link](https://www.nsf.gov/awardsearch/download.jsp) | ~500,000   | ~ 3 GB    |
| USAspending* | [Link](https://files.usaspending.gov/database_download/) | ~ ?   | ~ 126 GB (zip); ~ 1 TB SQL   |
| DOE*          | [Link](https://pamspublic.science.energy.gov/WebPAMSExternal/Interface/Awards/AwardSearchExternal.aspx) | ~10,000   | ~ 70 MB    |

* = the USAspending and DOE dataset pipelines have not been fully tested / implemented yet.  Of these, the DOE may indeed work, however USAspending implementation is _definitively_ incomplete at the current time.

## Chapter overviews

Below you will find moderatly detailed descriptions of the Predecessor Versions of the notebooks. 

### XML Ingest
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_XML_ingest.ipynb)

In this chapter we load up the XML file downloaded from grants.gov, look at the general data schema, and do a summary glance of the data by agency.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/totalsTable.PNG?raw=true)

#### Features
- Overview of xml data schema
- Quick look at data
- Consideration of cleaning approaches
- Quick dataset summary

### Open Science Overview
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_Open_Science_Overview.ipynb)

In this chapter we take a closer look at the data, within the context of open science.  Specifically, we look at the co-occurrence of terms from a list of terms we generate.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/textFrequency.png?raw=true)

#### Features
-  (First) application of quick / functionalized [download](https://github.com/DanNBullock/USG_grants_crawl/blob/115f6d2d114c8ab81a0cdee6c107c2a64f220a51/src/grantsGov_utilities.py#L8-L191) and [clean](https://github.com/DanNBullock/USG_grants_crawl/blob/115f6d2d114c8ab81a0cdee6c107c2a64f220a51/src/grantsGov_utilities.py#L193-L424) code.
- Check of description field size.
- Simple keyword search.
- Term co-occurrence analysis.
- Chord diagram / visualization.

### Agency-specific
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_Agency.ipynb)

In this chapter we build upon our initial overview, by looking at how open science-related terms are used in an agency-specific fashion.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/SBA_openness.PNG?raw=true)

#### Features
- Interactive plot for inspecting grants & grant counts using particular keywords in particular agencies.
- Also replicated with grant value total instead of count.

### Agency-specific replication from Lee & Chung (2022)
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_Agency-Replication.ipynb)

In this chapter we repeat our previous (agency-specific) analysis, but instead of using a keyword list of our own devising, we use a keyword list emperically derived by [Lee & Chung (2022)](https://doi.org/10.47989/irpaper949).  This keyword list is stored in the GitHub repository, as '[OSterms_LeeChung2022.csv](https://github.com/DanNBullock/USG_grants_crawl/blob/main/keywordLists\OSterms_LeeChung2022.csv)'

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/OS_keywords_LeeChung.png?raw=true)

#### Features
- Use of empirically supported keyword set.
- Replication of previous analyses and visualizations.

### Sanity Check
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_SanityCheck.ipynb)

In this chapter we implement some sanity checks. These  include confirming that the extreme ends of the term-matching distributions (e.g. many term matches vs no term matches) do indeed reflect the sorts of grants we would expect. We also check to make sure that our quantative analyses of these descriptions actually return the sorts of results we would expect.

#### Features
- Closer look at putatively relevant grant descriptions.
- Application of various sanity checks for ongoing analyses.

### Co-Occurrence frequency analysis, within-agency
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_Agency-Co-Occurrence.ipynb)

In this chapter we drill even further down, and look at term co-occurrence _within_ agencies, in order to see _how_ these terms are being used.  This culminates in the applicaiton of a cosine distance analysis to determine which agencies are using these terms in similar (or distinct) ways.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/agencyTermSimilarity.png?raw=true)

#### Features
- Introduction of cosine distance as method for comparing keyword-term usage patterns across agencies

### Latent Dirichlet Allocation (LDA)
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/OLD_notebooks/GrantsDotGov_LDA.ipynb)

In this chapter we drill even further down, and look at term co-occurrence _within_ agencies, in order to see _how_ these terms are being used.  This culminates in the applicaiton of a cosine distance analysis to determine which agencies are using these terms in similar (or distinct) ways.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/Topic-One.PNG?raw=true)

#### Features
- Provision of several [stopword](https://en.wikipedia.org/wiki/Stop_word) files specific to current grant context (e.g., [general terms](https://github.com/DanNBullock/USG_grants_crawl/blob/main/keywordLists/grantSpecificStopwords.txt), [abbreviations](https://github.com/DanNBullock/USG_grants_crawl/blob/main/keywordLists/grantSpecificStopwords_abbreviations.txt), and [terms to exclude for particularly stringent analyses](https://github.com/DanNBullock/USG_grants_crawl/blob/main/keywordLists/grantSpecificStopwords_aggressive.txt))
- Application of [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) method.
- Interactive visualization of LDA results.