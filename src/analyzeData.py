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
            tupleDict[(iStringPhrase,iFile.replace('.xml',''))]=False

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
            tupleDict[(iStringPhrase,iFile.replace('.xml',''))]=applyRegexToXMLFile(os.path.join(directoryPath,iFile),iStringPhrase,fieldsSelect)

    return tupleDict

def quantifyDataCompleteness(DForFilePaths):
    """
    This is a data quality assesment function which computes the number of empty / null values for each field in a given data set.
    It returns a pandas dataframe with two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
    In addition to having a row for each field in the data structure, it also has a row that reflects the total number of records assesed, which is functionally the 
    maximum potential value for any field (e.g. in the case of a field that is empty for all records).

    Parameters
    ----------
    DForFilePaths : either a pandas dataframe or a list of strings
        Either a pandas dataframe containing the records to be assesed (as rows) or a list of strings corresponding to the paths to the files (in xml or json format, each file treated as individual records) to be assessed.

    Returns
    -------
    dataCompletenessDF : pandas dataframe
        A pandas dataframe with two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
        The last row is the total number of records assessed.

    """
    import os
    import pandas as pd
    import json
    import xmltodict
    import numpy as np
    
    # go ahead and create the output dataframe, which will have two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
    dataCompletenessDF=pd.DataFrame(columns=['fieldName','numEmpty'])

    # first, determine if the input is a pandas dataframe or a list of file paths
    # we'll handle the pandas dataframe case first because that is the easier case
    if isinstance(DForFilePaths,pd.DataFrame):
        # if it's a pandas dataframe, create the output dataframe, which will have two columns:  the first column is the field name and the second column is the number of empty / null values for that field.
       
        # iterate across the columns in the input dataframe
        for iCol in DForFilePaths.columns:
            # determine the number of empty values in the column using the isempty function
            numEmpty=DForFilePaths[iCol].apply(isempty).sum()
            # add a row to the output dataframe
            dataCompletenessDF=dataCompletenessDF.append({'fieldName':iCol,'numEmpty':numEmpty},ignore_index=True)
        # add a row for the total number of records
        dataCompletenessDF=dataCompletenessDF.append({'fieldName':'totalNumRecords','numEmpty':DForFilePaths.shape[0]},ignore_index=True)

    # now we'll handle the case where the input is a list of file paths
    elif isinstance(DForFilePaths,list):
        # if it's a list of file paths, this could get quite demanding.  We'll approach this by creating an intermediary pandas data frame to hold per-record results.
        # at the moment we don't know what the fields are, but we do know that there will be a row for each record.
        boolRecordDF=pd.DataFrame()
        # HOWEVER, because appending to a dataframe is very slow, we'll just append to a list
        boolRecordDFsList=[[] for i in range(len(DForFilePaths))]
        # hopefully the records all have the same fields,
        # I believe that pandas can gracefully handle the case where the fields are not the same, but I'm not sure
        # iterate across the files
        for recordIndex,iFile in enumerate(DForFilePaths)   :
            # determine the file extension
            fileExtension=os.path.splitext(iFile)[1]
            # if the file extension is .xml
            if fileExtension=='.xml':
                # debug try implementation
                try:
                    # load it into a dictionary using the xmltodict library
                    iDict=xmltodict.parse(open(iFile,'r').read())
                    # I'm going to assume that there's a singular root tag, and so whatever that is, we'll get it and convert the full content to a dataframe
                    # get the root tag
                    rootTag=list(iDict.keys())[0]
                    # extract content to a separate dictionary (is this necessary?)
                    extractedDictionary=iDict[rootTag]
                    # pandas is having some trouble with converting the dictionary to a pandas file, potentially due to nesting.  As a work around we'll iterate through the dictionary keys and create a boolean vector, which we will then use to create a pandas dataframe
                    # create an empty array to hold the boolean values
                    boolArray=np.zeros(len(extractedDictionary.keys()),dtype=bool)
                    # iterate across the keys
                    for iKeyIndex,iKey in enumerate(extractedDictionary.keys()):
                        # determine if the value is empty
                        boolArray[iKeyIndex]=isempty(extractedDictionary[iKey])
                    # use the boolArray and the keys to create a pandas dataframe, the keys should serve as the columns
                    # initially suggested, not sure what to make of the reshape
                    #iDFbool=pd.DataFrame(boolArray.reshape(1,-1),columns=list(extractedDictionary.keys()))
                    iDFbool=pd.DataFrame(boolArray.reshape(1,-1),columns=list(extractedDictionary.keys()))
                    
                except:
                    # raise an error
                    raise ValueError('The file '+iFile+' could not be parsed by the xmltodict library. \n rootTag: '+rootTag+'\n iDict: '+str(iDict) + '\n extractedDictionary.keys(): '+str(extractedDictionary.keys()))
                #iDF=pd.DataFrame.from_dict(iDict[list(iDict.keys())[0]])
            # if the file extension is .json
            elif fileExtension=='.json':
                # debug try implementation
                try:
                    # load it into a dictionary using the json library
                    iDict=json.load(open(iFile,'r'))
                    # convert the full content to a dataframe
                    iDF=pd.DataFrame.from_dict(iDict)
                    # apply the isempty function to each column
                    iDFbool=iDF.apply(isempty)
                except:
                    # raise an error
                    raise ValueError('The file '+iFile+' could not be parsed by the json library. \n iDict: '+str(iDict) + '\n iDict.keys(): '+str(iDict.keys()))
            # now that we have the content in a dataframe, we can apply the isempty function to each column

            boolRecordDFsList[recordIndex]=iDFbool
        # now that we have the intermediary list, we can concatenate it into a dataframe
        boolRecordDF=pd.concat(boolRecordDFsList)
        # now we can iterate across the columns in the dataframe
        # create a holder for the number of empty values in each column
        numEmptyVec=np.zeros(boolRecordDF.shape[1])
        for iIndex,iCol in enumerate(boolRecordDF.columns):
            # determine the number of empty values in the column using the isempty function
            numEmpty=boolRecordDF[iCol].sum()
            # add that to the relevant position in the numEmptyVec
            numEmptyVec[iIndex]=numEmpty
            #dataCompletenessDF=dataCompletenessDF.append({'fieldName':iCol,'numEmpty':numEmpty},ignore_index=True)
        # add a row for the total number of records
        recordTotal=boolRecordDF.shape[0]
        # add the total number of records to the numEmptyVec
        numEmptyVec=np.append(numEmptyVec,recordTotal)
        
        # create a vecotr for the column names
        colNamesVec=np.array(boolRecordDF.columns)
        # add 'totalNumRecords' to the colNamesVec
        colNamesVec=np.append(colNamesVec,'totalNumRecords')

        # create a dataframe from the numEmptyVec and colNamesVec
        dataCompletenessDF=pd.DataFrame({'fieldName':colNamesVec,'numEmpty':numEmptyVec})

        # this should avoid warnings about setting values on a copy of a slice from a dataframe and using append


    return dataCompletenessDF






def isempty(inputContent):
    '''
    This function determines whether the input is null, empty, '', zero, or NaN, or equivalent.
    Is this ugly?  Yes it is. 

    NOTE: Technically this is a duplicate of the same named function in the processData function set,
    but is included here in order to avoid cross-module dependencies.  At least for now.

    Inputs:
        inputContent: any
            Any input content.
    Outputs:    
        isEmpty: boolean
            A boolean indicating whether the input is null, empty, '', zero, or NaN, or equivalent.
    '''
    import numpy as np
    try:
        # if the input is null, return True
        if inputContent is None:
            return True
        else:
            raise Exception
    except:
        try:
            # if the input is empty, return True
            if inputContent=='':
                return True
            else:
                raise Exception
        except:
            try:
                # if the input is zero, return True
                if inputContent==0:
                    return True
                else:
                    raise Exception
            except:
                try:
                    # if the input is NaN, return True
                    if np.isnan(inputContent):
                        return True
                    else:
                        raise Exception
                except:
                    # otherwise, return False
                    return False

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
            efficientDict['rowDescription']='Searched Keywords'
            efficientDict['colDescription']='NIH Application Number'
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
    inputStructs : list of strings, xml strings, or dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the nested sequence of fields to be searched.  First field is the root tag.  Last field is the field to be searched.  Will throw an error if not specified correctly.
    nameField : string, optional
        A string corresponding to the field, presumed to be present in all input structures, to be used as the name for the input structure.  The default is 'infer', which will attempt to infer the name field from the input structures.
    savePath : string, optional
        A string corresponding to the path to the directory where the results should be saved.  The default is '', which will save the results in the current directory.
        If savePath is set to None, then the results will not be saved.
    
    Returns 
    -------

    resultsDF : pandas dataframe
        A pandas dataframe containing the results of the field extraction.
   
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
        # NOTE: come back and clean up this logic later, it is not doing what is intended at the moment.
        if not nameField=='infer':
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
    if savePath is not None:
    # establish the subdirectories if necessary
        if not os.path.isdir(os.path.dirname(savePath)):
            os.makedirs(savePath)
        # save the results
        resultsDF.to_csv(savePath,index=False)               
    return resultsDF

def wordCountForField(inputStructs,targetField,nameField='infer',savePath=''):
    """
    Using fieldExtractAndSave, this function extracts the (presumably) text content of the target field, for each
    input structure and then performs a word count on the extracted text.  The results are returned as a pandas dataframe
    and saved down to the specified savePath if savePath is not None.

    Parameters
    ----------
    inputStructs : list of strings, xml strings, or dictionaries
        A list of valid objects (file paths, xml strings, or dictionary objects) to be searched.
    targetField : list of strings
        A list of strings corresponding to the *nested* sequence of fields to be searched.  First field is the root tag.  Last field is
        the target field.  Intermediate fields are nested tags.
    nameField : list of strings
        A list of strings corresponding to the *nested* sequence of fields to be searched.  First field is the root tag.  Last field is
        the name field.  Intermediate fields are nested tags.  If set to 'infer', then the name field is inferred from the file name.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.

    Returns
    -------
    resultsDF : pandas dataframe
        A pandas dataframe with two columns: 'itemID' and 'wordCount'. The 'itemID' column contains the name of the input structure, and the 'wordCount'
        column contains the word count of the target field for each input structure.
    """
    import pandas as pd
    import re
    import os
    # extract the target field
    resultsDF=fieldExtractAndSave(inputStructs,targetField,nameField=nameField,savePath=None)
    # what we should now have is a pandas dataframe with two columns: 'itemID' and 'fieldValue'
    # the field value should be a string containing the text content of the target field
    # we'll use a regex method to count the number of words
    for iIndexes,iRows in resultsDF.iterrows():
        # get the text content for the current entry
        currentText=iRows['fieldValue']
        # if it isn't empty, then perform the word count
        if not pd.isnull(currentText):
            # perform the word count
            # alternatively: len(re.findall(re.compile('\\b[A-Za-z]+\\b'), currentText))
            resultsDF.loc[iIndexes,'wordCount']=len(re.findall(r'\w+', currentText))
        # if it is empty, then set the word count to zero
        else:
            resultsDF.loc[iIndexes,'wordCount']=0
    # save the results
    if savePath is not None:
    # establish the subdirectories if necessary
        if not os.path.isdir(os.path.dirname(savePath)):
            os.makedirs(savePath)
        # save the results
        resultsDF.to_csv(savePath,index=False)
    return resultsDF

def countsFromCoOccurrenceMatrix(coOccurrenceMatrix,rowsOrColumns='rows',axisLabels=None,savePath=''):
    """
    This function takes in a co-occurrence matrix and returns a pandas dataframe with the counts of the number of times
    each item *OCCURS IRRESPECTIVE OF COOCURRENCE WITH OTHER ITEMS*. In other words, this function sums the rows or columns
    (the matrix should be symmetric) and returns the results as a pandas dataframe.

    Parameters
    ----------
    coOccurrenceMatrix : numpy array or pandas dataframe
        A square matrix with the rows and columns corresponding to the same set of items.
        In the typical case in this package, wherein this is a term co-occurrence matrix, the rows and columns
        correspond to the instances of co-occurrence of the terms.
    rowsOrColumns : string
        Either 'rows' or 'columns', depending on whether you want the counts to be computed with respect to the rows or the columns of the input matrix.
        Probably doesn't make sense if you target the larger of the two dimensions of the input matrix.
    axisLabels : list of strings
        A list of strings corresponding to the labels of the rows or columns of the input matrix.  If None, then the labels are assumed to be integers.
    savePath : string
        The path to which the results should be saved

    Returns
    -------
    resultsDF : pandas dataframe
        A pandas dataframe with two columns: 'itemID' and 'count'. The 'itemID' column contains the label of the row or column of the input matrix, and the 'count'
        column contains the count of the number of times each item occurs in the in the input matrix. 
    
    """
    import pandas as pd
    import numpy as np
    import os
    # if the input is a pandas dataframe, then convert it to a numpy array
    if isinstance(coOccurrenceMatrix,pd.DataFrame):
        coOccurrenceMatrix=coOccurrenceMatrix.values
        # if the axis labels are not specified, then use either the row or column labels of the input matrix
        if axisLabels is None:
            if rowsOrColumns=='rows':
                axisLabels=coOccurrenceMatrix.index
            elif rowsOrColumns=='columns':
                axisLabels=coOccurrenceMatrix.columns
    # if it's a numpy array we don't need to do anything
    elif isinstance(coOccurrenceMatrix,np.ndarray):
        # if the axis labels are not specified, then use integers
        if axisLabels is None:
            axisLabels=np.arange(coOccurrenceMatrix.shape[0])
    # if it's not a numpy array or a pandas dataframe, then raise an error
    else:
        raise ValueError('Input matrix must be a numpy array or pandas dataframe')
    # sum the rows or columns of the input matrix (should be equivalent)
    if rowsOrColumns=='rows':
        results=np.sum(coOccurrenceMatrix,axis=1)
    elif rowsOrColumns=='columns':
        results=np.sum(coOccurrenceMatrix,axis=0)
    # convert the results to a pandas dataframe
    resultsDF=pd.DataFrame({'itemID':axisLabels,'count':results})
    # save the results
    if savePath is not None:
    # establish the subdirectories if necessary
        if not os.path.isdir(os.path.dirname(savePath)):
            os.makedirs(savePath)
        # save the results
        resultsDF.to_csv(savePath,index=False)
    return resultsDF


def coOccurrenceMatrix(occurenceMatrix,rowsOrColumns='rows',savePath='',rowLabels=None,colLabels=None):
    """
    This function takes in a non-square matrix and computes the co-occurrence matrix, which is a square matrix
    where each entry is the number of times an item in the row occurs with an item in the column.  The results
    are returned with respect to either the rows or the columns of the input matrix, depending on the input of 
    the rowsOrColumns variable.  

    In this way, this analysis only makes sense if you select the smaller of the two dimensions of the input matrix

    Parameters
    ----------
    occurenceMatrix : numpy array or pandas dataframe
        A non-square matrix with the rows corresponding to one set of items and the columns corresponding to another set of items.
    rowsOrColumns : string
        Either 'rows' or 'columns', depending on whether you want the co-occurrence matrix to be computed with respect to the rows or the columns of the input matrix.
        'columns' will analyze co-occurences _within_ the columns of the input matrix, and 'rows' will analyze co-occurences _within_ the rows of the input matrix.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.

    Returns
    -------
    coOccurrenceMatrix : numpy array
        A square matrix with the rows and columns corresponding to the items in the rows or columns of the input matrix, depending on the rowsOrColumns variable.
        The i and j elements are understood to correspond to the same set of items, such that the i,j element is the number of times the i item occurs with the j item.
        
        In the case of a boolean matrix representing keywords along the colums and grants along the rows, a co-occurance matrix for the 
        columns would indicate how often each keyword occurs with each other keyword.  A co-occurance matrix for the rows would indicate the number
        of terms shared by each pair of grants.
        NOTE: keywords are actually the rows.
    
    """
    import numpy as np
    import pandas as pd
    import h5py

    """
    this doesn't do what was expected / intended.  rowsums= number hits per term across documents, colsums = number of terms per document.
    Thus if rows are terms and columns are records, the dotproduct of the transpose of the matrix with the matrix will give you the number of times each term co-occurs with each other term.
    whereas the dotproduct of the matrix with the transpose of the matrix will give you the number of terms shared by each pair of records.
    
    # lets go ahead and check what the sum would be across each axis of the input matrix
 
    dimPassCheck=np.zeros(occurenceMatrix.ndim,dtype=bool)
    for iDims in range(occurenceMatrix.ndim):
        # get the sum across the current axis
        currDimSums=np.sum(occurenceMatrix,axis=iDims)
        # a count of co-occurrences only makes sense of things can co-occur along a given axis, so we'll check to see if there are any summed values of two or greater for each axis
        # if there are no sums of two or greater along this axis, then this axis isn't a valid choice for performing a co-occurrence analysis.
        dimPassCheck[iDims]=np.any(currDimSums>=2)

    # use dimPassCheck to determine if the axis requested in rowsOrColumns is valid
    # remember, requesting "rows" means that the desired output is a square matrix with N rows and columns, where N is the number of rows in the input matrix (and vice versa for "columns")
    if rowsOrColumns=='rows':
        if not dimPassCheck[0]:
            raise ValueError('The rowsOrColumns variable is set to "rows" but there are no rows with two or more values in the input matrix.  Thus, there are no co-occurrences along the specified dimension')
    elif rowsOrColumns=='columns':
        if not dimPassCheck[1]:
            raise ValueError('The rowsOrColumns variable is set to "columns" but there are no columns with two or more values in the input matrix.  Thus, there are no co-occurrences along the specified dimension')
    """
    # if the input is a pandas dataframe, then convert it to a numpy array
    if isinstance(occurenceMatrix,pd.DataFrame):
        currRowNames=occurenceMatrix.index
        currColNames=occurenceMatrix.columns
        occurenceMatrix=occurenceMatrix.values
    # if the input is a numpy array, then proceed
    elif isinstance(occurenceMatrix,np.ndarray) and not rowLabels==None and not colLabels==None:
        # if it's not a pandas dataframe, and instead a numpy array, then you're not going to get row and column names
        # so we have to generate dummy names, which will simply be integers
        currRowNames=rowLabels
        currColNames=colLabels
    elif isinstance(occurenceMatrix,np.ndarray):
        # if it's not a pandas dataframe, and instead a numpy array, then you're not going to get row and column names
        # so we have to generate dummy names, which will simply be integers
        currRowNames=np.arange(occurenceMatrix.shape[0])
        currColNames=np.arange(occurenceMatrix.shape[1])
    # if the input is neither a pandas dataframe nor a numpy array, then raise an error
    else:
        raise ValueError('The input must be a pandas dataframe or a numpy array')
    # parse the case logic for rows or columns
    if rowsOrColumns=='rows':
        # compute the co-occurrence matrix
        # coOccurrenceMatrix=np.dot(occurenceMatrix.T,occurenceMatrix)
        # is it actually
        coOccurrenceMatrix=np.dot(occurenceMatrix,occurenceMatrix.T)
        # set the row names
        rowNames=currRowNames
        # set the column names
        columnNames=currRowNames
    elif rowsOrColumns=='columns':
        # compute the co-occurrence matrix
        # coOccurrenceMatrix=np.dot(occurenceMatrix,occurenceMatrix.T)
        # is it actually
        coOccurrenceMatrix=np.dot(occurenceMatrix.T,occurenceMatrix)
        # set the row names
        rowNames=currColNames
        # set the column names
        columnNames=currColNames
    # if the rowsOrColumns variable is not set to 'rows' or 'columns', then raise an error
    else:
        raise ValueError('The rowsOrColumns variable must be set to either "rows" or "columns"')
    
    # determine the desired saving behavior
    if savePath is not None:
        # in any of the available cases when saving, it will be wortwhile to know whether the 
        # row / column labels (indexes) are simply sequential integers or not.  If they are sequential integers we can basically ignore them.
        # run a check to see if they are sequential integers
        # we'll use a try except here, because we don't know if the input rowNames is simply the output of DataFrame.index (and thus a list of strings, integers, etc.) or if it's a numpy array from np.arange
        try:
            # if it's a numpy array, then we can use the np.all function to check if it's sequential
            if np.all(np.arange(len(rowNames))==[int(x) for x in rowNames]):
                indexesMeaningful=False
            else:
                indexesMeaningful=True
        except:
            # if rowNames is made up of of strings, you'll get a `ValueError: invalid literal for int()` error
            # in this case, we'll just assume that the indexes are meaningful
            indexesMeaningful=True


        # if it's not none, then check it if is blank (''), or a specific format
        if savePath=='':
            # if it's blank, then they haven't provided a desired format, so we have to use a heuristic for this
            # we'll just set an arbitrary value here, to serve as the heuristic limit
            # in this case, what the value represents is the number of rows (or columns) that we would consider the maximum reasonable to store in a csv
            # in essence: if there are sufficiently few values, then it's fine to store the data as an uncompressed csv.
            # for example, a 1000 by 1000 matrix would be 1,000,000 numeric values which would be 8,000,000 bytes, or 8 MB for float 64 (or 4 MB for float 32)
            thresholdCSV=1000
            # also set the string for the default name
            defaultName='coOccurrenceMatrix'
            # if the number of rows or columns is less than the threshold, then save as a csv
            if coOccurrenceMatrix.shape[0]<thresholdCSV:
                # if the indexes are meaningful, then save the row and column names as well
                if indexesMeaningful:
                    # save the co-occurrence matrix as a csv
                    # make sure that it is being saved with the right column and row names, in accordance with rowsOrColumns
                    if rowsOrColumns=='rows': 
                        coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=rowNames,columns=rowNames)
                    elif rowsOrColumns=='columns':
                        coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=columnNames,columns=columnNames)
                    #coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=rowNames,columns=columnNames)
                    coOccurrenceMatrixDF.to_csv(defaultName+'.csv')
                else:
                    # save the co-occurrence matrix as a csv
                    coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=None,columns=None)
                    coOccurrenceMatrixDF.to_csv(defaultName+'.csv')
            # if the number of rows or columns is greater than the threshold, then save as an hdf5
            else:
                # if the indexes are meaningful, then save the row and column names as well
                if indexesMeaningful:
                    # save the co-occurrence matrix as an hdf5
                    with h5py.File(defaultName+'.hdf5','w') as f:
                        f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
                        f.create_dataset('rowName',data=rowNames,compression='gzip')
                        f.create_dataset('colName',data=columnNames,compression='gzip')
                else:
                    # save the co-occurrence matrix as an hdf5
                    with h5py.File(defaultName+'.hdf5','w') as f:
                        f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
                # in either case, close the file
                f.close()
        # if it's not blank, then check if it's a csv or an hdf5
        elif savePath.endswith('.csv'):
            # if it's a csv, then save the co-occurrence matrix as a csv essentially the same way as above
            if indexesMeaningful:
                # save the co-occurrence matrix as a csv
                if rowsOrColumns=='rows': 
                        coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=rowNames,columns=rowNames)
                elif rowsOrColumns=='columns':
                    coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=columnNames,columns=columnNames)
                coOccurrenceMatrixDF.to_csv(savePath)
            else:
                # save the co-occurrence matrix as a csv
                coOccurrenceMatrixDF=pd.DataFrame(coOccurrenceMatrix,index=None,columns=None)
                coOccurrenceMatrixDF.to_csv(savePath)
        elif savePath.endswith('.hdf5'):
            # if it's an hdf5, then save the co-occurrence matrix as an hdf5 essentially the same way as above
            if indexesMeaningful:
                # save the co-occurrence matrix as an hdf5
                with h5py.File(savePath,'w') as f:
                    f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
                    f.create_dataset('rowName',data=rowNames,compression='gzip')
                    f.create_dataset('colName',data=columnNames,compression='gzip')
            else:
                # save the co-occurrence matrix as an hdf5
                with h5py.File(savePath,'w') as f:
                    f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
            # in either case, close the file
            f.close()

        # if it's not blank, csv, or hdf5, or None then raise an error
        else:
            raise ValueError('The savePath variable must be either blank (''), None, or end with ".csv" or ".hdf5"')      

    # return the results
    return coOccurrenceMatrix

def convertStandardHDF5toPandas(inputHDF5obj):
    """
    In the current toolset, HDF5 files are formatted with the following standard fields:

        f.create_dataset('dataMatrix',data=coOccurrenceMatrix,compression='gzip')
        f.create_dataset('rowName',data=rowNames,compression='gzip')
        f.create_dataset('colName',data=columnNames,compression='gzip')

    Additionally, the dataMatrix, which is an np.array, is typically exceptionally sparse and (usually but not always) boolean.

    This function takes in an HDF5 file with this standard format and returns a pandas dataframe with the dataMatrix as the values and the row and column names as the indexes.
    
    Parameters
    ----------
    inputHDF5obj : hdf5 object
        An hdf5 object with the standard format described above.

    Returns
    -------
    dataMatrixDF : pandas dataframe
        A pandas dataframe with the dataMatrix as the values and the row and column names as the indexes.
    """
    import pandas as pd
    import numpy as np
    # get the column and row names, and convert them to strings.  Remember, they are stored as byte strings in the hdf5 file
    columnNames=[x.decode('utf-8') for x in inputHDF5obj['colName']]
    rowNames=[x.decode('utf-8') for x in inputHDF5obj['rowName']]
    # for now we'll assume it's boolean and that even if the data array is large we don't need to 
    # convert it to a sparse matrix
    dataMatrixDF=pd.DataFrame(inputHDF5obj['dataMatrix'],index=rowNames,columns=columnNames)
    return dataMatrixDF

def sumMergeMatrix_byCategories(matrix,categoryKeyFileDF,targetAxis='columns',savePath=''):
    """
    This function takes in a matrix and category dictionary (in the form of a two column pandas dataframe) and returns a new matrix
    where the elements of the specified axis have been condensed into the agglomerations specified by the category dictionary.
    In this way, the output matrix will retain the same number of opposite axis elements, but will have N number of `targetAxis` elements,
    where N is the number of unique categories in the category dictionary.

    Parameters
    ----------
    matrix : pandas dataframe
        A matrix of some sort, presumably bool, but potentially numeric.  The column / row indexes should correspond to the 
        identifiers (first column) in the `categoryKeyFileDF`, and be consistent with the axis requested in the `targetAxis` variable.
    categoryKeyFileDF : pandas dataframe
        A two column pandas dataframe where the first column contains the identifiers (presumably `itemID`) 
        and the second column contains the category labels (presumably `fieldValue`); presumably as in the convention of the output of fieldExtractAndSave.
    targetAxis : string
        Either 'rows' or 'columns', depending on whether you want to sum merge the rows or columns of the input matrix.  This is the axis
        across which the identifiers (from categoryKeyFileDF[`itemID`]) will be searched for.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.  If '', then the results are saved to the current directory.

    Returns
    -------
    sumMergeMatrix : pandas dataframe
        A pandas dataframe with summations across the specified axis for each unique category in the category dictionary.  The non-requested axis's 
        indexes should be preserved, however the requested axis's indexes should be replaced with the unique categories from the category dictionary.
    
    NOTE: consider refactoring this in light of the hd5 functionality implemented in subsetHD5DataByKeyfile
    """
    import pandas as pd
    import numpy as np
    import os
    import h5py
    # check if the input matrix is a pandas dataframe
    # if it is, then proceed
    # if it isn't then raise an error explaning why a pandas dataframe is necessary (the column / row indexes need to be matched against the category dictionary))
    if not isinstance(matrix,pd.DataFrame):
        raise ValueError('The input matrix must be a pandas dataframe in order to match category indentities from `categoryKeyFileDF` with specific records in the matrix.')
    
    # make an attempt to parse the input categoryKeyFileDF.  Start by trying to index into the columns 'itemID' and 'fieldValue'.  If that doesn't work, throw a warning and index into the first two columns, with the first being assumed to be the equivalent of 'itemID' and the second assumed to be the equivalent of 'fieldValue'.
    try:
        recordIDs=categoryKeyFileDF['itemID'].values
        categoryLabels=categoryKeyFileDF['fieldValue'].values
    except:
        print('Warning: The input categoryKeyFileDF does not have the expected column names.  Attempting to infer the appropriate columns.  THIS MAY RESULT IN AN ERROR')
        recordIDs=categoryKeyFileDF.iloc[:,0].values
        categoryLabels=categoryKeyFileDF.iloc[:,1].values
    # go ahead and establish the unique categories
    uniqueCategories=np.unique(categoryLabels)

    # go ahead and use the targetAxis to obtain the appropriate axis labels
    # TODO: consider updating this to accept integer-based indexing to indicate dimension

    rowLabels=matrix.index
    columnLabels=matrix.columns

    # initialize a new matrix to store the results, but take in to account targetAxis
    if targetAxis=='rows':
        sumMergeMatrix=pd.DataFrame(index=uniqueCategories,columns=columnLabels)
    elif targetAxis=='columns' or targetAxis=='cols':
        sumMergeMatrix=pd.DataFrame(index=rowLabels,columns=uniqueCategories)

    # now loop through the unique categories and sum merge the appropriate rows or columns
    for iCategory in uniqueCategories:
        # get the indexes of the records that match the current category
        currentCategoryIndexes=np.where(categoryLabels==iCategory)[0]
        if len(currentCategoryIndexes)==0:
            raise ValueError('There are no records in the categoryKeyFileDF that match the current category: '+iCategory)
        # raise an error if there are no records that match the current category
        # use these indexes to subset recordIDs
        currentCategoryRecordIDs=recordIDs[currentCategoryIndexes]
        # use these indexes to subset the input matrix, keeping in mind the targetAxis
        if targetAxis=='rows':
            currentCategoryMatrix=matrix.loc[currentCategoryRecordIDs,:]
            # sum merge the current category matrix
            currentCategoryMatrix=currentCategoryMatrix.sum(axis=0)
            # add the results to the corresponding location in the sumMergeMatrix
            sumMergeMatrix.loc[iCategory,:]=currentCategoryMatrix
        elif targetAxis=='columns' or targetAxis=='cols':
            currentCategoryMatrix=matrix.loc[:,currentCategoryRecordIDs]
            # sum merge the current category matrix
            currentCategoryMatrix=currentCategoryMatrix.sum(axis=1)
            # add the results to the corresponding location in the sumMergeMatrix
            sumMergeMatrix.loc[:,iCategory]=currentCategoryMatrix
    
    # determine the desired saving behavior, stealing this code from coOccurrenceMatrix
    if savePath is not None:
        # we don't need to run a check here to determine if the rows and indexes are meaningful
        # they *have* to be, given the above algorithm

        # if it's not none, then check it if is blank (''), or a specific format
        if savePath=='':
            # if it's blank, then they haven't provided a desired format, so we have to use a heuristic for this
            # we'll just set an arbitrary value here, to serve as the heuristic limit
            # in this case, what the value represents is the number of rows (or columns) that we would consider the maximum reasonable to store in a csv
            # in essence: if there are sufficiently few values, then it's fine to store the data as an uncompressed csv.
            # for example, a 1000 by 1000 matrix would be 1,000,000 numeric values which would be 8,000,000 bytes, or 8 MB for float 64 (or 4 MB for float 32)
            thresholdCSV=1000
            # also set the string for the default name
            defaultName='categorySumMergeMatrix'
            # if the number of rows or columns is less than the threshold, then save as a csv
            if sumMergeMatrix.shape[0]<thresholdCSV:          
                # save the sumMergeMatrix matrix as a csv
                sumMergeMatrix.to_csv(defaultName+'.csv')
            # if the number of rows or columns is greater than the threshold, then save as an hdf5
            else:
                # save the co-occurrence matrix as an hdf5
                with h5py.File(defaultName+'.hdf5','w') as f:
                    f.create_dataset('dataMatrix',data=sumMergeMatrix.values,compression='gzip')
                    f.create_dataset('rowName',data=sumMergeMatrix.index,compression='gzip')
                    f.create_dataset('colName',data=sumMergeMatrix.columns,compression='gzip')
                # now close the file
                f.close()
        # if it's not blank, then check if it's a csv or an hdf5
        elif savePath.endswith('.csv'):
            # if it's a csv, then save the co-occurrence matrix as a csv essentially the same way as above
            sumMergeMatrix.to_csv(savePath)

        elif savePath.endswith('.hdf5'):
            # if it's an hdf5, then save the co-occurrence matrix as an hdf5 essentially the same way as above
            with h5py.File(defaultName+'.hdf5','w') as f:
                f.create_dataset('dataMatrix',data=sumMergeMatrix.values,compression='gzip')
                f.create_dataset('rowName',data=sumMergeMatrix.index,compression='gzip')
                f.create_dataset('colName',data=sumMergeMatrix.columns,compression='gzip')
                # now close the file
                f.close()
        # if it's not blank, csv, or hdf5, or None then raise an error
        else:
            raise ValueError('The savePath variable must be either blank (''), None, or end with ".csv" or ".hdf5"')

        # return the results
    return sumMergeMatrix      

def cosineDistanceMatrix(inputMatrixDF, axisToCompareWithin='columns',savePath=''):
    """
    This function takes in a matrix and computes the cosine distance metric for the elements of the specified axis.
    The results are returned as a square matrix with the rows and columns corresponding to the elements of the specified axis.
    
    The distance between elements i and j of the axisToCompareWithin is determined by the cosine distance of the vectors formed
    by all of the elements of the opposite axis.  

    Parameters
    ----------
    inputMatrixDF : pandas dataframe
        A matrix of some sort, which contains numeric values.  The column labels and row indexes should correspond to the
        identifiers of the elements of the specified axis.  They will be used to label the rows and columns of the output matrix.
    axisToCompareWithin : string
        Either 'rows' or 'columns', depending on whether you want to compute the cosine distance between the rows or the columns of the input matrix.
    savePath : string
        The path to which the results should be saved.  If None, then the results are not saved.  If '', then the results are saved to the current directory.

    Returns
    -------
    cosineDistanceMatrix : pandas dataframe
        A pandas dataframe with the cosine distance between each pair of elements of the specified axis.  The rows and columns correspond to the elements of the specified axis.
    
    """
    import pandas as pd
    import numpy as np
    import scipy.spatial.distance as ssd
    import os
    import h5py

    # check if the input matrix is a pandas dataframe and has informative row and column labels, which we will define as being strings
    # if it is, then proceed
    # if it isn't then raise an error explaning why a pandas dataframe is necessary (the column / row indexes need to be matched against the category dictionary))
    if not isinstance(inputMatrixDF,pd.DataFrame):
        raise ValueError('A pandas dataframe with informative row and column labels is required in order to compute the cosine distance between the rows or columns of the input matrix.')
    # check if the row and column labels are strings
    if not np.all([isinstance(x,str) for x in inputMatrixDF.index]) or not np.all([isinstance(x,str) for x in inputMatrixDF.columns]):
        raise ValueError('A pandas dataframe with informative row and column labels is required in order to compute the cosine distance between the rows or columns of the input matrix.')
    
    # go ahead and convert the input matrix to a numpy array
    inputMatrix=inputMatrixDF.values

    # parse the case logic for rows or columns
    if axisToCompareWithin=='rows':
        # create a list of tuples, where each tuple contains the indexes of the rows to be compared
        comparisonIndexes=[(i,j) for i in range(inputMatrix.shape[0]) for j in range(inputMatrix.shape[0]) if i<j]
        # initialize a list to store the results
        cosineDistanceResults=[[] for x in range(len(comparisonIndexes))]
        # loop through the comparison indexes and compute the cosine distance between the rows
        for iComparison in range(len(comparisonIndexes)):
            # get the current comparison indexes
            currentComparisonIndexes=comparisonIndexes[iComparison]
            # get the current comparison rows
            currentComparisonRows=inputMatrix[currentComparisonIndexes,:]
            # compute the cosine distance between the current comparison rows
            currentCosineDistance=ssd.cosine(currentComparisonRows[0,:],currentComparisonRows[1,:])
            # store the results
            cosineDistanceResults[iComparison]=currentCosineDistance

        # convert the results to a square matrix
        cosineDistanceMatrix=np.zeros((inputMatrix.shape[0],inputMatrix.shape[0]))
        # loop through the comparison indexes and store the results in the appropriate location in the square matrix
        for iComparison in range(len(comparisonIndexes)):
            # get the current comparison indexes
            currentComparisonIndexes=comparisonIndexes[iComparison]
            # get the current comparison rows
            currentComparisonRows=inputMatrix[currentComparisonIndexes,:]
            # get the current cosine distance
            currentCosineDistance=cosineDistanceResults[iComparison]
            # store the results
            cosineDistanceMatrix[currentComparisonIndexes[0],currentComparisonIndexes[1]]=currentCosineDistance
            cosineDistanceMatrix[currentComparisonIndexes[1],currentComparisonIndexes[0]]=currentCosineDistance
        # set the row and column names
        rowNames=inputMatrixDF.index
        columnNames=inputMatrixDF.index
    elif axisToCompareWithin=='columns':
        # do the same thing as above, but with the columns
        # create a list of tuples, where each tuple contains the indexes of the columns to be compared
        comparisonIndexes=[(i,j) for i in range(inputMatrix.shape[1]) for j in range(inputMatrix.shape[1]) if i<j]
        # initialize a list to store the results
        cosineDistanceResults=[[] for x in range(len(comparisonIndexes))]
        # loop through the comparison indexes and compute the cosine distance between the columns
        for iComparison in range(len(comparisonIndexes)):
            # get the current comparison indexes
            currentComparisonIndexes=comparisonIndexes[iComparison]
            # get the current comparison columns
            currentComparisonColumns=inputMatrix[:,currentComparisonIndexes]
            # compute the cosine distance between the current comparison columns
            currentCosineDistance=ssd.cosine(currentComparisonColumns[:,0],currentComparisonColumns[:,1])
            # store the results
            cosineDistanceResults[iComparison]=currentCosineDistance
        
        # convert the results to a square matrix
        cosineDistanceMatrix=np.zeros((inputMatrix.shape[1],inputMatrix.shape[1]))
        # loop through the comparison indexes and store the results in the appropriate location in the square matrix
        for iComparison in range(len(comparisonIndexes)):
            # get the current comparison indexes
            currentComparisonIndexes=comparisonIndexes[iComparison]
            # get the current comparison columns
            currentComparisonColumns=inputMatrix[:,currentComparisonIndexes]
            # get the current cosine distance
            currentCosineDistance=cosineDistanceResults[iComparison]
            # store the results
            cosineDistanceMatrix[currentComparisonIndexes[0],currentComparisonIndexes[1]]=currentCosineDistance
            cosineDistanceMatrix[currentComparisonIndexes[1],currentComparisonIndexes[0]]=currentCosineDistance
        # set the row and column names
        rowNames=inputMatrixDF.columns
        columnNames=inputMatrixDF.columns

    return cosineDistanceMatrix





def subsetHD5DataByKeyfile(hd5FilePathOrObject,keyFilePathOrObject,saveFilePath=None,saveFileName=None):
    """
    This function uses a keyfile to select a subset of the records in an HD5 file, and then optionally saves that subset to a new HD5 file, if save path information is provided.
    Returns the subset of data.  

    Parameters
    ----------
    hd5FilePathOrObject : string or h5py object
        The path to the HD5 file, or the HD5 file object itself.  The HD5 file is presumed to be of the standard format produced within this toolset,
        which means that the structure has the following data keys:

        - dataMatrix : numpy array
            The data matrix, with rows corresponding to the items and columns corresponding to the attributes.
        - rowName : list of strings
            The names or IDs of the items.
        - colName : list of strings
            The names or IDs of the attributes.

        And the following attribute keys:
        - rowDescription : string
            A description and / or context associated with the row entries.
        - colDescription : string
            A description and / or context associated with the column entries.

    keyFilePathOrObject : string or pandas dataframe
        The path to the keyfile, or the keyfile object itself.  The keyfile is presumed to be a pandas dataframe with two columns.
        The first column contains the relevant IDs or names, and the second column contains a boolean variable indicating whether the
        corresponding entry should be included in the subset.

    NOTE:  In order to determine which axis the keyfile corresponds to, this function will check for a match between the IDs in the keyfile, and the rowNames and colNames in the HD5 file.
    If a match cannot be found, then an error will be raised.

    saveFilePath : string
        The directory path to which the subset of data should be saved.  If None, then the subset of data is not saved.
    saveFileName : string
        The name of the file to which the subset of data should be saved.  If None, then the subset of data is not saved.

    Returns
    -------
    subsetData : pandas dataframe
        The subset of data, with the same structure as the input HD5 file.    
    """
    import pandas as pd
    import h5py
    import numpy as np

    # if the hd5FilePathOrObject is a string, then open the file
    if isinstance(hd5FilePathOrObject,str):
        hd5File=h5py.File(hd5FilePathOrObject,'r')
    # if the hd5FilePathOrObject is an h5py object, then proceed
    elif isinstance(hd5FilePathOrObject,h5py.File):
        hd5File=hd5FilePathOrObject
    # if the hd5FilePathOrObject is neither a string nor an h5py object, then raise an error
    else:
        raise ValueError('The hd5FilePathOrObject must be either a string or an appropriately formatted h5py object')
    
    # if the keyFilePathOrObject is a string, then open the file
    if isinstance(keyFilePathOrObject,str):
        keyFile=pd.read_csv(keyFilePathOrObject,header=None)
    # if the keyFilePathOrObject is a pandas dataframe, then proceed
    elif isinstance(keyFilePathOrObject,pd.DataFrame):
        keyFile=keyFilePathOrObject
    # if the keyFilePathOrObject is neither a string nor a pandas dataframe, then raise an error
    else:
        raise ValueError('The keyFilePathOrObject must be either a string or an appropriately formatted pandas dataframe')
    
    # get the domain of entries covered in the keyfile, this should be the content of the first column
    keyFileDomain=keyFile.iloc[:,0].values
    # get the boolean values indicating whether each entry should be included in the subset, this should be the content of the second column
    keyFileBoolean=keyFile.iloc[:,1].values

    # get the row names from the HD5 file
    rowNames=hd5File['rowName'].value
    # get the column names from the HD5 file
    colNames=hd5File['colName'].value

    # check if the keyfile domain is a subset of the row names
    if np.all(np.in1d(keyFileDomain,rowNames)):
        # if so, then the keyfile corresponds to the rows
        keyFileAxis='rows'
    # check if the keyfile domain is a subset of the column names
    elif np.all(np.in1d(keyFileDomain,colNames)):
        # if so, then the keyfile corresponds to the columns
        keyFileAxis='columns'
    # if the keyfile domain is not a subset of either the row names or the column names, then raise an error
    else:
        raise ValueError('The keyfile domain (i.e. the content of the first column of the keyfile) must be a subset of either the row names or the column names of the input HD5 file')
    
    # in the case that the keyfile corresponds to the rows, then proceed
    if keyFileAxis=='rows':
        # get the indices of the keyfile domain in the row names
        keyFileIndices=np.where(np.in1d(rowNames,keyFileDomain))[0]
        # get the subset of row names
        subsetRowNames=rowNames[keyFileIndices]
        # get the subset of data
        subsetData=hd5File['dataMatrix'][keyFileIndices,:]
        # the colName, colDescription, and rowDescription are the same as the original HD5 file
        subsetColName=hd5File['colName'].value
        subsetColDescription=hd5File['colDescription'].value
        subsetRowDescription=hd5File['rowDescription'].value
    # in the case that the keyfile corresponds to the columns, then proceed
    elif keyFileAxis=='columns':
        # get the indices of the keyfile domain in the column names
        keyFileIndices=np.where(np.in1d(colNames,keyFileDomain))[0]
        # get the subset of column names
        subsetColNames=colNames[keyFileIndices]
        # get the subset of data
        subsetData=hd5File['dataMatrix'][:,keyFileIndices]
        # the rowName, rowDescription, and colDescription are the same as the original HD5 file
        subsetRowName=hd5File['rowName'].value
        subsetRowDescription=hd5File['rowDescription'].value
        subsetColDescription=hd5File['colDescription'].value

    # go ahead and reform the hd5 object that will either be returned or saved
    



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
                elif not nameField=='' or nameField==None:
                    nameField=nameField
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
            raise ValueError('Field ' + str(iField) + ' not found in dictionary ' + str(inputDict) + '. \n Input list = ' + str(fieldList)) 
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
    # a list of fields found in the NIH schema; all caps, because YELLING
    NIHfields=['APPLICATION_ID', 'ACTIVITY', 'ADMINISTERING_IC', 'APPLICATION_TYPE', 'ARRA_FUNDED', 'AWARD_NOTICE_DATE', 'BUDGET_START', 'BUDGET_END', 'CFDA_CODE', 'CORE_PROJECT_NUM', 'ED_INST_TYPE']

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
    # now check if the NIH fields are present
    NIHfieldCount=0
    for NIHfield in NIHfields:
        if NIHfield in allKeys:
            NIHfieldCount+=1

    # now determine which data source is the best match
    # heaven help you if the sequencing of these matters
    if NSFfieldCount>=minFieldThreshold:
        dataSource='NSF'
    elif grantsGovFieldCount>=minFieldThreshold:
        dataSource='grantsGov'
    elif NIHfieldCount>=minFieldThreshold:
        dataSource='NIH'
    else:    
        dataSource=None
    return dataSource


