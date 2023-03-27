import xmltodict
import sys
import os
import pandas as pd
import glob

grantXML_or_path='C:\\Users\\dbullock\\Documents\\code\\gitDir\\USG_grants_crawl\\inputData\\GrantsDBExtract20230113v2.xml'
def grantXML_to_dictionary(grantXML_or_path):
    """
    Convert the XML data structure from https://www.grants.gov/xml-extract.html to a pandas dataframe.

    Accepts either a path indicating a string, or a string corresponding to an XML structure

    Parameters
    ----------
    grantXML_or_path : path str or XML str
        Either a path indicating a string, or a string corresponding to an XML structure.    

    Returns
    -------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov, converted from XML.  Likely includes NAN values for empty entries.

    See Also
    --------
    grantXML_to_dictionary : convert the XML data structure from https://www.grants.gov/xml-extract.html to a pandas dataframe.
    """
    import xmltodict
    import pandas as pd
    import os

    # if a string path is passed in
    if isinstance(grantXML_or_path, str):
    # check if its a filepath
        if os.path.isfile(grantXML_or_path):
            # open it
            with open(grantXML_or_path, 'r') as f:
                #govGrantData_raw = f.read()
                govGrantData_dictionary = xmltodict.parse(f.read())
        else:
            # we assume it's an xml formatted structure string, and simply change the name
            govGrantData_dictionary = xmltodict.parse(grantXML_or_path)
        # convert xml to dictionary            
    # convert to pandas dataframe
    grantsDF=pd.DataFrame.from_records(govGrantData_dictionary['Grants']['OpportunitySynopsisDetail_1_0'], columns=['OpportunityID', 'OpportunityTitle','OpportunityNumber','AgencyCode', 'AgencyName', 'LastUpdatedDate','AwardCeiling', 'AwardFloor', 'EstimatedTotalProgramFunding', 'ExpectedNumberOfAwards', 'Description'])
    # reformat the date
    grantsDF['LastUpdatedDate']=grantsDF['LastUpdatedDate'].apply(lambda x: str(x)[0:2] + '/' + str(x)[2:4] + '/' + str(x)[4:8] )
    # replace dashes with spaces in the text, to match altered keywords
    # I don't know why I have to force specify string, descriptions should already be strings
    grantsDF['Description']=grantsDF['Description'].apply(lambda x: str(x).replace('-',' ') )
    return grantsDF

def reTypeGrantColumns(grantsDF):
    """
    Iterates through columns and retypes the columns in an intentional fashion.

    Parameters
    ----------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov, likely derived from the function grantXML_to_dictionary.

    Returns
    -------
    grantsDF : pandas.DataFrame
        The same dataframe which was input, with the relevant column types (and nan values) changed in place.

    See Also
    --------
    grantXML_to_dictionary : convert the XML data structure from https://www.grants.gov/xml-extract.html to a pandas dataframe.
    """
    import numpy as np
    from warnings import warn

    # get the column names
    columnNames=grantsDF.columns
    # set the replacement types, need int 64 because money gets big
    # string, int, float sqeuencing
    replacementTypes=[np.int64,np.float64,str]
    # set the values that nan will be replaced by
    replacementValues=[np.int64(0),np.float64(0),'']

    #iterate through the columns and get the types
    for iColumns in columnNames:
        # implement try structure way out here, makes it robust, I guess
        try:
            # get a sample from the current column
            currentSample=grantsDF[iColumns].iloc[0:50]
            # TEMPORARILY replace the na values with a string '0'
            currentSample=currentSample.fillna(str('0'))
            # check if it's a string or a null.  Should be an easy case.  Shouldn't fail unless object
            strOrNull=np.all(currentSample.apply(lambda x: isinstance(x,str)))
            # if it's a string or null
            if strOrNull:
                # check if it's convertable to an int or float
                # int check DOES NOT replace period
                intORNull  = np.all(currentSample.apply(lambda x: x.isnumeric()))
                # float check replaces a SINGLE period
                floatORNull= np.all(currentSample.apply(lambda x: x.replace('.','',1).isnumeric()))

                # BEGIN REPLACEMENT PROCESS; no switch cases, so just iterate through options
                # if it's an int and null column, convert it as such; do it in place
                if intORNull:
                    # start by replacing the nans
                    grantsDF[iColumns].fillna(replacementValues[0], inplace=True)
                    # then replace the types 
                    grantsDF=grantsDF.astype({iColumns : replacementTypes[0]}, copy=False)
                # if it's a float
                elif floatORNull:
                    # start by replacing the nans
                    grantsDF[iColumns].fillna(replacementValues[1], inplace=True)
                    # then replace the types 
                    grantsDF=grantsDF.astype({iColumns : replacementTypes[1]}, copy=False)
                # I guess it's just a string (or maybe an object, which will result in an error at some point)
                else:
                    # start by replacing the nans
                    grantsDF[iColumns].fillna(replacementValues[2], inplace=True)
                    # then replace the types 
                    grantsDF=grantsDF.astype({iColumns : replacementTypes[2]}, copy=False)
        # in the event that it fails, throw a warning; probably because there were objects in there somewhere
        except:
            warn('Type conversion for column ' + iColumns + ' failed.')
    print(grantsDF.dtypes)
    return grantsDF

def downloadLatestGrantsXML(savePathDir=None):
    """
    Downloads the latest XML data structure from https://www.grants.gov/xml-extract.html.

    Downloads to local directory if no path value entered for savePath.  Returns the resultant XML structure as well.

    Parameters
    ----------
    savePathDir : str
        A string path corresponding to the *directory* the user would like the grants.gov xml file downloaded.
        Default value is None, resulting in download to current working directory.

    Returns
    -------
    XML_filePath : str
        The path to the resultant (e.g. downloaded and unzipped) data structure.

    See Also
    --------
    grantXML_to_dictionary : convert the XML data structure from https://www.grants.gov/xml-extract.html to a pandas dataframe.
    """
    import os
    import zipfile
    from datetime import datetime
    import requests

    # check and see what the save path has been set to
    if savePathDir == None:
        savePathDir = ''
    # check if the path exists
    elif os.path.isdir(savePathDir):
        # do nothing, the path is set
        pass
    # if the directory doesn't exist, *don't* make the directory, instead raise an error
    else:
        raise Exception ('Input save path\n' + savePathDir + '\ndoes not exist. Create first.')

    # file pathing taken care of, begin prep for download
    # grants.gov extract url
    grantsExtractURL='https://www.grants.gov/extract/'
    # generate all of the file name parts
    dateString= datetime.today().strftime('%Y%m%d')
    fileStem='GrantsDBExtract'
    fileEnd='v2.zip'
    fullFileName= fileStem + dateString + fileEnd
    # set queryURL
    queryURL= grantsExtractURL + fullFileName

    # use recomended requests method
    # https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url
    def download_url(url, save_path, chunk_size=128):
        r = requests.get(url, stream=True)
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        print(str(os.path.getsize(save_path)) + ' bytes file downloaded from\n' + url)
        print('Saved to ' + savePathDir)

    # establish save path
    zipSavePath=os.path.join(savePathDir,fullFileName)
    # download
    download_url(queryURL, zipSavePath, chunk_size=128)
    # unzip in place
    with zipfile.ZipFile(zipSavePath, 'r') as zip_ref:
        zip_ref.extractall(savePathDir)
    print('Downloaded file unZipped, deleting original file.')
    # should result in a file with exactly the same name, ecept XML instead of .zip
    os.remove(zipSavePath)
    print ('XML file located at\n' + zipSavePath.replace('zip','xml'))
    return zipSavePath.replace('zip','xml')

def repairFunding_GovGrantsDF(grantsDF):
    """
    Repairs the content of the grantsDF dataframe in accordance with established heuristics.

    NOTE: this function CHANGES the values / content of the grantsDF from the information contained on grants.gov, including
    but not limited to adding data columns, replacing null/empty values, and/or inferring missing values.

    Parameters
    ----------
    grantsDF : pandas.DataFrame
            A dataframe containing grants data from grants.gov  

    Returns
    -------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov, converted from XML.  Likely includes NAN values for empty entries.

    See Also
    --------
    grantXML_to_dictionary : convert the XML data structure from https://www.grants.gov/xml-extract.html to a pandas dataframe.
    """
    from warnings import warn
    import numpy as np
    import copy
    warn('NOTE: this function CHANGES the values / content of the grantsDF from the information contained on grants.gov, including but not limited to adding data columns, replacing null/empty values, and/or inferring missing values.')

    # fairly complicated heuristics here

    #arbitrary assumption about floor value of grant
    floorThresh=3000

    # here's a presumed sequencing for these columns
    # AwardCeiling	AwardFloor	EstimatedTotalProgramFunding	ExpectedNumberOfAwards
    # EstimatedTotalProgramFunding > AwardCeiling > (AwardFloor == 0 OR AwardFloor > ExpectedNumberOfAwards
    # So imagine an algorithm we apply to these four values for each row
    # first sort(grantsDF[['AwardCeiling','AwardFloor','EstimatedTotalProgramFunding','ExpectedNumberOfAwards'] )
    # e.g.          [87753000 , 4000, 0 , 0]= sort([0	0	87753000	4000])
    # if the number of zeros is 3 and the 

    quantColumns=['AwardCeiling','AwardFloor','EstimatedTotalProgramFunding','ExpectedNumberOfAwards']
    correctedCount=0
    for iIndex,iRows in grantsDF.iterrows():

        # get the grant quantificaiton values for this row 
        grantQuantificationValues=[iRows[iColumns] for iColumns in quantColumns]        
        # get the sorted order of the vector
        #sortedOrder=np.argsort(grantQuantificationValues)
        grantQuantificationValues_sorted=sorted(grantQuantificationValues)
        # create a vector for the sorting to occur in
        grantQuantificationValues_RE_sorted=copy.deepcopy(grantQuantificationValues)

        #pctThresh=1
        # if the award floor is less than 1% of the total funding, set it to zero
        #if (grantQuantificationValues_RE_sorted[1]*(100/pctThresh))<grantQuantificationValues_RE_sorted[2]:
        #    print(grantQuantificationValues_RE_sorted)
        
        #    grantQuantificationValues_RE_sorted[1]=0
            
        
        # by definition, your grant value total ought to be the largest number
        if not grantQuantificationValues_sorted[3] == grantQuantificationValues[2]:
            # if it's not, move the value in that spot to where the largest number is
            grantQuantificationValues_RE_sorted[list(grantQuantificationValues).index(grantQuantificationValues_sorted[3])]=grantQuantificationValues[2]
            # and switch the spots
            grantQuantificationValues_RE_sorted[2]=grantQuantificationValues_sorted[3]        

        
        
        # if the largest value is above the threshold, we can do something
        if grantQuantificationValues_RE_sorted[2] > floorThresh:
            # now we need a count of how many zeros there are
            unique, counts = np.unique(grantQuantificationValues_RE_sorted, return_counts=True)
            countsDict=dict(zip(unique, counts))
            try:
                zeroCount=countsDict[0]
            except:
                zeroCount=0
            # now we get into our case based logic
            # if there are 3 zeros, and the grant value is a above the threshold, we can assume that there's 1 grant, 
            # and the ceiling is the total value
            if zeroCount == 3:
                grantQuantificationValues_RE_sorted=[grantQuantificationValues_RE_sorted[2],0,grantQuantificationValues_RE_sorted[2],1 ]
            
            # if you have two zeros, one can't be in the estimated number
            elif zeroCount == 2:
            # if you have a ceiling value of 0 and a floor value that isn't, I have to assume those are flipped
                if grantQuantificationValues_RE_sorted[0]==0 and not grantQuantificationValues_RE_sorted[1]==0:
                    grantQuantificationValues_RE_sorted[0]=grantQuantificationValues_RE_sorted[1]
                    grantQuantificationValues_RE_sorted[1]=0
                # if the grant count is zero, but the ceiling value isn't
                if grantQuantificationValues_RE_sorted[3]==0 and not grantQuantificationValues_RE_sorted[0]==0:
                # then use that info to estimate the number of awards
                    grantQuantificationValues_RE_sorted[3]=np.floor(np.divide(grantQuantificationValues_RE_sorted[2],grantQuantificationValues_RE_sorted[0])).astype(int)

                # if you have a count but not a ceiling value, do the inverse computation of the first
                elif not grantQuantificationValues_RE_sorted[3]==0 and grantQuantificationValues_RE_sorted[0]==0:
                    grantQuantificationValues_RE_sorted[0]=np.floor(np.divide(grantQuantificationValues_RE_sorted[2],grantQuantificationValues_RE_sorted[3])).astype(int)
                # if you've asserted that the max grant val is 
                else:
                    pass
                    # shouldn't be anything else, we've handled all the cases I think for two zeros.
            
            elif zeroCount == 1:
                # if the zero isn't in the value floor column, we have a problem.
                if not grantQuantificationValues_RE_sorted[1]==0:
                    # if it's in the ceiling, I'm again going to assume you flipped them
                    if grantQuantificationValues_RE_sorted[0]==0 and not grantQuantificationValues_RE_sorted[1]==0:
                        grantQuantificationValues_RE_sorted[0]=grantQuantificationValues_RE_sorted[1]
                        grantQuantificationValues_RE_sorted[1]=0
                      # if the grant count is zero, but the ceiling value isn't
                    elif grantQuantificationValues_RE_sorted[3]==0 and not grantQuantificationValues_RE_sorted[0]==0:
                    # then use that info to estimate the number of awards
                        grantQuantificationValues_RE_sorted[3]=np.floor(np.divide(grantQuantificationValues_RE_sorted[2],grantQuantificationValues_RE_sorted[0])).astype(int)
                    else:
                        # cases seem mostly taken care of
                        pass
                    
            else:
                pass
                #print(grantQuantificationValues_RE_sorted)
        if not np.all(np.equal(grantQuantificationValues,grantQuantificationValues_RE_sorted)):
            correctedCount=correctedCount+1
            grantsDF[quantColumns].iloc[iIndex]=grantQuantificationValues_RE_sorted
    
    print(str(correctedCount) + ' grant funding value records repaired')
            

    return grantsDF
                    
def inferNames_GovGrantsDF(grantsDF):
    """
    Infers agency names for the grantsDF dataframe in accordance with established heuristics.

    NOTE: this function CHANGES the values / content of the grantsDF from the information contained on grants.gov, including
    but not limited to adding data columns, replacing null/empty values, and/or inferring missing values.

    Parameters
    ----------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov   

    Returns
    -------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov, with an additional column

    See Also
    --------
    reTypeGrantColumns : Iterates through columns and retypes the columns in an intentional fashion.
    repairFunding_GovGrantsDF : Repairs the content of the grantsDF dataframe in accordance with established heuristics.
    """
    import numpy
    import copy
    import pandas as pd
    # silence!
    pd.options.mode.chained_assignment = None
    # get the column names
    allColumnNameslist=list(grantsDF.columns)
    # add a column for agency sub code
    try: 
        grantsDF.insert(allColumnNameslist.index('AgencyCode')+1,'AgencySubCode', '')
    except:
        pass
    #quantColumns=['AgencyName','AgencyCode']
    # set a fill value for null name values
    fillValue='Other'

    correctedCount=0
    for iIndex,iRows in grantsDF.iterrows():
        currAgencyName=iRows['AgencyName']
        currAngencyCode=iRows['AgencyCode']
        currAngencySubCode=''
        inputInfo=[currAgencyName,currAngencyCode,currAngencySubCode]
        # try and split the subcode out now
        try:
            currAngencySubCode=currAngencyCode.split('-',1)[1]
            currAngencyCode=currAngencyCode.split('-',1)[0]
        except:
            currAngencySubCode=''
        # go ahead and throw it in
        grantsDF['AgencySubCode'].iloc[iIndex]=currAngencySubCode

        #create a vector to hold all of these
        
        

        # if the agency code is either nan or empty we'll try and fix it
        if currAngencyCode == '':
            
            if not currAgencyName == '':
                # use the capital letters to infer, replace commas with dashes
                # start wit the full agency name
                currAngencyCode=copy.deepcopy(currAgencyName)
                # commas to dashes
                currAngencyCode=currAngencyCode.replace(',','-')
                # drop all non capital, non dash characters
                currAngencyCode=''.join([char for char in currAngencyCode if char.isupper() or char == '-'])
                try:
                    currAngencySubCode=currAngencyCode.split('-',1)[1]
                except:
                    currAngencySubCode=''
                currAngencyCode=currAngencyCode.split('-',1)[0]
            
            else:
                # if there's no agency name available, just set both to 'Other'
                currAngencyCode=fillValue
                currAngencySubCode=''
                currAgencyName=fillValue

            #correctedCount =correctedCount + 1

        # if the name is null set it to the fill value as well
        if currAgencyName == '':
            currAgencyName=fillValue
            #correctedCount =correctedCount + 1
            try:
                currAngencySubCode=currAngencyCode.split('-',1)[1]
                currAngencyCode=currAngencyCode.split('-',1)[0]
            except:
                currAngencySubCode=''
        
        outputInfo=[currAgencyName,currAngencyCode,currAngencySubCode]
        #if there is new information to add, update the record
        if not inputInfo==outputInfo:
            grantsDF['AgencyName'].iloc[iIndex] =  outputInfo[0]
            grantsDF['AgencyCode'].iloc[iIndex] =  outputInfo[1]
            grantsDF['AgencySubCode'].iloc[iIndex] =  outputInfo[2]
            correctedCount =correctedCount + 1
            # dont bother updating if not relevant.
        #print(iIndex)    
    print(str(correctedCount) + ' grant agency name or code value records altered')
    return grantsDF

def prepareGrantsDF(grantsDF, repair=True):
    """
    Resets column types, infers agency names, and repairs grant values

    NOTE: this function CHANGES the values / content of the grantsDF from the information contained on grants.gov, including
    but not limited to adding data columns, replacing null/empty values, and/or inferring missing values.

    Parameters
    ----------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov   

    Returns
    -------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov, that has been prepared for analysis

    See Also
    --------
    reTypeGrantColumns : Iterates through columns and retypes the columns in an intentional fashion.
    repairFunding_GovGrantsDF : Repairs the content of the grantsDF dataframe in accordance with established heuristics.
    inferNames_GovGrantsDF : Infers agency names for the grantsDF dataframe in accordance with established heuristics.
    """

    # first do the retyping
    grantsDF=reTypeGrantColumns(grantsDF)
    # then redo the names
    grantsDF=inferNames_GovGrantsDF(grantsDF)
    #then do the repair if requested
    if repair:
        grantsDF=repairFunding_GovGrantsDF(grantsDF)
    
    return grantsDF

def grants_by_Agencies(grantsDF):
    """
    Divides up the grant IDs ('OpportunityID') from the input grantsDF by top level agency.

    Returns a dictionary wherein the keys are agency names and the values are lists of 'OpportunityID's.

    Parameters
    ----------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov   

    Returns
    -------
    grantFindsOut : dictionary
        A a dictionary wherein the keys are agency names and the values are lists of 'OpportunityID's.

    See Also
    --------
    searchGrantsDF_for_keywords : Divides up the grant IDs ('OpportunityID')--for grants whose description includes
    an item from the input keywordList variable--into groups associated by keyword.
      """

    import numpy as np
    # create a dictionary which could be saved as a json, so that you don't have to do this each time
    agencyGrants={}

    grantAgenciesUnique = np.unique(list(grantsDF['AgencyCode'].values), return_counts=False)

    for iAgencies in grantAgenciesUnique:
        # find the 'OpportunityID's of the grants whose agency code matches the current iAgency
        currentGrantIDs=grantsDF['OpportunityID'].loc[grantsDF['AgencyCode'].eq(iAgencies)].values
        # set it in the output dictionary
        agencyGrants[iAgencies]=currentGrantIDs
    return agencyGrants

def searchGrantsDF_for_keywords(grantsDF,keywordList):
    """
    Divides up the grant IDs ('OpportunityID')--for grants whose description includes
    an item from the input keywordList variable--into groups associated by keyword.

    Returns a dictionary wherein the keys are keywords and the values are lists of 'OpportunityID's
    wherein the the keyword was found in the associated description.

    Parameters
    ----------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov   
    keywordList : list of strings
        A list of strings corresponding to the keywords one is interested in assessing the occurrences of. 

    Returns
    -------
    grantFindsOut : dictionary
        A a dictionary wherein the keys are keywords and the values are lists of 'OpportunityID's
    wherein the the keyword was found in the associated description.

    See Also
    --------
    grants_by_Agencies : Divides up the grant IDs ('OpportunityID') from the input grantsDF by top level agency.
    """
    import re

    # create a dictionary which could be saved as a json, so that you don't have to do this each time
    grantFindsOut={}
    grantsDF['Description']=grantsDF['Description'].apply(lambda x: x.lower().replace('-',''))

    for iKeywords in keywordList:
    # create a blank list to store the IDs of the grants with the keyword in the description
        grantsFound=[]
        # create the compiled search for this keyword
        compiledSearch=re.compile('\\b'+iKeywords.lower()+'\\b')
        for iRows,iListing in grantsDF.iterrows():
            # maybe it doesn't have a description field
            try:
                # case insensitive find for the keyword
                # get rid of dashes to be insensitive to variations in hyphenation behaviors
                if bool(compiledSearch.search(iListing['Description'])):
                    #append the ID if found
                    grantsFound.append(iListing['OpportunityID'])
            except:
                # do nothing, if there's no description field, then the word can't be found
                pass
                
        # store the found entries in the output dictionary.  Use the keyword as the key (with spaces replaced with underscores),
        # and the value being the list of grant IDs
        # maybe don't do this for now
        #grantFindsOut[iKeywords.replace(' ','_')]=grantsFound
        grantFindsOut[iKeywords]=grantsFound
    return grantFindsOut

#def evalGrantCoOccurrence(dictionariesList,formatOut='dictionary'):
#    """
#    DOESN'T WORK
#    code-davinci-002 prompt:
#    This function takes a list of dictionaries as input.  Each dictionary is formatted such that the keys are strings, and the values are lists.  The output is also a dictionary.  It's keys are tuples, wherein each element of the tuple corresponds to a key value of the corresponding (in sequence order) input dictionaries.  For example, for an input featuring three dictionaries, the i_0,j_0,k_0 dictionary entry would correspond to the list values which were associated for all of the following: dictionary_i keyitem_0, dictionary_j keyitem_0, dictionary_k keyitem_0.  Tuples which do not return any shared list elements are assocaited with a blank list in the output dictionary structure.
#    
#    Parameters
#    ----------
#    dictionariesList : list of dictionaries
#        A list such that each member dictionary is formatted such that the keys are strings, and the values are lists.
#    formatOut : string
#        The desired format of the output. Either 'dictionary' or 'dataframe'.  'dataframe' likely will not work for list sizes larger than 2.  
#
#    Returns
#    -------
#    grantFindsOut : dictionary or pandas.DataFrame
#        If formatOut='dictionary' : a dictionary such that its keys are tuples, wherein each element of the tuple corresponds to a key value of the corresponding (in sequence order) input dictionaries.
#        If formatOut='dataframe' : a pandas.DataFrame such that the row indexes correspond to the keys of the first input, and the column indexes correspond to the keys of the second input.  The cell values are lists of co occurring list elements.
#    """
#    #initialize the output dictionary
#    out_dict = {}
#    #iterate through the input dictionary list
#    for i in range(len(dictionariesList)):
#        #iterate through the keys of the current dictionary
#        for key in dictionariesList[i].keys():
#            #iterate through the values of the current dictionary
#            for value in dictionariesList[i][key]:
#                #initialize a list to store the values of the other dictionaries
#                other_values = []
#                #iterate through the other dictionaries
#                for j in range(len(dictionariesList)):
#                    #skip the current dictionary
#                    if j != i:
#                        #iterate through the keys of the other dictionaries
#                        for other_key in dictionariesList[j].keys():
#                            #iterate through the values of the other dictionaries
#                            for other_value in dictionariesList[j][other_key]:
#                                #if the current value is equal to the other value, append the other value to the other values list
#                                if value == other_value:
#                                    other_values.append(other_value)
#                #if the other values list is not empty, add the tuple of the current value and the other values list to the output dictionary
#                if other_values != []:
#                    out_dict[(value,)] = other_values
#    #return the output dictionary
#    return out_dict

def evalGrantCoOccurrence(dictionariesList,formatOut='dictionary'):
    """
    
    code-davinci-002 prompt:
    This function takes a list of dictionaries as input.  Each dictionary is formatted such that the keys are strings, and the values are lists.  The output is also a dictionary.  It's keys are tuples, wherein each element of the tuple corresponds to a key value of the corresponding (in sequence order) input dictionaries.  For example, for an input featuring three dictionaries, the i_0,j_0,k_0 dictionary entry would correspond to the list values which were associated for all of the following: dictionary_i keyitem_0, dictionary_j keyitem_0, dictionary_k keyitem_0.  Tuples which do not return any shared list elements are assocaited with a blank list in the output dictionary structure.
    Davinci code didn't work, doing manually    

    Parameters    ----------
    dictionariesList : list of dictionaries
        A list such that each member dictionary is formatted such that the keys are strings, and the values are lists.
    formatOut : string
        The desired format of the output. Either 'dictionary' or 'dataframe'.  'dataframe' likely will not work for list sizes larger than 2.  

    Returns
    -------
    grantFindsOut : dictionary or pandas.DataFrame
        If formatOut='dictionary' : a dictionary such that its keys are tuples, wherein each element of the tuple corresponds to a key value of the corresponding (in sequence order) input dictionaries.
        If formatOut='dataframe' : a pandas.DataFrame such that the row indexes correspond to the keys of the first input, and the column indexes correspond to the keys of the second input.  The cell values are lists of co occurring list elements.
    """
    import itertools
    import pandas as pd

    # create output structure
    grantFindsOut={}
    # get the list of keys for all inputs
    keysLists=[list(iDictionaries.keys()) for iDictionaries in dictionariesList]
    # find the unique(?) combinations of these
    allKeyCombinations=list(itertools.product(*keysLists))
    #iterate across them
    for iKeyCombos in  allKeyCombinations:
        # create a holder for the key-value results for each dictioanry
        allPairResults=[]
        # iterate across the key lists / input dictionaries
        for iDictionaryIndex,iKeys in enumerate(iKeyCombos):
            try:
                # try and get the current key value
                allPairResults.append(dictionariesList[iDictionaryIndex][iKeys])
            except:
                # otherwise put in an empty, probably not possible           
                allPairResults.append([])

        # covert these lists to sets    
        asSets=[set(iPairResult) for iPairResult in allPairResults]
        # find the intersection of the sets, redundancy with self input doesn't matter
        allIntersection=list(asSets[0].intersection(*asSets))
        # place it in the output strucutre
        grantFindsOut[iKeyCombos]=allIntersection

    if len(dictionariesList)==2 and formatOut.lower()=='dataframe':
        outDF=pd.DataFrame(index=keysLists[0],columns=keysLists[1])
        for iRecords in grantFindsOut:
            outDF.loc[iRecords[0],iRecords[1]]=grantFindsOut[iRecords]

        return outDF
    else: 
        return grantFindsOut
        

def detectLocalGrantData(localPath='',forceDownload=True):
    """
    Detects and loads local grant data.  Optionally download it if not found locally


    Parameters    ----------
    localPath : string
        Path to where  the grant data is, or where the user would like it to be if it is not already there.
    forceDownload : bool
        Flag to determine what happens if data isn't found.  Will download if 'True'.
    
    Returns
    -------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov

    See Also
    --------
    grantXML_to_dictionary : convert the XML data structure from https://www.grants.gov/xml-extract.html to a pandas dataframe.
  
    """
    import os
    import pandas as pd
    import glob

    # do a quick reset to the current working directory if relevant
    if  localPath=='':
        localPath=os.getcwd()


    if os.path.isfile(localPath):
        
        if os.path.splitext(localPath)[-1].lower()=='.csv':
            # remember, we are using the bar instead of comma, description field has commas, as do some names
            grantsDF=pd.read_csv('allGrantsData.csv',sep='|')
            print('CSV loaded')
        elif os.path.splitext(localPath)[-1].lower()=='.xml':
            grantsDF=grantXML_to_dictionary(grantXML_or_path)
        else:
            Exception('Input file format not recognized')

    # if the input is a directory, check to see what's there        
    elif os.path.isdir(localPath):
        # check for the file
        try:
            if os.path.isfile(glob.glob(os.path.join(localPath,'GrantsDBExtract*.xml'))[-1]):
                # if it exists get the path
                pathToXML=glob.glob(os.path.join(localPath,'GrantsDBExtract*.xml'))[-1]
                print(pathToXML)
                # and load it
                grantsDF=grantXML_to_dictionary(pathToXML)
        except:
            print ('No local grant data xml file found')
            # if the forceDownload option is set
            if forceDownload:
                print('Downloading grant data from grants.gov')
                xmlDownloadPath=downloadLatestGrantsXML(savePathDir=localPath)
                grantsDF=grantXML_to_dictionary(xmlDownloadPath)
    
    return grantsDF

def load_details(opp_id):
    """
    Uses the grants.gov rest API to get the information for the specified grant.

    Parameters    ----------
    opp_id: str or int
        The 'OpportunityID' identifier for the current target grant.


    
    Returns
    -------
    outJson: json
        A json structure with the rest API output.  See https://www.grants.gov/web/grants/s2s/grantor/schemas/grants-funding-synopsis.html     

    See Also
    --------
   
    """
    outJson=requests.post("https://www.grants.gov/grantsws/rest/opportunity/details", data={'oppId': opp_id}).json()

    return outJson

def downloadGrantsGov_grantDocs(OpportunityID,localPath=''):
    """
    Downloads the associated grants.gov documents for a given grant, as specified by it's OpportunityID


    Parameters    ----------
    OpportunityID: str or int
        The 'OpportunityID' identifier for the current target grant.
    localPath : string
        Path to where the output data should be downloaded to.  Will then create a directory in this directory,
        with the title being the OpportunityID

    
    Returns
    -------
    None

    See Also
    --------
   
    """
    import os
    import json
    import requests

    # set the base urls
    base_url='http://www.grants.gov/grantsws/rest/opportunity/details?oppId='
    #base_url= 'http://www.grants.gov/grantsws/OppDetails?oppId='
    #document_url = 'http://www.grants.gov/grantsws/rest/oppdetails/att/download/'
    docDownloadLink='https://www.grants.gov/grantsws/rest/opportunity/att/download/'

    # do a quick reset to the current working directory if relevant
    if  localPath=='':
        localPath=os.getcwd()
    
    currentSaveDir=os.path.join(localPath,str(OpportunityID))
    # make the save path dir
    if not os.path.exists(currentSaveDir):
        os.mkdir(currentSaveDir)
    detailsOut=load_details(OpportunityID)
    try:
            fileName=os.path.join(currentSaveDir,'description.txt')
            pdf = open(fileName, 'wb')
            pdf.write( bytes(detailsOut['synopsis']['synopsisDesc'],'utf-8'))
            pdf.close()
            for iFolders in detailsOut['synopsisAttachmentFolders']:
                associatedDocRecords=iFolders
                for iAttachments in associatedDocRecords['synopsisAttachments']:
                    fileExtension=iAttachments['fileName'].split('.')[1]
                    if fileExtension.lower() in ['pdf','doc','docx','txt','md']:

                        

                        response = requests.get(docDownloadLink+str(iAttachments['id']))
                        fileName=os.path.join(currentSaveDir,str(iAttachments['id'])+'.'+fileExtension)
                        # Write content in pdf file
                        pdf = open(fileName, 'wb')
                        pdf.write(response.content)
                        pdf.close()
    except:
        print('Failed to download documents for '+ str(OpportunityID))

def tupleDictionaries_to_NDarray(tupleDictionary,operation=len):
    """
    This function coverts a dictionary with permuted tuples as the keys (e.g. keys = [list 1, list 2, list 3, etc.])
    and converts it to a count ND array (e.g. len(tupleDictionary[iKey]) for iKeys in list(tupleDictionary.keys()))
    
    Think of this as pandas.DataFrame.applymap(), but for dictionaries.


    Parameters    ----------
    tupleDictionary: dictionary
        A dictionary with permuted tuples as the keys (e.g. keys = [list 1, list 2, list 3, etc.])
    
    Returns
    -------
    ndArrayHolder : numpy array
        A N-dimensional count array

    See Also
    --------
   
    """
    import numpy as np
    # convert the keys to an array
    keysArray=np.asarray(list(tupleDictionary.keys()))
    # create a list to hold the unique labels
    uniqueDimLabels=[]
    # iterate through the sets of key elements
    for iDims in range(keysArray.shape[1]):
        # append the unique key values for each dimension to the holder
        uniqueDimLabels.append(list(np.unique(keysArray[:,iDims])))
    # create a array holder for this 
    ndArrayHolder=np.zeros([len(iDems) for iDems in  uniqueDimLabels],dtype=np.int32)
    # iterate through the keys
    for iKeys in list(tupleDictionary.keys()):
        # get the current coords associated with the given key
        indexCoords=[ uniqueDimLabels[iCoords].index(iKeys[iCoords]) for iCoords in range(len(iKeys))]
        # do the relevant operation and place the output it in the relevant space
        ndArrayHolder[tuple(indexCoords)]=operation(tupleDictionary[iKeys])
    return ndArrayHolder

def convertIDdictionary_to_values(grantsDF,opportunityIDdictionary,columnSelect):
    """
    This function coverts each value element in a dictionary in which the values are all grant opportunityID values, to the corresponding 
    value from the relevant column in the grantsDF dataframe.

    Parameters    ----------
    grantsDF : pandas.DataFrame
        A dataframe containing grants data from grants.gov  
    opportunityIDdictionary: dictionary
        A dictionary in which the values are all grant opportunityID values.
    columnSelect: string
        A string corresponding to a column in the input grantsDF.
    
    Returns
    -------
    convertedDictionary : dictionary
        A dictionary in which the each value element in a dictionary is no longer an opportunityID value,
    but rather, the corresponding value from the relevant column in the grantsDF dataframe.

    See Also
    --------
   
    """
    # iterate across the dictionary keys
    for iKeys in opportunityIDdictionary:
        # get the values for this key
        currentValues=opportunityIDdictionary[iKeys]
        # create a holder for the converted values
        convertedValues=[]
        # iterate across these values, which are presumably opportunityIDs
        for iCurrentValues in currentValues:
            # get the current grantsDF row
            currentRow=grantsDF.loc[grantsDF['opportunityID'].eq(iCurrentValues)]
            # find the desired convert value
            currentConvertValue=currentRow[columnSelect]
            # append it to the list
            convertedValues.append(convertedValues)
        # once all of the converted values have been obtained, set the current-key dictionary value to the replacemnt values
        opportunityIDdictionary[iKeys]=convertedValues
    
    return opportunityIDdictionary

#import json
#import requests


#grantsFindJSON='C:\\Users\\dbullock\\Documents\\code\\gitDir\\USG_grants_crawl\\grantFindsOut.json'
# Opening JSON file
#f = open(grantsFindJSON)
#keywordsData=json.load(f )
#f.close()

#idList=[]
#for iKeywords in list(keywordsData.keys()):
#    idList.extend(keywordsData[iKeywords])
#import numpy as np
#uniqueIDs,counts=np.unique(idList, return_counts=True)

#atLeastTwiceIDs=uniqueIDs[counts>=2]
#storeOutputDirectory='C:\\Users\\dbullock\\Documents\\code\\dataSources\\grantData'
