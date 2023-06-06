def applyRegexsToDirOfXML(directoryPath,stringPhraseList,fieldsSelect):
    """
    Applies a regex search to the list of inputTexts and a dictionary wherein the keys are a tuple of the string phrase and the file name and the values are booleans indicating whether the string phrase was found in the file.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    directoryPath : string
        A string corresponding to the path to the directory containing the xml files to be searched.
    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.

    Returns
    -------
    tupleDict : dict
        A dictionary with tuples as keys and booleans as values, indicating whether the targetField was found in the inputStructs.

    """
    import os
    fileList=os.listdir(directoryPath)
    # filter the list down to only the xml files
    fileList=[iFile for iFile in fileList if iFile[-4:]=='.xml']

    # create an empty dictionary with the tuples of the string phrase and the file name as the keys
    tupleDict={}
    # iterate across pairings of the string phrases and the file names in order to create the dictionary keys
    for iStringPhrase in stringPhraseList:
        for iFile in fileList:
            tupleDict[(iStringPhrase,iFile)]=False

    # iterate across the stringPhraseList and apply the regex search to each file
    for iStringPhrase in stringPhraseList:
        # temporary debut print statement
        print('Searching for the string phrase: '+iStringPhrase)
        # get the list of files in the directory
        # no we already got that, so we don't need to keep redoing that
        # fileList=os.listdir(directoryPath)
        # iterate across the files
        for iFile in fileList:
            # apply the regex search to the file and place it in the appropriate tuple dictionary entry
            tupleDict[(iStringPhrase,iFile)]=applyRegexToXMLFile(os.path.join(directoryPath,iFile),iStringPhrase,fieldsSelect)

    return tupleDict


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
        A dictionary with tuples as keys and booleans as values, indicating whether the targetField was found in the inputStructs.
    rowDescription : string, optional
        A string describing the data in the rows. The default is '', a blank string.
    colDescription : string, optional  
        A string describing the data in the columns. The default is '', a blank string.

    Returns
    -------
    efficientDict : dict
        A more efficient dictionary with the following fields:
        - rowName: string, the names of the rows (the unique values of the targetField)
        - colName: string, the names of the columns (the identifiers of the inputStructs)
        - rowDescription: string, a description of the rows
        - colDescription: string, a description of the columns
        - dataMatrix: len(rowName) by len(colName) matrix of booleans indicating whether the targetField was found in the inputStructs

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
    efficientDict['rowDescription']=rowDescription
    efficientDict['colDescription']=colDescription
    # before iterating across the rows and colums, go ahead and fill in the row and column names
    efficientDict['rowName']=uniqueRowName
    efficientDict['colName']=uniqueColName
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

def regexSearchAndSave(directoryPath,stringPhraseList,fieldsSelect,savePath=''):
    """
    Applies a regex search to the field specified by the list in fieldsSelect (single field; sequence represents nested fields) to the xml files in the directory specified by directoryPath.
    Saves the results in an efficient, compressed hdf5 file.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    directoryPath : string
        A string corresponding to the path to the directory containing the xml files to be searched.
    stringPhraseList : list of strings
        A list of strings corresponding to the phrases one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
      savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.
    
    Returns 
    -------

    The output is saved down as an hdf5 file.
   
    """
    import os
    import h5py
    import xmltodict
    # TODO: make this more robust relative to alternative ways of inputting the items to be searched, see tupleDictFromDictFields for example inference behavior.
    # TODO: consider implementing inference behavior for the fieldsSelect, using the first xml file in the directory to infer the fieldsSelect.

    # apply the regex search to the contents using applyRegexsToDirOfXML
    tupleDict=applyRegexsToDirOfXML(directoryPath,stringPhraseList,fieldsSelect)
    # convert the tupleDict to an efficientDict
    efficientDict=convertTupleDictToEfficientDict(tupleDict)
    # try and infer the data source from the first xml file in directoryPath
    try: 
        # start by getting the contents of the directory
        fileList=os.listdir(directoryPath)
        # get the first xml file
        firstXMLFile=[iFile for iFile in fileList if iFile.endswith('.xml')][0]
        # load the object
        with open(os.path.join(directoryPath,firstXMLFile)) as fd:
            firstXMLObject=xmltodict.parse(fd.read())
            #close the file
        fd.close()
        # get the data source using detectDataSourceFromSchema
        dataSource=detectDataSourceFromSchema(firstXMLObject)
        # use this metadata to set the metadata for the efficientDict
        if dataSource=='NSF':
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='NSF Award Number'
        elif dataSource=='NIH':
            # throw not implemented error
            raise NotImplementedError('NIH not yet implemented')
        elif dataSource=='grantsGov':
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='Grants.Gov Opportunity ID'
        else:
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='Presumptive grant identifier'
    except:
        # if this fails, just set the metadata to be generic
        efficientDict['rowDescription']='Searched Keywords'
        efficientDict['colDescription']='Presumptive grant identifier'
    # set the data and attribute keys for the hdf5 file
    # apparently rowName and colName are too big to save as attributes, so they have to be saved as datasets
    dataKeys=['dataMatrix','rowName','colName']
    attributeKeys=['rowDescription','colDescription']

    # save the efficientDict as an hdf5 file
    if savePath=='':
        savePath=os.getcwd()
    # create the save file name
        saveFileName='regexSearchResults_'+fieldsSelect[-1]+'.hdf5'
        # create the save path
        savePath=os.path.join(savePath,saveFileName)
    # otherwise use the provided savePath
    else:
        savePath=savePath
        # but make sure the directory that would contain the file exists
        if not os.path.exists(os.path.dirname(savePath)):
            os.makedirs(os.path.dirname(savePath))
    # save the file
    with h5py.File(savePath,'w') as f:
        # iterate across the data keys and save the data
        for iKey in dataKeys:
            f.create_dataset(iKey,data=efficientDict[iKey],compression='gzip')
        # iterate across the attribute keys and save the attributes
        for iKey in attributeKeys:
            f.attrs[iKey]=efficientDict[iKey]
    # close the file
    f.close()
    return

def fieldExtractAndSave(inputStructs,targetField,nameField='infer',savePath=''):
    """
    Extracts the values of the target field from the input structures and saves the results in an efficient, compressed hdf5 file.

    Parameters
    ----------
    inputStructs : list of dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    nameField : string, optional
        A string corresponding to the field, presumed to be present in all input structures, to be used as the name for the input structure.  The default is 'infer', which will attempt to infer the name field from the input structures.
    savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.
    
    Returns 
    -------

    The output is saved down as a csv.
   
    """
    import os
    import h5py
    import xmltodict
    import pandas as pd


    # start by determining what the first element of the inputStructs is
    firstElement=inputStructs[0]
    if isinstance(firstElement,str):
    # if it's a file path then test if it's a valid file path
        if os.path.isfile(firstElement):
            # if it's a valid file path then test if it's an XML file
            if firstElement.endswith('.xml'):
                # if it's an XML file then read it in as a dictionary
                inputType='xmlFile'
                # load it up and test the source 
                with open(firstElement) as fd:
                    firstElementObject=xmltodict.parse(fd.read())
                fd.close()
                # get the data source using detectDataSourceFromSchema
                dataSource=detectDataSourceFromSchema(firstElementObject)
            else:
                # if it's not an XML file then raise an error
                raise ValueError('The inputStructs variable contains a file-like string with non-"xml" extension that is not a valid file path.')
        # if it's a string but not a file, check if it's a valid XML string
        elif firstElement.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
            inputType='xmlString'
            # load it up and test the source
            firstElementObject=xmltodict.parse(firstElement)
            # get the data source using detectDataSourceFromSchema
            dataSource=detectDataSourceFromSchema(firstElementObject)
        # TODO: maybe also consider checking if it's a valid JSON string
    # if it's not a string then check if it's a dictionary
    elif isinstance(firstElement,dict):
        inputType='dict'
        # get the data source using detectDataSourceFromSchema
        dataSource=detectDataSourceFromSchema(firstElement)
    # if it's not a string or a dictionary then raise an error
    else:
        raise ValueError('The inputStructs variable contains an item that is not a valid file path, XML string, or dictionary.')
    print('input type '+inputType+' detected')
    # go ahead and specify name field
    if dataSource == 'NSF':
        targetNameField=['rootTag','Award','AwardID']
    elif dataSource == 'NIH':
        targetNameField=['rootTag','APPLICATION_ID']
    elif dataSource == 'grantsGov':
        targetNameField=['rootTag','OpportunityID']

    # initalize a pandas dataframe with columns for 'itemID' and 'fieldValue' to store the results
    # ensure that it has N blank rows, where N is the number of inputStructs
    resultsDF=pd.DataFrame(columns=['itemID','fieldValue'],index=range(len(inputStructs)))
    
    # loop through the inputStructs and extract the target field
    for iIndex,iStruct in enumerate(inputStructs):
        # load it up as appropriate, given the inputType
        if inputType=='xmlFile':
            with open(iStruct) as fd:
                iStructObject=xmltodict.parse(fd.read())
            fd.close()
        elif inputType=='xmlString':
            iStructObject=xmltodict.parse(iStruct)
        elif inputType=='dict':
            iStructObject=iStruct
        # extract the target field
        targetValue=extractValueFromDictField(iStructObject,targetField)
        # extract the name field
        if nameField=='infer':
            nameValue=extractValueFromDictField(iStructObject,targetNameField)
        else:
            # assume that you're suppoesd to get it from the name of the file, but throw an error if the input isn't a string
            if isinstance(inputStructs,str):
                nameValue=os.path.basename(iStruct).split('.')[0]
            else:    
                raise ValueError('The nameField variable is not "infer" but the inputStructs variable is not a string and thus the file name is unknown.  No possible way to determine name without "infer" method.')
        # add the results to the dataframe, but don't use append because it has been depricated
        resultsDF.loc[iIndex,'itemID']=nameValue
        resultsDF.loc[iIndex,'fieldValue']=targetValue
        
    # save the results
    # establish the subdirectories if necessary
    if not os.path.isdir(os.path.dirname(savePath)):
        os.makedirs(savePath)
    # save the results
    resultsDF.to_csv(savePath,index=False)               
    return




def tupleDictFromDictFields(inputStructs,targetField,nameField='infer'):
    '''
    This function creates a tuple dictionary, as produced by applyRegexsToDirOfXML, wherein the keys are the tuples corresponding to the identifiers 
    off the inputStructs and the unique values of the target field.  Thus this function assumes that the range of unique values for targetField is 
    reasonably finite, and can produce a matrix-like storage structure wherein the colums correspond to the input identifiers, and the (substantially smaller number)
    of rows correspond to the unique values of the target field.  Violation of the assumption that len(uniqueValues(targetField)) << len(inputStructs) will result in
    a very inefficient storage structure.

    Parameters
    ----------
    inputStructs : list of dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    nameField : string, optional
        A string corresponding to the field, presumed to be present in all input structures, to be used as the identifier for the input structures.  The default is 'infer', which will attempt to infer the name field from the input structures using the detectDataSourceFromSchema to determine which of the currently accepted schemas the input structures conform to.

    Returns
    -------
    tupleDict: dictionary
        A dictionary with tuples as keys and booleans as values, indicating whether the targetField was found in the inputStructs.

    See Also
    --------
    applyRegexsToDirOfXML : Searches a directory of XML files for the presence of a string phrase.  Returns a tuple dictionary.
    convertTupleDictToEfficientDict : Converts a tuple dictionary to a more efficient dictionary structure.
    '''
    import xmltodict
    import os
    import copy

    # first detect what kind of data source we are dealing with by looking at the first item in the inputStructs
    testInput=inputStructs[0]
    # if it's a string then test if it's a file path
    if isinstance(testInput,str):
        # if it's a file path then test if it's a valid file path
        if os.path.isfile(testInput):
            # if it's a valid file path then test if it's an XML file
            if testInput.endswith('.xml'):
                # if it's an XML file then read it in as a dictionary
                inputType='xmlFile'
                # take this opportunity to parse the nameField='infer' logic
                if nameField=='infer':
                    detectedDataSource=detectDataSourceFromSchema(testInput)
                    if detectedDataSource == 'NSF':
                        nameField=['rootTag','Award','AwardID']
                    elif detectedDataSource == 'NIH':
                        nameField=['rootTag','APPLICATION_ID']
                    elif detectedDataSource == 'grantsGov':
                        nameField=['rootTag','OpportunityID']
                    else:
                        raise ValueError('"infer" option for nameField using detectDataSourceFromSchema function returned unrecognized data source.')
                # if the nameField option is not set to "infer" then just use the the filenames, but the actual processing of this will be handled later
                else:
                    nameField='fileName'

            else:
                # if it's not an XML file then raise an error
                raise ValueError('The inputStructs variable contains a file-like string with "xml" extension that is not a valid file path.')
        # if it's a string but not a file, check if it's a valid XML string
        elif testInput.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
            inputType='xmlString'
        # TODO: maybe also consider checking if it's a valid JSON string
    # if it's not a string then check if it's a dictionary
    elif isinstance(testInput,dict):
        inputType='dict'
    # if it's not a string or a dictionary then raise an error
    else:
        raise ValueError('The inputStructs variable contains an item that is not a valid file path, XML string, or dictionary.')
    
    # establish the tuple dictionary
    tupleDict={}

    # TODO consider throwing an error if the wrong combination of inputType and nameField is used
    # now iterate across the inputStructs and extract the targetField and nameField and store them in a tuple dictionary
    for iInput in inputStructs:
        # handle the input appropriately
        if inputType=='xmlFile':
            # read in the input as a dictionary
            with open(iInput) as fd:
                inputDict = xmltodict.parse(fd.read())
            # close the file
            fd.close()
        elif inputType=='xmlString':
            # read in the input as a dictionary
            inputDict = xmltodict.parse(iInput)
        elif inputType=='dict':
            # copy the inputDict to a new variable
            inputDict=copy.deepcopy(iInput)
        else:
            raise ValueError('The inputStructs variable contains an item that is not a valid file path, XML string, or dictionary.')
        # extract the targetField and nameField
        iTargetField= extractValueFromDictField(inputDict,targetField)
        # TODO:  there is currently no handling for case 'fileName'
        iNameField=extractValueFromDictField(inputDict,nameField)
        tupleDict[(iTargetField,iNameField,)]=True

    # return the tuple dictionary
    return tupleDict

def extractValueFromDictField(inputDict,fieldList):
    """
    This function extracts the value from a nested dictionary field.

    Parameters
    ----------
    inputDict : dictionary
        A dictionary containing the nested field to be extracted.
    fieldList : list of strings
        A list of strings corresponding to the nested fields to be extracted.
        
    Returns
    -------
    fieldValue : string
        A string corresponding to the value of the nested field.   
    """
    # iterate across the fieldList to get the nested field
    for iField in fieldList:
        try:
            inputDict=inputDict[iField]
        except:
            # throw an error indicating which file failed
            raise ValueError('Field ' + str(iField) + ' not found in dictionary ' + str(inputDict) + '.') 
    # extract the targetField
    fieldValue=inputDict
    # return the targetField
    return fieldValue

def searchInputListsForKeywords(inputLists,keywordList):
    """
    Divides up the items in the inputLists--for items whose description includes
    an item from the input keywordList variable--into groups associated by keyword.

    Returns a dictionary wherein the keys are keywords and the values are lists of items
    wherein the the keyword was found in the associated description.

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

    # next we iterate across the keywords and compiled regexes and search the inputLists for the keywords
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

def applyRegexToInput(inputText,stringPhrase):
    """
    Applies a regex search to the inputText and returns a boolean indicating whether the stringPhrase was found.

    NOTE: case sensitive is depricated.

    Parameters
    ----------
    inputText : string
        A string to be assessed for the presence of the stringPhrase.
    stringPhrase : string
        A string corresponding to the phrase one is interested in assessing the occurrences of. 

    Returns
    -------
    bool
        A boolean indicating whether the stringPhrase was found in the inputText.
    """
    import re

    compiledSearch=re.compile(stringPhrase)
    try:
        if bool(compiledSearch.search(inputText)):
            return True
        else:
            return False
    except:
        return False

def applyRegexToXMLFile(xmlFilePath,stringPhrase,fieldsSelect):
    """
    Applies a regex search to the inputText and returns a boolean indicating whether the stringPhrase was found.
    
    NOTE: case sensitive is depricated.

    Parameters
    ----------
    xmlFilePath : string
        A string corresponding to the path to the xml file to be searched.  Can also be the file contents as a string.
    stringPhrase : string
        A string corresponding to the phrase one is interested in assessing the occurrences of.
    fieldsSelect : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.

    Returns
    -------
    bool
        A boolean indicating whether the stringPhrase was found in the inputText.
    """
    import xmltodict
    import re
    # if the xmlFilePath is a string, then assume it's the file path and load the file
    if type(xmlFilePath)==str:
        with open(xmlFilePath) as f:
            xmlDict=xmltodict.parse(f.read())
    # close the file
        f.close()
    else:
        xmlDict=xmltodict.parse(xmlFilePath)
    # use extractValueFromDictField to extract the relevant field
    targetRegexText=extractValueFromDictField(xmlDict,fieldsSelect)

    # if xmlDict is empty, just go ahead and return False
    if targetRegexText==None:
        # print a warning
        print('WARNING: targetRegexText is None')
        return False
    # otherwise, check if it's empty
    # NOTE: for a while this was set up wrong and was triggering on any length greater than zero
    elif len(targetRegexText)==0:
        # print a warning
        print('WARNING: targetRegexText is empty')
        return False
    # otherwise proceed with the search
    
    # now that we have the relevant contet, we need to convert the text to nlp-ready text
    # use prepareTextForNLP(inputText,stopwordsList=None,lemmatizer=None)
    targetRegexText=prepareTextForNLP(targetRegexText)
  
    stringPhrase=prepareTextForNLP(stringPhrase)

    # use applyRegexToInput
    outputBool=applyRegexToInput(targetRegexText,stringPhrase)

    return outputBool

def prepareTextForNLP(inputText,stopwordsList=None,lemmatizer=None):
    """
    This function is designed to take a string of text and prepare it for NLP analysis.  It does this by:
        1) converting to lowercase
        1.5) replacing dashes with spaces
        2) removing punctuation
        3) removing stopwords
        4) removing digits
        5) removing whitespace
        6) removing single character words
        7) lemmatizing
    Inputs:
        inputText: string
            The text to be prepared for NLP analysis
    Outputs:
        outputText: string
            The text prepared for NLP analysis
    """
    import re
    import nltk
    # download the stopwords and wordnet corpora if they haven't already been downloaded
    nltk.download('stopwords',quiet=True)
    nltk.download('wordnet',quiet=True)
    # import the necessary libraries
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    # convert to lowercase
    outputText=inputText.lower()
    # replace dashes with spaces
    outputText=re.sub(r'-',' ',outputText)
    # remove punctuation
    outputText=re.sub(r'[^\w\s]','',outputText)
    # remove stopwords
    if stopwordsList is None:
        stop_words = set(stopwords.words('english'))
    else:
        stop_words = set(stopwordsList) 
    outputText = ' '.join([word for word in outputText.split() if word not in stop_words])
    # remove digits
    outputText=re.sub(r'\d+','',outputText)
    # remove whitespace
    outputText=re.sub(r'\s+',' ',outputText)
    # remove single character words
    outputText=re.sub(r'\b[a-zA-Z]\b','',outputText)
    # lemmatize
    if lemmatizer is None:
        lemmatizer = WordNetLemmatizer()
    else:
        lemmatizer=lemmatizer
    outputText=' '.join([lemmatizer.lemmatize(word) for word in outputText.split()])
    return outputText

def prepareAllTextsForNLP(inputTexts,stopwordsList=None,lemmatizer=None):
    """
    This function is designed to take a list of strings of text and prepare them for NLP analysis.  It does this by:
        1) converting to lowercase
        1.5) replacing dashes with spaces
        2) removing punctuation
        3) removing stopwords
        4) removing digits
        5) removing whitespace
        6) removing single character words
        7) lemmatizing
    
    Also, it is optinally possible to run this function in a parralized fashion, if dask is installed.
    
    Inputs:
        inputTexts: list of strings
            The texts to be prepared for NLP analysis
        stopwordsList: list of strings
            A list of stopwords to be removed from the text
        lemmatizer: nltk.stem.WordNetLemmatizer
            A lemmatizer to be used to lemmatize the text
    Outputs:
        outputTexts: list of strings
            The texts prepared for NLP analysis
    """
    outputTexts=[]
    for iText in inputTexts:
        outputTexts.append(prepareTextForNLP(iText,stopwordsList=stopwordsList,lemmatizer=lemmatizer))
    return outputTexts

def detectDataSourceFromSchema(testDirOrFile):
    """
    This function is designed to detect the data source of a given file or directory based on the schema of the file(s).
    Inputs:
        testDirOrFile: string
            A string corresponding to the path to the file or directory to be tested
    Outputs:
        dataSource: string
            A string corresponding to the data source of the file or directory.  Currently either "NSF" or "grantsGov"
    """
    import os
    import xmltodict
    import json

    # parametrs to set:
    # minFieldThreshold: int
    #  The minimum number of fields that must match known fields for the corresponding schema in order for it to be considerd a valid mathc
    minFieldThreshold=3
    # A list of fields found in the NSF schema
    NSFfields=['AwardID','AbstractNarration','AwardTitle','AwardAmount','NSF_ID','Directorate']
    # A list of fields found in the grants.gov schema
    grantsGovFields=['OpportunityID','Synopsis','Title','EstimatedTotalProgramFunding','AgencyCode','Description']

    # for a detailed overview of the NSF grant award data schema view:
    # https://github.com/macks22/nsf-award-data/blob/master/docs/nsf-xml-schema-details.md#xml-schema-breakdown
    # the schema itself can be downloaded from here:
    # https://www.nsf.gov/awardsearch/resources/Award.xsd

    # for a detailed overview of the grants.gov grant award data schema view:
    # http://apply.grants.gov/system/OpportunityDetail-V1.0
    # the schema itself can be downloaded from here:
    # https://apply07.grants.gov/apply/system/schemas/OpportunityDetail-V1.0.xsd
    # determine if input is file or directory
    # first check if it's a string
    if type(testDirOrFile)==str:
        # if it's a string, then check if it's a directory
        if os.path.isdir(testDirOrFile):
            # if it's a directory, then simply pick the first xml file in the directory
            testFile=os.listdir(testDirOrFile)[0]
            with open(testFile) as f:
                xmlDict=xmltodict.parse(f.read())
            f.close()
        # if it's a file, then simply use that file
        elif os.path.isfile(testDirOrFile):
            testFile=testDirOrFile
            with open(testFile) as f:
                xmlDict=xmltodict.parse(f.read())
            f.close()
        else:
            # if it's a string, but neither of the above, then try and parse it as xml or json
            try:
                xmlDict=xmltodict.parse(testDirOrFile)
            except:
                try:
                    xmlDict=json.loads(testDirOrFile)
                except:
                    print('Error: input is a string but is not a valid file, directory, xml, or json')
                    return None
    # if it's a dictionary, then assume it's already been parsed
    elif type(testDirOrFile)==dict:
        xmlDict=testDirOrFile
    # otherwise, return an error
    else:
        print('Error: input of type '+str(type(testDirOrFile))+' is not a valid file, directory, xml, json, or dict')
        return None
    # read in the presumptive xml file using xmltodict
    # hopefully it is validly structured and we don't need to use beautiful soup to fix it

    # close the file

    # now check it for the relevant fields
    # recurisvely search the xmlDict for all keys, including exhaustive search of nested dictionaries
    def getKeys(inputDict):
        keys=[]
        for key in inputDict.keys():
            keys.append(key)
            if type(inputDict[key])==dict:
                keys.extend(getKeys(inputDict[key]))
        return keys
    allKeys=getKeys(xmlDict)

    # now check if the NSF fields are present
    # NOTE: add checks for other data schemas here as additonal data sources are added
    NSFfieldCount=0
    for NSFfield in NSFfields:
        if NSFfield in allKeys:
            NSFfieldCount+=1
    # now check if the grants.gov fields are present
    grantsGovFieldCount=0
    for grantsGovField in grantsGovFields:
        if grantsGovField in allKeys:
            grantsGovFieldCount+=1
    # now determine which data source is the best match
    if NSFfieldCount>=minFieldThreshold:
        dataSource='NSF'
    elif grantsGovFieldCount>=minFieldThreshold:
        dataSource='grantsGov'
    else:    
        dataSource=None
    return dataSource


