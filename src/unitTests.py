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
