"""
This set of functions is used to test the functionality of the functions found in the other modules of this package

"""

def inferenceTest():
    """
    This function tests the functionality of detectDataSourceFromSchema.

    """
    import numpy.testing as npt
    import os
    # add the path to the package to the system path
    import sys
    repoDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    codeDir=os.path.join(repoDir,'src')
    sys.path.append(codeDir)
    dataDir=os.path.join(repoDir,'inputData')
    import analyzeData

    # import the csv which indicates the data source for each example
    import pandas as pd
    # dataSourceFile=os.path.join(dataDir,'testFiles','key.csv')
    # actually, we can just hard code the data sources and grant names
    dataSources=['NSF','grantsGov'] # TODO: add NIH
    # make sure to get the order right
    # rule of thumb: the first two numbers of NSF are the year, and they all appear to have 7 digits
    fileNames=['2200269','261970']
    # make a temporary dataframe for these
    dataSource=pd.DataFrame({'grantName':fileNames,'dataSource':dataSources})
    # read it in
    # actually dont, we're just hardcoding now
    # dataSource=pd.read_csv(dataSourceFile,header=None)
    # iterate across the rows
    for i in range(dataSource.shape[0]):
        grantName=dataSource.iloc[i,0]
        # grant path
        grantPath=os.path.join(dataDir,'testFiles',str(grantName)+'.xml')
        grantSource=grantName=dataSource.iloc[i,1]
        # run the function
        detectedSource=analyzeData.detectDataSourceFromSchema(grantPath)
        # check if the detected source matches the expected source
        print('Test of '+ grantSource + ' as data source.')
        npt.assert_equal(detectedSource,grantSource)

def fieldExtractTest():
    """
    This function tests the functionality of extractValueFromDictField against expected behaviors

    """
    import numpy.testing as npt
    import os
    import xmltodict
    # add the path to the package to the system path
    import sys
    repoDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    codeDir=os.path.join(repoDir,'src')
    sys.path.append(codeDir)
    dataDir=os.path.join(repoDir,'inputData')
    import analyzeData

    # import the csv which indicates the data source for each example
    import pandas as pd
    # don't actually need this, but we'll keep it for now
    dataSources=['NSF','grantsGov'] # TODO: add NIH
    # both start with 'rootTag' due to how we imposed that norm on the restructured grants.gov data
    # we'll just default to using the ID fields
    fieldSequences = [['rootTag','AwardID'],['rootTag','OpportunityID']]
    # make sure to get the order right
    # rule of thumb: the first two numbers of NSF are the year, and they all appear to have 7 digits
    fileNames=['2200269','261970']

    for iIndex,iFiles in enumerate(fileNames):
        grantName=iFiles
        # grant path
        grantPath=os.path.join(dataDir,'testFiles',grantName+'.xml')
        # read in the grant
        # this function requires the grant to be in a dictionary, not a file path
        with open(grantPath) as grantFile:
            grantDict=xmltodict.parse(grantFile.read())
            # extract the desired field
            extractedField=analyzeData.extractValueFromDictField(grantDict,fieldSequences[iIndex])
            # this should be equivalent to the file name (which is the grant ID)
            npt.assert_equal(extractedField,grantName)

def regexOnXMLtest():
    """
    This function tests the functionality of applyRegexToXMLFile against expected behaviors
    
    applyRegexToXMLFile(xmlFilePath,stringPhrase,fieldsSelect,caseSensitive=False)

    """
    import numpy.testing as npt
    import os
    import xmltodict
    # add the path to the package to the system path
    import sys
    repoDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    codeDir=os.path.join(repoDir,'src')
    sys.path.append(codeDir)
    dataDir=os.path.join(repoDir,'inputData')
    import analyzeData

    # set the names for the files
    NSF_filename='2200269.xml'
    grantsGov_filename='261970.xml'

    # set some keywords to regex test for
    NSFgrantKeywords=['machine learning','covid-19', 'AI model','null result']
    NSF_expected=[True,True,True,False]
    grantsGovKeywords=['collaborative', 'geospatial', 'conservation' ,'null result']
    grantsGov_expected=[True,True,True,False]

    # set the field to regex search in
    # NOTE: apparently rootTag doesn't actually show up in the NSF dictionary structure, potentially due to the indentation formatting of those files?
    # NOTE: BUT SOMETIMES IT DOES SHOW UP.  
    # TODO: FIGURE OUT WHY AND WHEN rootTag SHOWS UP
    NSFfieldSequences = ['rootTag','Award','AbstractNarration']
    grantsGovfieldSequences = ['rootTag','Description']

    # first test NSF

    # set the file path for nsf
    NSF_filePath=os.path.join(dataDir,'testFiles',NSF_filename)
    NSF_results=[]
    for iTest in NSFgrantKeywords:
        searchResult=analyzeData.applyRegexToXMLFile(NSF_filePath,iTest,NSFfieldSequences)
        print('Search result for ' + iTest + ' in NSF ' + NSF_filename + ' is ' + str(searchResult))
        NSF_results.append(searchResult)
    # check if the results match the expected results
    npt.assert_equal(NSF_results,NSF_expected)

    # set the file path for grants.gov
    grantsGov_filePath=os.path.join(dataDir,'testFiles',grantsGov_filename)
    grantsGov_results=[]
    for iTest in grantsGovKeywords:
        searchResult=analyzeData.applyRegexToXMLFile(grantsGov_filePath,iTest,grantsGovfieldSequences)
        print('Search result for ' + iTest + ' in grants.gov ' + grantsGov_filename + ' is ' + str(searchResult))
        grantsGov_results.append(searchResult)
    # check if the results match the expected results
    npt.assert_equal(grantsGov_results,grantsGov_expected)

import numpy as np
np.zeros((10,5))


def unique_partitions_OLD(cis):
    """
    This is a copy of the "old" unique_partitions function, found here in bctpy:
    https://github.com/aestrivex/bctpy/blob/1b40e281eda081060707e30b68106ac1ebf54130/bct/algorithms/clustering.py#L397-L428
    which may or may not be working as intended.  We're using this instantion to test against the new version of the function.

    NOTE: the documentation in this docstring is inferred from my reading / understanding of the code (08/11/2023).  It may not be correct.

    My understanding is that this function takes in an N by M array / matrix of int type ( or int coercible), 
    where N is the number of nodes and M is the number of repetitions of the clustering algorithm.  Given that any particular
    clustering could have a different number of clusters, there should be no expectation that the number of clusters (and thus the number of unique integers)
    is the same across all repetitions.  This function relabels the clusters so that the same clusters have the same integer label across all repetitions.


    Parameters
    
    """
    # relabels the partitions to recognize different numbers on same
    # topology

    n, r = np.shape(cis)  # ci represents one vector for each rep
    # Dan Note: n probably means nodes, r probably means reps
    ci_tmp = np.zeros(n)

    for i in range(r):
        for j, u in enumerate(sorted(
                np.unique(cis[:, i], return_index=True)[1])):
            ci_tmp[np.where(cis[:, i] == cis[u, i])] = j
        cis[:, i] = ci_tmp
        # so far no partitions have been deleted from ci

    # now squash any of the partitions that are completely identical
    # do not delete them from ci which needs to stay same size, so make
    # copy
    ciu = []
    cis = cis.copy()
    c = np.arange(r)
    # count=0
    while (c != 0).sum() > 0:
        ciu.append(cis[:, 0])
        dup = np.where(np.sum(np.abs(cis.T - cis[:, 0]), axis=1) == 0)
        cis = np.delete(cis, dup, axis=1)
        c = np.delete(c, dup)
        # count+=1
        # print count,c,dup
        # if count>10:
        #	class QualitativeError(): pass
        #	raise QualitativeError()
    return np.transpose(ciu)