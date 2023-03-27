## Chapter overviews

### XML Ingest
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_XML_ingest.ipynb)

In this chapter we load up the XML file downloaded from grants.gov, look at the general data schema, and do a summary glance of the data by agency.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/totalsTable.PNG?raw=true)

#### Features
- Overview of xml data schema
- Quick look at data
- Consideration of cleaning approaches
- Quick dataset summary

### Open Science Overview
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Open_Science_Overview.ipynb)

In this chapter we take a closer look at the data, within the context of open science.  Specifically, we look at the co-occurrence of terms from a list of terms we generate.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/textFrequency.png?raw=true)

#### Features
-  (First) application of quick / functionalized [download](https://github.com/DanNBullock/USG_grants_crawl/blob/115f6d2d114c8ab81a0cdee6c107c2a64f220a51/src/grantsGov_utilities.py#L8-L191) and [clean](https://github.com/DanNBullock/USG_grants_crawl/blob/115f6d2d114c8ab81a0cdee6c107c2a64f220a51/src/grantsGov_utilities.py#L193-L424) code.
- Check of description field size.
- Simple keyword search.
- Term co-occurrence analysis.
- Chord diagram / visualization.

### Agency-specific
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Agency.ipynb)

In this chapter we build upon our initial overview, by looking at how open science-related terms are used in an agency-specific fashion.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/SBA_openness.PNG?raw=true)

#### Features
- Interactive plot for inspecting grants & grant counts using particular keywords in particular agencies.
- Also replicated with grant value total instead of count.

### Agency-specific replication from Lee & Chung (2022)
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Agency-Replication.ipynb)

In this chapter we repeat our previous (agency-specific) analysis, but instead of using a keyword list of our own devising, we use a keyword list emperically derived by [Lee & Chung (2022)](https://doi.org/10.47989/irpaper949).  This keyword list is stored in the GitHub repository, as '[OSterms_LeeChung2022.csv](https://github.com/DanNBullock/USG_grants_crawl/blob/main/OSterms_LeeChung2022.csv)'

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/OS_keywords_LeeChung.png?raw=true)

#### Features
- Use of empirically supported keyword set.
- Replication of previous analyses and visualizations.

### Sanity Check
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_SanityCheck.ipynb)

In this chapter we implement some sanity checks. These  include confirming that the extreme ends of the term-matching distributions (e.g. many term matches vs no term matches) do indeed reflect the sorts of grants we would expect. We also check to make sure that our quantative analyses of these descriptions actually return the sorts of results we would expect.

#### Features
- Closer look at putatively relevant grant descriptions.
- Application of various sanity checks for ongoing analyses.

### Co-Occurrence frequency analysis, within-agency
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Agency-Co-Occurrence.ipynb)

In this chapter we drill even further down, and look at term co-occurrence _within_ agencies, in order to see _how_ these terms are being used.  This culminates in the applicaiton of a cosine distance analysis to determine which agencies are using these terms in similar (or distinct) ways.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/agencyTermSimilarity.png?raw=true)

#### Features
- Introduction of cosine distance as method for comparing keyword-term usage patterns across agencies

### Latent Dirichlet Allocation (LDA)
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_LDA.ipynb)

In this chapter we drill even further down, and look at term co-occurrence _within_ agencies, in order to see _how_ these terms are being used.  This culminates in the applicaiton of a cosine distance analysis to determine which agencies are using these terms in similar (or distinct) ways.

![alt text](https://github.com/DanNBullock/USG_grants_crawl/blob/main/imgs/Topic-One.PNG?raw=true)

#### Features
- Provision of several [stopword](https://en.wikipedia.org/wiki/Stop_word) files specific to current grant context (e.g., [general terms](https://github.com/DanNBullock/USG_grants_crawl/blob/main/grantSpecificStopwords.txt), [abbreviations](https://github.com/DanNBullock/USG_grants_crawl/blob/main/grantSpecificStopwords_abbreviations.txt), and [terms to exclude for particularly stringent analyses](https://github.com/DanNBullock/USG_grants_crawl/blob/main/grantSpecificStopwords_aggressive.txt))
- Application of [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) method.
- Interactive visualization of LDA results.