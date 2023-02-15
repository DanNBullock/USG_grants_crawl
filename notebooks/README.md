### Chapter overviews

#### XML Ingest
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_XML_ingest.ipynb)

In this chapter we load up the XML file downloaded from grants.gov, look at the general data schema, and do a summary glance of the data by agency.

#### Open Science Overview
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Open_Science_Overview.ipynb)

In this chapter we take a closer look at the data, within the context of open science.  Specifically, we look at the co-occurrence of terms from a list of terms we generate.

#### Agency-specific
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Agency.ipynb)

In this chapter we build upon our initial overview, by looking at how open science-related terms are used in an agency-specific fashion.

#### Agency-specific replication from Lee & Chung (2022)
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Agency-Replication.ipynb)

In this chapter we repeat our previous (agency-specific) analysis, but instead of using a keyword list of our own devising, we use a keyword list emperically derived by [Lee & Chung (2022)](https://doi.org/10.47989/irpaper949).  This keyword list is stored in the GitHub repository, as '[OSterms_LeeChung2022.csv](https://github.com/DanNBullock/USG_grants_crawl/blob/main/OSterms_LeeChung2022.csv)'

#### Co-Occurrence frequency analysis, within-agency
[link to chapter](https://github.com/DanNBullock/USG_grants_crawl/blob/main/notebooks/GrantsDotGov_Agency-Co-Occurrence.ipynb)

In this chapter we drill even further down, and look at term co-occurrence _within_ agencies, in order to see _how_ these terms are being used.  This culminates in the applicaiton of a cosine distance analysis to determine which agencies are using these terms in similar (or distinct) ways.