# now that we have handled downloading, we need to process and curate the data
def processDownloadedData(dataLocation,sourceOrg,saveDir,singleMulti='multi'):
    """
    This function processes downloaded data from any of the supported sources and saves down the proceessed resultant
    in a "processed" subdirectory of the source data directory.  The singleMulti flag determines whether the data are
    stored as a single file or as multiple files.

    Inputs:
        dataLocation: string
            A string corresponding to the path to the downloaded data.
        sourceOrg: string
            A string corresponding to the source organization of the data.  Currently supported are 'NSF' and 'Grants.gov'.
        saveDir: string
            A string corresponding to the path to the directory where the processed data should be saved.
        singleMulti: string
            A string corresponding to whether the data should be stored as a single file or as multiple files.  Currently
            supported are 'single' and 'multi'.
    
    Outputs: None    
    """
    import pandas as pd
    from glob import glob
    import xmltodict
    import os

    # establish a vector with the currently accepted sources
    # currently no support for NIH
    acceptedSources=['NSF','grantsGov','NIH']

    # check if the source is in the accepted sources
    if sourceOrg not in acceptedSources:
        # if not, raise an error
        raise ValueError('The source organization '+sourceOrg+' is not currently supported.  Supported sources are '+str(acceptedSources))
    # otherwise proceed in a casewise fashion
    else:
        # if the source is NSF
        if sourceOrg=='NSF':
            # TODO: is this even used here?
            # load the directorate remap file
            directorateRemap=pd.read_csv('../NSF_directorate_remap.csv')
            # find the remapped directorate names
            validDirectorateNames=directorateRemap['fixedName'].unique()

            # given that the NSF data should have been unzipped at this point, they should now be in a single directory
            # filled with xml files
            # use glob to find all of the xml files
            xmlFiles=glob(dataLocation+os.sep+'*.xml')
            # create a "processed" subdirectory if it doesn't exist
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
            # iterate across the xml files
            for iFiles in xmlFiles:
                # use attemptXMLrepair to attempt to repair the xml file if necessary
                attemptXMLrepair(iFiles)
                # load the xml file into a dictionary, which presumably works now
                with open(iFiles) as fd:
                    doc = xmltodict.parse(fd.read())
                # use applyFixesToRecord_NSF
                # it was originally designed to work on a json files, but should work fine on a dictionary
                # it will return a dictionary with the fixed record
                fixedRecord=applyFixesToRecord_NSF(doc)
                # save it down to the processed directory as an xml file with the same name
                # get the file name
                fileName=iFiles.split(os.sep)[-1]
                # get the save path
                savePath=saveDir+os.sep+fileName
                # save it down
                with open(savePath, 'w') as fd:
                    fd.write(xmltodict.unparse(fixedRecord, pretty=True))
                # close the file
                fd.close()
            # NOTE: thus the NSF data have been processed and saved down to the "processed" subdirectory of the dataLocation
            print('NSF data have been processed and saved down to ' + saveDir)
        # if the source is NIH
        elif sourceOrg=='NIH':
            # should be taken care of here
            # beyond merging the data, there is currently (as of 2023-07-07) no additional processing needed
            mergeNIHDataToXML(dataLocation,saveDir)

        # if the source is grants.gov
        elif sourceOrg=='grantsGov':
                        
            # determine if the dataLocation is a directory or a specific file
            if os.path.isdir(dataLocation):
                # establish the processed data directory
                processedDataDir=saveDir
                # use glob to find an xml file with "GrantsDBExtract" in the name
                grantsGovFilename=glob(dataLocation+os.sep+'*GrantsDBExtract*.xml')[0]
                # if this file exists, load it with pandas
                if os.path.isfile(grantsGovFilename):
                    # Load it and parse it with xmltodict
                    with open(dataLocation) as fd:
                        doc = xmltodict.parse(fd.read())
                    fd.close()
                # extract the list of grants
                grants=doc['Grants']['OpportunitySynopsisDetail_1_0']
                # convert the grants to a pandas dataframe
                currentData=pd.DataFrame(grants)

            elif os.path.isfile(dataLocation):
                # establish the processed data directory
                
                processedDataDir=saveDir
                # Load it and parse it with xmltodict
                with open(dataLocation) as fd:
                    doc = xmltodict.parse(fd.read())
                # close the file   
                fd.close()
                # extract the list of grants
                grants=doc['Grants']['OpportunitySynopsisDetail_1_0']
                # convert the grants to a pandas dataframe
                currentData=pd.DataFrame(grants)
 
            else:
                # if not, raise an error
                raise ValueError('The grants.gov data file '+dataLocation+' does not exist.')
            # process the grants.gov data using repairFunding_GovGrantsDF
            processedCurrentData=prepareGrantsDF(currentData)
            # save the processed data in the desired format, either as a single file, or per entry, as xml, using the "OpportunityID" as the xml file name
            # check to see if a "processed" subdirectory exists
            if not os.path.exists(processedDataDir):
                os.makedirs(processedDataDir)
                
            # if the singleMulti flag is set to single
            if singleMulti=='single':
                # save the data as a single file
                # NOTE: this is being saved down as a csv, maybe this isn't what we want to do in the long run
                processedCurrentData.to_csv(processedDataDir+os.sep+'processedGrantsGovData.csv',index=False)
            # if the singleMulti flag is set to multi
            elif singleMulti=='multi':
                # iterate across the rows
                for iRows in range(processedCurrentData.shape[0]):
                    # get the current row
                    currentRow=processedCurrentData.iloc[[iRows],:]
                    # get the current row's OpportunityID
                    currentOpportunityID=currentRow['OpportunityID'].values[0].astype(str)
                    # establish the save path
                    currSavePath=os.path.join(processedDataDir,currentOpportunityID+'.xml')
                    # attempt to save the current row as an xml file
                    try:
                        # pandas to_xml doesn't seem to work
                        # currentRow.to_xml(currSavePath)
                        # so first we convert to a dictionary
                        currentRowDict=currentRow.to_dict(orient='records')
                        # then we save it down using xmltodict
                        with open(currSavePath, 'w') as fd:
                            # NOTE: kind of arbitrarily having to implement 'rootTag' as the root of the xml structure, a convention borrowed from the NSF format
                            fd.write(xmltodict.unparse({'rootTag': currentRowDict}, pretty=True))
                        # close the file
                        fd.close()
                    # if it fails throw an error
                    except:
                        raise ValueError('The grants.gov data could not be saved down to '+currSavePath + '\n' + 'The current row content is: ' + str(currentRow) )
        print('grants.gov data have been processed and saved down to ' + processedDataDir)
    return

def processNIHData(dataLocation,singleMulti='single'):
    """
    This function processes NIH data, which come in year-wise csv files, and separate the abstract information from the project information.
    This process will undo that, by going through the csv files, year wise, opening both the abstract and project CSVs and creating individual records
    for each individual project.
    Inputs:
        dataLocation: string
            The path to the NIH data.
        singleMulti: string
            A flag indicating whether the data should be saved down as a single file, or as multiple files.

    """


def mergeNIHDataToXML(dataSourceDir,xmlSaveDir):
    """
    This function merges NIH data, by award ID, into individual xml files.  For each
    data (grant) record, the data must be pulled from an abstract and project file,
    from the corresponding year.  The abstract files are named 
    "RePORTER_PRJABS_C_FYxxxx.csv" where xxxx is a year, while the project files are
    named "RePORTER_PRJ_C_FYxxxx.csv".  The award ID is the first column in both files.
    Inputs:
        dataSourceDir: string
            The directory where the NIH data are stored.
        xmlSaveDir: string
            The directory where the xml files should be saved.
    Outputs:
        None (saves down xml files)
    """
    import os
    import pandas as pd
    from glob import glob
    import xmltodict
    from bs4 import BeautifulSoup
    from warnings import warn

    # first make sure the save directory exists, and if not make it
    if not os.path.exists(xmlSaveDir):
        os.makedirs(xmlSaveDir)

    # get the list of years
    # NOTE: this assumes that the years are the only 4 digit numbers in the directory

    # get the list of files in the directory, that have "RePORTER" in the name
    fileList=glob(dataSourceDir+os.sep+'*RePORTER*')
    # now split these in to the abstract and project files
    abstractFileList=[x for x in fileList if 'PRJABS' in x]
    projectFileList=[x for x in fileList if 'PRJ' in x]
    # note though that 'PRJ' is a substring of 'PRJABS', so we need to remove the abstract files from the project file list
    projectFileList=[x for x in projectFileList if x not in abstractFileList]

    # now ensure they are sorted in the same order so that the years match up
    abstractFileList.sort()
    projectFileList.sort()
    # now get the years from the abstract file list
    years=[int(x.split('FY')[1].split('.')[0]) for x in abstractFileList]
    # now iterate across the years
    for iYear in range(len(years)):
        # get the current abstract file
        currentAbstractFile=abstractFileList[iYear]
        # get the current project file
        currentProjectFile=projectFileList[iYear]
        # now load up each of these files
        currentAbstractData=pd.read_csv(currentAbstractFile,encoding = "utf-8")
        currentProjectData=pd.read_csv(currentProjectFile, encoding = "utf-8")
        # get the award IDs from the abstract data
        abstractAwardIDs=currentAbstractData['APPLICATION_ID'].values
        # we don't need the award IDs from the project data, they're the same, so now we just loop over the IDs
        for iIDs in range(len(abstractAwardIDs)):
            # get the current award ID
            currentAwardID=abstractAwardIDs[iIDs]
            # get the current abstract data
            currentSingleAbstractData=currentAbstractData[currentAbstractData['APPLICATION_ID']==currentAwardID]
            # from this get the abstract text
            currentAbstractText=currentSingleAbstractData['ABSTRACT_TEXT'].values[0]
            # get the current project data
            currentSingleProjectData=currentProjectData[currentProjectData['APPLICATION_ID']==currentAwardID]
            # here we need to implement some robustness, and check to see if any rows have actually been returned
            # if not, then we need to throw a warning and skip this award ID
            if currentSingleProjectData.shape[0]==0:
                warn('No project data were found for award ID ' + str(currentAwardID) + ' from year ' + str(years[iYear]) + '.\nSkipping this award ID.')
                # we should also create an error log file, to keep track of these
                # create the error log file if it doesn't exist
                # we'll store it as a csv, where the first column is the award ID, and the second column is the error / warning message
                if not os.path.exists(xmlSaveDir+os.sep+'errorLog.csv'):
                    with open(xmlSaveDir+os.sep+'errorLog.csv','w') as fd:
                        fd.write('awardID,errorLog\n')
                    fd.close()
                # now append the current award ID and error message to the error log
                with open(xmlSaveDir+os.sep+'errorLog.csv','a') as fd:
                    fd.write(str(currentAwardID) + ',' + 'No project data were found for award ID' + str(currentAwardID) + ' from year ' + str(years[iYear])+'\n')
            else:
                # otherwise, we can proceed
            
                # now we need to convert the currentProjectData to a dictionary
                currentProjectDataDict=currentSingleProjectData.to_dict(orient='records')
                # add the abstract text to the dictionary as a new key, all caps is fine, as that is what is also in the project spreadsheet
                currentProjectDataDict[0]['ABSTRACT_TEXT']=currentAbstractText


                # now save this down as an xml file
                # first make the save path
                # note that currentAwardID is currently an integer, so we need to convert it to a string
                currentSavePath=os.path.join(xmlSaveDir,str(currentAwardID)+'.xml')
                # now save it down

                with open(currentSavePath, 'w') as fd:
                    # NOTE: kind of arbitrarily having to implement 'rootTag' as the root of the xml structure, a convention borrowed from the NSF format
                    fd.write(xmltodict.unparse({'rootTag': currentProjectDataDict}, pretty=True))
                # close the file
                fd.close()
        # if it fails throw an warning
    return

def attemptXMLrepair(xmlPath,errorLogPath=None):
    """
    This function loads a putative xml file, and if it is not a valid xml file, attempts to repair it.
    Inputs:
        xmlPath: string
            The path to the putative xml file.
        errorLogPath: string
            The path to the error log file.
    Outputs:
        None (saves down the repaired xml file if it is successful)
    """
    import xmltodict
    import os
    from bs4 import BeautifulSoup

    # get the directory that the xml file is in
    xmlDirectory=os.path.dirname(xmlPath)
    # if no errorLogPath is passed in, set it to the xmlDirectory
    if errorLogPath is None:
        errorLogPath=xmlDirectory+os.sep+'errorLog.txt'
    # check if the errorLogPath exists
    if not os.path.isfile(errorLogPath):
        # if it doesn't exist, create it
        open(errorLogPath,'w').close()
    

    # check if the input file exists
    if os.path.isfile(xmlPath):
        # if it exists, attempt to load it as a dictionary
        currXml=open(xmlPath).read()
        # determine if it is a valid XML file
        try:
            currentDict=xmltodict.parse(currXml)
        except:
            try:
                # throw a warning indicating that the file is not valid
                print('Warning: '+xmlPath+' is not a valid XML file.')
                print('Attempting to repair the file.')
                # if it is not a valid XML file, use BeautifulSoup to repair it
                currXml = BeautifulSoup(currXml, 'xml')
                currentDict=xmltodict.parse(currXml.prettify())
                # save the repaired xml file
                with open(xmlPath, 'w') as outfile:
                    outfile.write(currXml.prettify())
                    # close the file
                    outfile.close()
            except:
                # if it is still not a valid XML file, throw an error
                print('Error: '+xmlPath+' is not a valid XML file.')
                print('Skipping this file.')
                # create an error log file in this directory if it doesn't exist
                errorLogPath=os.path.join(xmlDirectory,'xml2json_errorLog.txt')
                if not os.path.exists(errorLogPath):
                    with open(errorLogPath, 'w') as outfile:
                        outfile.write('Error: '+xmlPath+' is not a valid XML file.')
                #   and append the error to the error log file
                else:
                    with open(errorLogPath, 'a') as outfile:
                        outfile.write('Error: '+xmlPath+' is not a valid XML file.')
    else: 
    # if it's not a file, return an error
        print('Error: '+xmlPath+' is not a valid XML file.')
    return




def applyFixesToRecord_NSF(inputRecord,errorLogPath=None):
    """
    This function applies the established fixes to the NSF record.
    Inputs:
        inputRecord: dictionary
            A dictionary containing the JSON data.
    Outputs:
        inputRecord: dictionary
            A dictionary containing the JSON data.      
    
    """
    from bs4 import BeautifulSoup
    import os
    import pandas as pd

    # if no errorLogPath is passed in, set it to the presumptive data directory, which is
    # "inputData" in the root of the repository
    if errorLogPath is None:
        errorLogPath=os.path.join('inputData','NSF-fixes_errorLog.txt')

    # find location of directorate remap 
    directorateRemap=pd.read_csv('../NSF_directorate_remap.csv')
    # find the remapped directorate names
    validDirectorateNames=directorateRemap['fixedName'].unique()

    # first, we need to convert the html entities to unicode
    try: 
        if inputRecord['rootTag']['Award']['AbstractNarration'] is not None:
            soup=BeautifulSoup(inputRecord['rootTag']['Award']['AbstractNarration'],'html.parser')
            inputRecord['rootTag']['Award']['AbstractNarration']=soup.get_text().replace('<br/>','\n')
    except: 
        # try and create an informative error log message
        try:
        # open the file for appending
                with open(errorLogPath, 'a') as outfile:
                    outfile.write('Error locating AbstractNarration field for '+inputRecord['rootTag']['Award']['AwardID']+'\r')
        #print('Error locating AbstractNarration field for '+inputRecord['rootTag']['Award']['AwardID'])
        except:
            pass
    # next implement the directorate remapping 
    try:
        if inputRecord['rootTag']['Award']['Organization']['Directorate']['LongName'] not in validDirectorateNames:
            # get the current invalid directorate name
            currentInvalidName=inputRecord['rootTag']['Award']['Organization']['Directorate']['LongName']
            # find its index in the directorate remap file
            currentInvalidNameIndex=directorateRemap.loc[directorateRemap['foundName']==currentInvalidName].index[0]
            # remap the directorate name
            inputRecord['rootTag']['Award']['Organization']['Directorate']['LongName']=directorateRemap.loc[currentInvalidNameIndex,'fixedName']
    # if the directorate field is empty, check the division field
    except:
        try:
            # if the longNamefield is empty, check the division field
            if inputRecord['rootTag']['Award']['Organization']['Division']['LongName'] not in validDirectorateNames:
                # get the current invalid directorate name
                currentInvalidName=inputRecord['rootTag']['Award']['Organization']['Division']['LongName']
                # find its index in the directorate remap file
                currentInvalidNameIndex=directorateRemap.loc[directorateRemap['foundName']==currentInvalidName].index[0]
                # remap the directorate name
                inputRecord['rootTag']['Award']['Organization']['Directorate']['LongName']=directorateRemap.loc[currentInvalidNameIndex,'fixedName']
        except:
            try:
                # if this still fails, check if the field is empty, and then convert it to a "None" string
                if inputRecord['rootTag']['Award']['Organization']['Division']['LongName'] not in validDirectorateNames:
                    # get the current invalid directorate name
                    currentInvalidName=inputRecord['rootTag']['Award']['Organization']['Division']['LongName']
                    if isempty(currentInvalidName):
                        currentInvalidName='None'
                        # remap the directorate name
                        inputRecord['rootTag']['Award']['Organization']['Directorate']['LongName']=currentInvalidName
                    else:
                        with open(errorLogPath, 'a') as outfile:
                            outfile.write('Directorate remapping failed for '+inputRecord['rootTag']['Award']['AwardID']+'\r')
                            outfile.write(currentInvalidName + ' not found in directorate remap file\r')
            except:
                with open(errorLogPath, 'a') as outfile:
                    outfile.write('Directorate remapping failed for '+inputRecord['rootTag']['Award']['AwardID']+'\r')
                    try:
                        outfile.write(str(inputRecord['rootTag']['Award']['Organization']) + ' cause of error\r')
                    except:
                        pass

    # TODO: implement future record fixes here
    return inputRecord


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
                    # didn't seem to work, so now we try column specific
                    # grantsDF[iColumns]=grantsDF[iColumns].astype(replacementTypes[2])
                    # that didn't work either
                    # so lets see what copilot does
                    # here we convert the dtype of the column from object to string
                    # grantsDF[iColumns]=grantsDF[iColumns].astype('|S')
                    # none of this seems to work or matter, so just stick with the first one
                    
        # in the event that it fails, throw a warning; probably because there were objects in there somewhere
        except:
            warn('Type conversion for column ' + iColumns + ' failed.')
    print(grantsDF.dtypes)
    return grantsDF

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
        grantQuantificationValues=list(map(int,[iRows[iColumns] for iColumns in quantColumns]))        
        # get the sorted order of the vector
        #sortedOrder=np.argsort(grantQuantificationValues)
        grantQuantificationValues_sorted=sorted(grantQuantificationValues)
        # create a vector for the sorting to occur in
        grantQuantificationValues_RE_sorted=copy.deepcopy(grantQuantificationValues)

        # temporary error check to ensure all contents are numbers
        # for iValues in grantQuantificationValues:
        #    if not isinstance(iValues,(int,float)):
        #        print('Error: non-numeric value in grantQuantificationValues')
        #        print(grantQuantificationValues)
        #        print(iRows)
        #        return
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
    import numpy as np
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
            #print(outputInfo)
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

def isempty(inputContent):
    '''
    This function determines whether the input is null, empty, '', zero, or NaN, or equivalent.
    Is this ugly?  Yes it is.
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