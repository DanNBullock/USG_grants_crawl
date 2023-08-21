def applyRegexsToDirOfXML(directoryPath,stringPhraseList,fieldsSelect,caseSensitive=False):
    """
    Applies a regex search to the list of inputTexts and a dictionary wherein the keys are a tuple of the string phrase and the file name and the values are booleans indicating whether the string phrase was found in the file.

    Parameters
    ----------
    directoryPath : string
        A string corresponding to the path to the directory containing the xml files to be searched.
    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    caseSensitive : bool, optional
        A boolean indicating whether the search should be case sensitive. The default is False.

    Returns
    -------
    outputDict : dict
        A dictionary with a field corresponding to the string phrase, whose value is a dictionary with fields corresponding to the file names, whose values are booleans indicating whether the string phrase was found in the file.
    """
    # determine if dask is available
    try:
        import dask
        import dask.bag as db
        daskAvailable=True
    except:
        daskAvailable=False
    import os
    fileList=os.listdir(directoryPath)
    # create an empty dictionary with the tuples of the string phrase and the file name as the keys
    outputDict={}
    # if dask is available, use it to parallelize the search
    if daskAvailable:
        # iterate across the stringPhraseList and apply the regex search to each file
        for iStringPhrase in stringPhraseList:
            # get the list of files in the directory
            
            # create a dask bag with the file list
            fileListBag=db.from_sequence(fileList)
            # use the dask bag to apply the regex search to each file and place it in the appropriate tuple dictionary entry
            outputDict[iStringPhrase]=dict(fileListBag.map(lambda x: (iStringPhrase,x,applyRegexToXMLFile(os.path.join(directoryPath,x),iStringPhrase,fieldsSelect,caseSensitive=caseSensitive))).compute())
    # if dask is not available, use a for loop to iterate across the files
    else:
        # iterate across the stringPhraseList and apply the regex search to each file
        for iStringPhrase in stringPhraseList:
            # get the list of files in the directory
            fileList=os.listdir(directoryPath)
            # iterate across the files
            for iFile in fileList:
                try:
                    # apply the regex search to the file and place it in the appropriate tuple dictionary entry
                    outputDict[iStringPhrase][iFile]=applyRegexToXMLFile(os.path.join(directoryPath,iFile),iStringPhrase,fieldsSelect,caseSensitive=caseSensitive)
                except:
                    # throw an error and specify the file that caused the error
                    raise ValueError('Error in file: '+iFile)
                
    return outputDict

def convertTupleDictToEfficientDict(tupleDict,rowDescription='',colDescription=''):
    """
    Convets a dictionary with tuples as keys to a dictionary with three keys: rowNames, colNames, and dataMatrix.  
    The rowName and colName are themselves dictionaries, with two fields:  "nameValues" and "description".  
    "nameValues" is a list of the unique names of the rows or columns, respectively.  "description" is a string describing the data in the row or column.
    The dataMatrix is a N by M matrix of reflecting the values associated with the tuples.

    This is done because presumably this is a more efficient way to store the data.
    
    Parameters
    ----------
    tupleDict : dict
        A dictionary with tuples as keys.
    rowDescription : string, optional
        A string describing the data in the rows. The default is '', a blank string.
    colDescription : string, optional  
        A string describing the data in the columns. The default is '', a blank string.

    Returns
    -------
    efficientDict : dict
        A dictionary with three keys: rowName, colName, and dataMatrix.
    """
    import numpy as np
    # get the row and column names
    rowName=[iTuple[0] for iTuple in tupleDict.keys()]
    colName=[iTuple[1] for iTuple in tupleDict.keys()]
    # get the unique row and column names and preserve the order
    uniqueRowName=list(dict.fromkeys(rowName))
    uniqueColName=list(dict.fromkeys(colName))
    # create the efficient dictionary
    efficientDict={}
    efficientDict['rowName']={}
    efficientDict['colName']={}
    efficientDict['dataMatrix']=np.zeros((len(uniqueRowName),len(uniqueColName)))
    # go ahead and create the description field for the row and column names
    efficientDict['rowName']['description']=rowDescription
    efficientDict['colName']['description']=colDescription
    # before iterating across the rows and colums, go ahead and fill in the row and column names
    efficientDict['rowName']['nameValues']=uniqueRowName
    efficientDict['colName']['nameValues']=uniqueColName
    # iterate across the rows and columns and fill in the data matrix
    for iRow in range(len(uniqueRowName)):
        for iCol in range(len(uniqueColName)):
            # get the row and column names
            iRowName=uniqueRowName[iRow]
            iColName=uniqueColName[iCol]
            # get the value
            iValue=tupleDict[(iRowName,iColName)]
            # fill in the data matrix
            efficientDict['dataMatrix'][iRow,iCol]=iValue
    return efficientDict

    

def searchInputListsForKeywords_dask(inputLists,keywordList):
    """
    Divides up the items in the inputLists--for items whose description includes
    an item from the input keywordList variable--into groups associated by keyword.

    Returns a dictionary wherein the keys are keywords and the values are lists of items
    wherein the the keyword was found in the associated description.

    Uses dask if available to parallelize the search.

    Parameters
    ----------
    inputLists : list of lists
        A list of lists wherein each list contains a set of items to be assessed for keyword occurrences. 
    keywordList : list of strings
        A list of strings corresponding to the keywords one is interested in assessing the occurrences of. 

    Returns
    -------
    grantFindsOut : dictionary
        A a dictionary wherein the keys are keywords and the values are N long boolean vectors indicating
    whether the keyword was found in the associated description.

    See Also
    --------
    grants_by_Agencies : Divides up the grant IDs ('OpportunityID') from the input grantsDF by top level agency.
    """
    import pandas as pd
    import re
    import time
    import numpy as np
    # if inputLists is a series, then convert it to a list
    if type(inputLists)==pd.core.series.Series:
        inputLists=inputLists.values.tolist()

    # create a dictionary in which each each key is a keyword, and the value is a blank boolean vector of length N, where N is the number of items in the inputLists
    # first create a blank boolean vector of length N that will be placed in all dictionary entries
    blankBoolVec=[False]*len(inputLists)
    # then create the dictionary itself
    grantFindsOut={}
    # then populate the dictionary with the blank boolean vectors
    for iKeywords in keywordList:
        grantFindsOut[iKeywords]=blankBoolVec
    # next we compile all of the regex searches that we will perform
    # we replace dashes with spaces to be insensitive to variations in hyphenation behaviors
    compiledRegexList=[re.compile('\\b'+iKeywords.lower().replace('-',' ')+'\\b') for iKeywords in keywordList]

    # next define the function that will be used to search the input text for the compiled regex
    # we do this so that we can parallelize the search
    def searchInputForCompiledRegex(inputText,compiledRegex):
        """
        Searches the input text for the compiled regex and returns True if found, False if not found.
        Function is used to parallelize the search for keywords in the input text.
        """
        # case insensitive find for the keyword phrase
        # use try except to handle the case where there is no description field
        try:
        # get rid of dashes to be insensitive to variations in hyphenation behaviors
            if bool(compiledRegex.search(inputText.lower().replace('-',' '))):
                    #append the ID if found
                    return True
            else:
                return False
        except:
            # do nothing, if there's no description field, then the word can't be found
            return False

    # check if dask is available
    try:
        import dask
        #import dask.dataframe as dd
        import dask.bag as db
        import dask.multiprocessing
        import dask.distributed as dd
        from dask.diagnostics import ProgressBar
        import multiprocessing
        from dask.distributed import Client, progress
        # if dask is available, then use it to parallelize the search

        # first find the number of cores on the machine
        numCores=multiprocessing.cpu_count()
        # establish a dask client with the number of cores minus 2


        # redefining it here, I guess?
        
            # next define the function that will be used to search the input text for the compiled regex
        # we do this so that we can parallelize the search
       
        def searchInputForCompiledRegex(inputText,compiledRegex):
            """
            Searches the input text for the compiled regex and returns True if found, False if not found.
            Function is used to parallelize the search for keywords in the input text.
            """
            # case insensitive find for the keyword phrase
            # use try except to handle the case where there is no description field
            try:
            # get rid of dashes to be insensitive to variations in hyphenation behaviors
                if bool(compiledRegex.search(inputText.lower().replace('-',' '))):
                        #append the ID if found
                        return True
                else:
                    return False
            except:
                # do nothing, if there's no description field, then the word can't be found
                return False
        
        results=[]
        for iKeywords in keywordList:
            for iInput in inputLists:
                tempResult=dask.delayed(searchInputForCompiledRegex(iInput,iKeywords))
                results.append(tempResult)
        
        with dd.Client(n_workers=numCores-2) as client:
            searchResults=dd.compute(*results,scheduler='processes')
        
        # now reshape the searchResults into an array
        searchResults=np.array(searchResults).reshape(len(keywordList),len(inputLists))
        # now convert the array into a dictionary
        for iKeywords in range(len(keywordList)):
            grantFindsOut[keywordList[iKeywords]]=searchResults[iKeywords,:]



                




        # create a dask dataframe from the inputLists
        daskDF=dd.from_pandas(pd.DataFrame(inputLists),npartitions=4)
        # create a dask dataframe from the compiledRegexList
        daskCompiledRegexList=dd.from_pandas(pd.DataFrame(compiledRegexList))
        # use the daskDF and daskCompiledRegexList to parallelize the search across the inputLists, applying searchInputForCompiledRegex for each daskCompiledRegexList entry
        daskSearch=daskDF.map(lambda x: [searchInputForCompiledRegex(x,iRegex) for iRegex in compiledRegexList])
        testOut=daskSearch.compute()

        # next we will parallelize a nested loop, where the outer loop is across the keywords, and the inner loop is across the inputLists
        # this is because there are ~500000 items in the inputLists, and > 100 keywords, the major slowdown is looping across the inputLists
        # as such, we can do a regular loop across the keywords, and then use dask to parallelize the search across the inputLists
        # include a progress bar
        # create a dask bag from the inputLists
        daskBag=db.from_sequence(inputLists,npartitions=4)


 
        # because there are ~500000 items in the inputLists, and > 100 keywords, the major slowdown is looping across the inputLists
        # as such, we can do a regular loop across the keywords, and then use dask to parallelize the search across the inputLists
        # include a progress bar
        # create a dask bag from the inputLists
        daskBag=db.from_sequence(inputLists,npartitions=4)
        
        for iKeywords,iCompiledSearch in zip(keywordList,compiledRegexList):
            print('Searching for keyword: '+iKeywords)
            #start timer
            start=time.time()
            # use the dask bag to parallelize the search across the inputLists
            daskSearch=daskBag.map(lambda x: searchInputForCompiledRegex(x,iCompiledSearch))
            # convert the dask bag to list
            boolVec=daskSearch.compute()
            # store the boolean vector in the output dictionary
            grantFindsOut[iKeywords]=boolVec
            #print the number of items found
            print('Number of items found: '+str(sum(boolVec)))
            #print time for this loop
            print('Time for this keyword: '+iKeywords + ' = '+str(time.time()-start))

        # close the dask client
        client.close()
    except:
        # if dask is not available, then use a regular loop
        for iKeywords,iCompiledSearch in zip(keywordList,compiledRegexList):
            for iRows,iListing in enumerate(inputLists):
                # case insensitive find for the keyword phrase
                # use try except to handle the case where there is no description field
                try:
                    # get rid of dashes to be insensitive to variations in hyphenation behaviors
                    if bool(iCompiledSearch.search(iListing.lower().replace('-',' '))):
                        #append the ID if found
                        grantFindsOut[iKeywords][iRows]=True
                except:
                    # do nothing, if there's no description field, then the word can't be found and the false remains in place
                    pass
    return grantFindsOut



def applyKeywordSearch_NSF(inputDF,keywordList):
    """
    Applies the desired regex based keyword search to the relevant field of the NSF dataframe ('AbstractNarration') and
    outputs a dictionary wherein the keys are keywords and the values the 'AwardID' values for the grants in which the
    keyword was found in the associated description.
    Inputs:
        inputDF: pandas dataframe
            The dataframe containing the NSF grant data

        keywordList:  list of strings
            A list of strings corresponding to the keywords one is interested in assessing the occurrences of
    Outputs:
        grantFindsOut: dictionary
            A dictionary wherein the keys are keywords and the values the 'AwardID' values for the grants in which the
            keyword was found in the associated description.
    """
    import pandas as pd
    from itertools import compress
    # get the abstract narration field
    abstractNarrations=inputDF['AbstractNarration'].values.tolist()
    # apply the keyword search
    boolDictionaryKeywords=searchInputListsForKeywords_dask(abstractNarrations,keywordList)
    # convert the boolean vectors to lists of award IDs for each keyword
    # first get the award IDs
    awardIDs=inputDF['AwardID'].values.tolist()
    # then convert the boolean vectors to lists of award IDs
    awardIDLists={}
    for iKeywords in boolDictionaryKeywords.keys():
        awardIDLists[iKeywords]=list(compress(awardIDs,boolDictionaryKeywords[iKeywords]))
    return awardIDLists

def applyRegexToInput(inputText,stringPhrase,caseSensitive=False):
    """
    Applies a regex search to the inputText and returns a boolean indicating whether the stringPhrase was found.

    Parameters
    ----------
    inputText : string
        A string to be assessed for the presence of the stringPhrase.
    stringPhrase : string
        A string corresponding to the phrase one is interested in assessing the occurrences of. 
    caseSensitive : bool, optional
        A boolean indicating whether the search should be case sensitive. The default is False.

    Returns
    -------
    bool
        A boolean indicating whether the stringPhrase was found in the inputText.
    """
    import re
    if caseSensitive:
        compiledSearch=re.compile(stringPhrase)
    else:
        compiledSearch=re.compile(stringPhrase.lower())
    try:
        if bool(compiledSearch.search(inputText.lower())):
            return True
        else:
            return False
    except:
        return False

def applyRegexToXMLFile(xmlFilePath,stringPhrase,fieldsSelect,caseSensitive=False):
    """
    Applies a regex search to the inputText and returns a boolean indicating whether the stringPhrase was found.
    
    Parameters
    ----------
    xmlFilePath : string
        A string corresponding to the path to the xml file to be searched.  Can also be the file contents as a string.
    stringPhrase : string
        A string corresponding to the phrase one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    caseSensitive : bool, optional
        A boolean indicating whether the search should be case sensitive. The default is False.
    
    Returns
    -------
    bool
        A boolean indicating whether the stringPhrase was found in the inputText.
    """
    import xmltodict
    import re
    if caseSensitive:
        compiledSearch=re.compile(stringPhrase)
    else:
        compiledSearch=re.compile(stringPhrase.lower())
    # if the xmlFilePath is a string, then assume it's the file path and load the file
    if type(xmlFilePath)==str:
        with open(xmlFilePath) as f:
            xmlDict=xmltodict.parse(f.read())
    # close the file
        f.close()
    else:
        xmlDict=xmltodict.parse(xmlFilePath)
    # iterate through the elements of fieldsSelect list to get to the content of the final field
    for iField in fieldsSelect:
        xmlDict=xmlDict[iField]
    # now that we have the relevant contet, we need to convert the text to nlp-ready text
    # use prepareTextForNLP(inputText,stopwordsList=None,lemmatizer=None)
    xmlDict=prepareAllTextsForNLP(xmlDict)

    # use applyRegexToInput
    outputBool=applyRegexToInput(xmlDict,stringPhrase,caseSensitive=caseSensitive)
    return outputBool