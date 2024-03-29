import xmltodict
import sys
import os
import pandas as pd
import glob

def detectLocalDataSource(location, sourceOrg, singleMulti='single'):
    """
    Detects the presence of local data from the source organization.
    checks the location directory for the relevant content.  If singleMulti
    is set to 'single' it checks for a single, omnibus file, if set to
    'multi' it checks for multiple files in the designated directory.

    Parameters
    ----------
    location : str
        The directory which is to be checked for the desired data.
        Checks for the existence of the directory and throws an error if not found.
    sourceOrg : str
        One of the following, indicating the source organization:
            - 'grantsGov'
            - 'NIH'
            - 'NSF'
    singleMulti : str, optional
        Indicates whether the data should be a single file or multiple files.  The default is 'single'.
        - 'single' : checks for a single, omnibus file
        - 'multi' : checks for multiple files in the designated directory.
    
    Returns
    -------
    localData : string or boolean
        If the data is found, returns the path to the data.  If not found, returns False.

    NOTE: the data comes from the respective sources in different formats:
        - grants.gov : single omnibus XML file
        - NIH : ?
        - NSF : year-wise tar or zip files containing per-award XML files
    """
    import os
    import glob

    # check if the location exists
    if os.path.isdir(location):
        # if it does not exist, throw an error
        print('The location ' + location + ' does not exist.  Please check the location and try again.')
        return False
    # if it does exist, check for the data
    else:
        # TODO: This is where to add additional data sources
        # handle each case respectively
        # arbitrary convention: double spacing separating each case,
        # separating single and multi

        if sourceOrg=='grantsGov':
            # check for the single file
            if singleMulti=='single':
                # check for the single file
                # use the file stem to check for the file
                grantsGovFileStem='GrantsDBExtract'
                # check for the file, check for either xml or json, case insensitive
                # first check for xml
                grantsGovFile=glob.glob(location + grantsGovFileStem + '*.[xX][mM][lL]')
                # then check for json, and cat the results
                grantsGovFile=grantsGovFile+glob.glob(location + grantsGovFileStem + '*.[jJ][sS][oO][nN]')
                # if the file is found, return the path
                if len(grantsGovFile)>0:
                    return grantsGovFile[0]
                # if the file is not found, return False
                else:
                    return False
                
            # check for the multiple files
            elif singleMulti=='multi':
                # haven't implemented the split function yet, but
                # we'll assume that we will use the same convention as 
                # the NSF data, with separate xml files for each grant
                # named by the grants.gov ID number
                # check for the multiple files, just assume they are numbered and end with .xml
                grantsGovFiles=glob.glob(location + '*.xml')
                # check if the returned file names are numbers and thus valid
                # do this by iterating through the list of returns and checking if they are string numbers
                # if they are, return the list of files
                # if they are not, return False
                # get a list of the file names that meet this criteria
                grantsGovFiles=[x for x in grantsGovFiles if x.split(os.sep())[-1].split('.')[0].isdigit()]
                # if the list is not empty, return the list
                if len(grantsGovFiles)>0:
                    return grantsGovFiles
                # if the list is empty, return False
                else:
                    return False
        

        elif sourceOrg=='NIH':
            #TODO: figure out what the NIH data looks like
            # for now, throw a not implemented error
            raise NotImplementedError('The NIH data has not yet been implemented.  Please check back later.')
            return False
        

        elif sourceOrg=='NSF':
            # check for the single file
            if singleMulti=='single':
                # check for the single file
                # use the file stem to check for the file
                #TODO: confirm that this is the correct stem for the omnibus file
                nsfFileStem='NSF_Awards'
                # check for the file
                # check for both xml and json, case insensitive
                # first check for xml
                nsfFile=glob.glob(location + nsfFileStem + '*.[xX][mM][lL]')
                # then check for json, and cat the results
                nsfFile=nsfFile+glob.glob(location + nsfFileStem + '*.[jJ][sS][oO][nN]')
                # if the file is found, return the path
                if len(nsfFile)>0:
                    return nsfFile[0]
                # if the file is not found, return False
                else:
                    return False

            # check for the multiple files
            elif singleMulti=='multi':
                # check for the multiple files, just assume they are numbered and end with .xml
                nsfFiles=glob.glob(location + '*.xml')
                # check if the returned file names are numbers and thus valid
                # do this by iterating through the list of returns and checking if they are string numbers
                # if they are, return the list of files
                # if they are not, return False
                # get a list of the file names that meet this criteria
                nsfFiles=[x for x in nsfFiles if x.split(os.sep())[-1].split('.')[0].isdigit()]
                # if the list is not empty, return the list
                if len(nsfFiles)>0:
                    return nsfFiles
                # if the list is empty, return False
                else:
                    return False
        else:
            # if the source organization is not recognized, throw an error
            print('The source organization ' + sourceOrg + ' is not recognized.  Please check the source organization and try again.')
            return False
        
def getDataFromRemoteSource(destination,sourceOrg):
    """
    This function downloads the data from the remote source and saves it to the designated destination.

    Parameters
    ----------
    destination : string
        The path to the directory where the data will be saved.
    sourceOrg : string
        The organization from which the data will be downloaded, from one of the following
        - 'grantsGov'
        - 'NIH'
        - 'NSF'
    
    Returns
    -------
    result : str or boolean
        The path to the downloaded data, or False if the download failed.
    """
    import os
    import requests
    import shutil
    import zipfile
    import tarfile


    # check if the destination exists
    if os.path.isdir(destination):
        # if it does not, create a directory for the sourceOrg data
        os.mkdir(destination + os.sep() + sourceOrg)
        # set this as the new destination
        destination=destination + os.sep() + sourceOrg
    # if it does exist, check for the data


    else:
        # NOTE: this is where to add additional data sources
        # if it does exist, check for the data
        # for the grants.gov data, check for the single xml
        if sourceOrg=='grantsGov':
            # check for the single file
            # use the file stem to check for the file
            grantsGovFileStem='GrantsDBExtract'
            # first check for xml
            grantsGovFile=glob.glob(destination + grantsGovFileStem + '*.[xX][mM][lL]')
            # then check for json, and cat the results
            # if the file is found, return True, no need to go and re-download
            if len(grantsGovFile)>0:
                return grantsGovFile[0]
            # if the file is not found, continue
            else:
                pass

        # for the NIH data, check for the single xml
        # TODO: confirm that this is the case
        elif sourceOrg=='NIH':
            # check for the single file
            # use the file stem to check for the file
            nihFileStem='NIH_Awards'
            # first check for xml
            nihFile=glob.glob(destination + nihFileStem + '*.[xX][mM][lL]')
            # then check for json, and cat the results
            # if the file is found, return True, no need to go and re-download
            if len(nihFile)>0:
                return nihFile[0]
            # if the file is not found, continue
            else:
                pass

        # for the NSF data, look for a series of zip / tar files with four digit years as their names
        elif sourceOrg=='NSF':
            # check for zip and tar files
            # first check for zip
            nsfFiles=glob.glob(destination + '*.zip')
            # then check for tar, cat the results
            nsfFiles=nsfFiles+glob.glob(destination + '*.tar')
            # if the file are found, return True, no need to go and re-download
            if len(nsfFiles)>0:
                return nsfFiles
            # if the file is not found, continue
            else:
                pass

        # if the source organization is not recognized, throw an error
        else:
            print('The source organization ' + sourceOrg + ' is not recognized.  Please check the source organization and try again.')
            return False
        

        # NOTE: this is where to add additional data sources
        # if the data is not found, download it, depending on the source organization
        # for the grants.gov data, download and unzip the single xml
        if sourceOrg=='grantsGov':
                # use the downloadGrantsGovGrantsData
                # this returns the path to the downloaded data
                try: 
                    grantsGovFile=downloadGrantsGovGrantsData(destination)
                except:
                    print('The download of the grants.gov data failed.  Please check the source and try again.')
                    return False
                # if the download is successful, check that the grantsGovFile exists
                if os.path.isfile(grantsGovFile):
                    return grantsGovFile
                # if the download is not successful, return False
                else:
                    return False
        
        # for the NIH data, download and unzip the single xml
        elif sourceOrg=='NIH':
            #TODO confirm that this is the case
            # for now raise a not implemented error
            raise NotImplementedError('The NIH data source is not yet implemented.  Please check back later.')
        
        elif sourceOrg=='NSF':
            # create this list of files to be downloaded
            nsfDownloadURLS=genNSFdownloadURLs()
            # download the files with downloadNSFgrantsData
            nsfFiles=downloadNSFgrantsData(nsfDownloadURLS,destination)
            # if the download is successful, check that the first file exists, there are too many to check all
            if os.path.isfile(nsfFiles[0]):
                return nsfFiles
            # if the download is not successful, return False
            else:
                return False

# NOTE: here we have the functions for downloading the data from the remote sources

def downloadGrantsGovGrantsData(savePathDir=None):
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
    print ('XML file located at\n' + zipSavePath.replace('zip','xml'))
    return zipSavePath.replace('zip','xml')

        
def genNSFdownloadURLs():
    """
    This funtion generates the paths to the NSF grant data files that are stored at www.nsf.gov/awardsearch/.
    Note that it will generate files up to the current year.

    Inputs: None
    Outputs: 
        downloadURLs: list
            A list of strings corresponding to the download URLs for the NSF grant data files.
    """
    import datetime
    # get the current year
    currentYear=datetime.datetime.now().year
    # create a holder for the download URLs
    downloadURLs=[]
    # append the historical data URL
    downloadURLs.append('https://www.nsf.gov/awardsearch/download?DownloadFileName=Historical&All=true')
    #as of 04/04/2022, the earliest year of data is 1959
    firstYear=1959
    # iterate across the years
    for iYears in range(firstYear,currentYear+1):
        # create the download URL
        currentURL='https://www.nsf.gov/awardsearch/download?DownloadFileName='+str(iYears)+'&All=true'
        # append it to the holder
        downloadURLs.append(currentURL)
    return downloadURLs

def downloadNSFgrantsData(downloadURLs,saveDirectory=None):
    """
    This function downloads the NSF grant data files that are stored at www.nsf.gov/awardsearch/.
    Note that it will download files up to the current year.

    Inputs: 
        downloadURLs: list
            A list of strings corresponding to the download URLs for the NSF grant data files.
        saveDirectory: string
            A string corresponding to the directory in which the downloaded files should be saved.
    Outputs: None
    """
    if saveDirectory is None:
        saveDirectory=os.getcwd()+os.sep+'NSF_grant_data'
        # create the save directory if it doesn't exist
        if not os.path.exists(saveDirectory):
            os.makedirs(saveDirectory)

    import requests
    import os
    import zipfile
    import tarfile
    outPaths=[]
    # iterate across the download URLs
    for iURLs in downloadURLs:
        # get the file name
        fileName=iURLs.split('=')[-2].split('&')[0]+'.zip'
        # create the save path
        savePath=os.path.join(saveDirectory,fileName)
        # download the file
        response = requests.get(iURLs)
        # Write content in pdf file
        currFile = open(savePath, 'wb')
        currFile.write(response.content)
        currFile.close()
        # check if it is a zip or a tar file
        if fileName.endswith('.zip'):
            # unzip the file
            with zipfile.ZipFile(savePath, 'r') as zip_ref:
                zip_ref.extractall(saveDirectory)
        elif fileName.endswith('.tar'):
            # untar the file
            with tarfile.open(savePath, "r:") as tar_ref:
                tar_ref.extractall(saveDirectory)
        # append the save path to the holder
        outPaths.append(savePath)
        # print an indicator of how many files have been downloaded
        print('Downloaded '+str(len(outPaths))+' of '+str(len(downloadURLs))+' files')
    return

# now that we have handled downloading, we need to process and curate the data
def processDownloadedData(dataLocation,sourceOrg,singleMulti='multi'):
    """
    This function processes downloaded data from any of the supported sources and saves down the proceessed resultant
    in a "processed" subdirectory of the source data directory.  The singleMulti flag determines whether the data are
    stored as a single file or as multiple files.

    Inputs:
        dataLocation: string
            A string corresponding to the path to the downloaded data.
        sourceOrg: string
            A string corresponding to the source organization of the data.  Currently supported are 'NSF' and 'Grants.gov'.
        singleMulti: string
            A string corresponding to whether the data should be stored as a single file or as multiple files.  Currently
            supported are 'single' and 'multi'.
    
    Outputs: None    
    """
    import pandas as pd
    from glob import glob
    import xmltodict

    # establish a vector with the currently accepted sources
    # currently no support for NIH
    acceptedSources=['NSF','grantsGov']

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
            if not os.path.exists(dataLocation+os.sep+'processed'):
                os.makedirs(dataLocation+os.sep+'processed')
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
                savePath=dataLocation+os.sep+'processed'+os.sep+fileName
                # save it down
                with open(savePath, 'w') as fd:
                    fd.write(xmltodict.unparse(fixedRecord, pretty=True))
                # close the file
                fd.close()
            # NOTE: thus the NSF data have been processed and saved down to the "processed" subdirectory of the dataLocation
            print('NSF data have been processed and saved down to ' + dataLocation+os.sep+'processed')
            
        # if the source is grants.gov
        elif sourceOrg=='grantsGov':
                        
            # determine if the dataLocation is a directory or a specific file
            if os.path.isdir(dataLocation):
                # use glob to find an xml file with "GrantsDBExtract" in the name
                grantsGovFilename=glob(dataLocation+os.sep+'*GrantsDBExtract*.xml')[0]
                # if this file exists, load it with pandas
                if os.path.isfile(grantsGovFilename):
                    # load the presumed xml file from the dataLocation directory, which already should have been downloaded
                    # use pandas to read the xml file
                    currentData=pd.read_xml(grantsGovFilename)
            elif os.path.isfile(dataLocation):
                # if this file exists, load it with pandas
                if os.path.isfile(dataLocation):
                    # load the presumed xml file from the dataLocation directory, which already should have been downloaded
                    # use pandas to read the xml file
                    currentData=pd.read_xml(dataLocation)
                else:
                    # if not, raise an error
                    raise ValueError('The grants.gov data file '+dataLocation+' does not exist.')
            else:
                # if not, raise an error
                raise ValueError('The grants.gov data file '+dataLocation+' does not exist.')
            # process the grants.gov data using repairFunding_GovGrantsDF
            processedCurrentData=repairFunding_GovGrantsDF(currentData,singleMulti=singleMulti)
            # save the processed data in the desired format, either as a single file, or per entry, as xml, using the "OpportunityID" as the xml file name
            # check to see if a "processed" subdirectory exists
            if not os.path.exists(dataLocation+os.sep+'processed'):
                os.makedirs(dataLocation+os.sep+'processed')
                
            # if the singleMulti flag is set to single
            if singleMulti=='single':
                # save the data as a single file
                # NOTE: this is being saved down as a csv, maybe this isn't what we want to do in the long run
                processedCurrentData.to_csv(dataLocation+os.sep+'processedGrantsGovData.csv',index=False)
            # if the singleMulti flag is set to multi
            elif singleMulti=='multi':
                # iterate across the rows
                for iRows in range(processedCurrentData.shape[0]):
                    # get the current row
                    currentRow=processedCurrentData.iloc[iRows,:]
                    # get the current row's OpportunityID
                    currentOpportunityID=currentRow['OpportunityID']
                    # save the current row as an xml file
                    currentRow.to_xml(dataLocation+os.sep+'processed'+os.sep+currentOpportunityID+'.xml')
        print('grants.gov data have been processed and saved down to ' + dataLocation+os.sep+'processed')
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
        
                



# grantXML_or_path='C:\\Users\\dbullock\\Documents\\code\\gitDir\\USG_grants_crawl\\inputData\\GrantsDBExtract20230113v2.xml'
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
    grantsDF['Description']=grantsDF['Description'].apply(lambda x: x.lower().replace('-',' '))

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
        A a dictionary wherein the keys are keywords and the values are lists of items
    wherein the the keyword was found in the associated description.

    See Also
    --------
    grants_by_Agencies : Divides up the grant IDs ('OpportunityID') from the input grantsDF by top level agency.
    """
    import pandas as pd
    import re
    # if inputLists is a series, then convert it to a list
    if type(inputLists)==pd.core.series.Series:
        inputLists=inputLists.values.tolist()


    # create a dictionary which could be saved as a json, so that you don't have to do this each time
    grantFindsOut={}
    #grantsDF['Description']=grantsDF['Description'].apply(lambda x: x.lower().replace('-',''))

    for iKeywords in keywordList:
    # create a blank list to store the IDs of the grants with the keyword in the description
        grantsFound=[]
        # create the compiled search for this keyword
        compiledSearch=re.compile('\\b'+iKeywords.lower()+'\\b')
        for iRows,iListing in enumerate(inputLists):
            # maybe it doesn't have a description field
            try:
                # case insensitive find for the keyword
                # get rid of dashes to be insensitive to variations in hyphenation behaviors
                if bool(compiledSearch.search(iListing.lower())):
                    #append the ID if found
                    grantsFound.append(iListing)
            except:
                # do nothing, if there's no description field, then the word can't be found
                pass
                
        # store the found entries in the output dictionary.  Use the keyword as the key (with spaces replaced with underscores),
        # and the value being the list of grant IDs
        # maybe don't do this for now
        #grantFindsOut[iKeywords.replace(' ','_')]=grantsFound
        grantFindsOut[iKeywords]=grantsFound
    return grantFindsOut

# open the grants json file as a dictionary
#grantsJsonPath='/media/dan/HD4/coding/gitDir/USG_grants_crawl/inputData/NSF_grant_data/NSF_grants.json'
#keywordTable='/media/dan/HD4/coding/gitDir/USG_grants_crawl/OSterms_LeeChung2022.csv'
#import json
#with open(grantsJsonPath) as f:
#    grantsDict=json.load(f)
# load the keywords table
#import pandas as pd
#keywordsDF=pd.read_csv(keywordTable)
#keywordList=keywordsDF['terms']
#inputLists=[iAward['rootTag']['Award']['AbstractNarration'] for iAward in grantsDict]

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
                # apply the regex search to the file and place it in the appropriate tuple dictionary entry
                outputDict[iStringPhrase][iFile]=applyRegexToXMLFile(os.path.join(directoryPath,iFile),iStringPhrase,fieldsSelect,caseSensitive=caseSensitive)

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
    # run with dask if possible
    # not working due to dask.bag.map() not being able to handle the lemmatizer argument ?
    ##try:
    #    import dask
    #    import dask.bag as db
    #    outputTexts=db.from_sequence(inputTexts).map(lambda x: prepareTextForNLP(x,stopwordsList=stopwordsList,lemmatizer=lemmatizer)).compute()   
    # run without dask if not possible
    # except:
    outputTexts=[]
    for iText in inputTexts:
        outputTexts.append(prepareTextForNLP(iText,stopwordsList=stopwordsList,lemmatizer=lemmatizer))
    return outputTexts

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

# ok, now we might be interested in grant data from the nsf, lets go and get that

def genNSFdownloadURLs():
    """
    This funtion generates the paths to the NSF grant data files that are stored at www.nsf.gov/awardsearch/.
    Note that it will generate files up to the current year.

    Inputs: None
    Outputs: 
        downloadURLs: list
            A list of strings corresponding to the download URLs for the NSF grant data files.
    """
    import datetime
    # get the current year
    currentYear=datetime.datetime.now().year
    # create a holder for the download URLs
    downloadURLs=[]
    # append the historical data URL
    downloadURLs.append('https://www.nsf.gov/awardsearch/download?DownloadFileName=Historical&All=true')
    #as of 04/04/2022, the earliest year of data is 1959
    firstYear=1959
    # iterate across the years
    for iYears in range(firstYear,currentYear+1):
        # create the download URL
        currentURL='https://www.nsf.gov/awardsearch/download?DownloadFileName='+str(iYears)+'&All=true'
        # append it to the holder
        downloadURLs.append(currentURL)
    return downloadURLs

def downloadNSFgrantsData(downloadURLs,saveDirectory=None):
    """
    This function downloads the NSF grant data files that are stored at www.nsf.gov/awardsearch/.
    Note that it will download files up to the current year.

    Inputs: 
        downloadURLs: list
            A list of strings corresponding to the download URLs for the NSF grant data files.
        saveDirectory: string
            A string corresponding to the directory in which the downloaded files should be saved.
    Outputs: None
    """
    if saveDirectory is None:
        saveDirectory=os.getcwd()+os.sep+'NSF_grant_data'
        # create the save directory if it doesn't exist
        if not os.path.exists(saveDirectory):
            os.makedirs(saveDirectory)

    import requests
    import os
    import zipfile
    import tarfile
    outPaths=[]
    # iterate across the download URLs
    for iURLs in downloadURLs:
        # get the file name
        fileName=iURLs.split('=')[-2].split('&')[0]+'.zip'
        # create the save path
        savePath=os.path.join(saveDirectory,fileName)
        # download the file
        response = requests.get(iURLs)
        # Write content in pdf file
        currFile = open(savePath, 'wb')
        currFile.write(response.content)
        currFile.close()
        # check if it is a zip or a tar file
        if fileName.endswith('.zip'):
            # unzip the file
            with zipfile.ZipFile(savePath, 'r') as zip_ref:
                zip_ref.extractall(saveDirectory)
        elif fileName.endswith('.tar'):
            # untar the file
            with tarfile.open(savePath, "r:") as tar_ref:
                tar_ref.extractall(saveDirectory)
        # append the save path to the holder
        outPaths.append(savePath)
        # print an indicator of how many files have been downloaded
        print('Downloaded '+str(len(outPaths))+' of '+str(len(downloadURLs))+' files')
    # remove the zip files
    for iPaths in outPaths:
        os.remove(iPaths)
    return

def produceJSONfromXMLs(xmlDirectory,savePath=None):
    '''
    This function converts the NSF XML files in the input directory to a single omnibus JSON file.
    
    '''
    # we use BeautifulSoup to repair XML files if they are not valid 
    from bs4 import BeautifulSoup
    import glob
    import xmltodict
    import json
    import xml
    import pandas as pd
    # generate the save path if it is not provided
    if savePath is None:
        savePath=os.path.join(xmlDirectory,'NSF_grants.json')
    # get the list of XML files
    xmlFiles=glob.glob(xmlDirectory+os.sep+'*.xml')
    # create a holder for the JSON data
    jsonData=[]
    # load the directorate remap file
    directorateRemap=pd.read_csv('../NSF_directorate_remap.csv')
    # get the unique valid directorate names
    validDirectorateNames=directorateRemap['fixedName'].unique()

    # iterate across the XML files
    for iFiles in xmlFiles:
        # open the XML file
        currXml=open(iFiles).read()
        # determine if it is a valid XML file
        try:
            currentJSON=xmltodict.parse(currXml)
        except:
            try:
                # throw a warning indicating that the file is not valid
                print('Warning: '+iFiles+' is not a valid XML file.')
                print('Attempting to repair the file.')
                # if it is not a valid XML file, use BeautifulSoup to repair it
                currXml = BeautifulSoup(currXml, 'xml')
                currentJSON=xmltodict.parse(currXml.prettify())
            except:
                # if it is still not a valid XML file, throw an error
                print('Error: '+iFiles+' is not a valid XML file.')
                print('Skipping this file.')
                # create an error log file in this directory if it doesn't exist
                errorLogPath=os.path.join(xmlDirectory,'xml2json_errorLog.txt')
                if not os.path.exists(errorLogPath):
                    with open(errorLogPath, 'w') as outfile:
                        outfile.write('Error: '+iFiles+' is not a valid XML file.')
                #   and append the error to the error log file
                else:
                    with open(errorLogPath, 'a') as outfile:
                        outfile.write('Error: '+iFiles+' is not a valid XML file.')
                # and
                continue
        # for the currentJSON['rootTag']['Award']['AbstractNarration'] field, we need to convert the html entities to unicode
        # first, we need to convert the html entities to unicode
        if currentJSON['rootTag']['Award']['AbstractNarration'] is not None:
            soup=BeautifulSoup(currentJSON['rootTag']['Award']['AbstractNarration'],'html.parser')
            currentJSON['rootTag']['Award']['AbstractNarration']=soup.get_text().replace('<br/>','\n')
            #currentJSON['rootTag']['Award']['AbstractNarration']=currentJSON['rootTag']['Award']['AbstractNarration'].replace('<br>','\n')
        # also implement the directorate remapping here
        try:
            if currentJSON['rootTag']['Award']['Organization']['Directorate']['LongName'] not in validDirectorateNames:
                # get the current invalid directorate name
                currentInvalidName=currentJSON['rootTag']['Award']['Organization']['Directorate']['LongName']
                # find its index in the directorate remap file
                currentInvalidNameIndex=directorateRemap.loc[directorateRemap['foundName']==currentInvalidName].index[0]
                # remap the directorate name
                currentJSON['rootTag']['Award']['Organization']['Directorate']['LongName']=directorateRemap.loc[currentInvalidNameIndex,'fixedName']
        except:
            try:
                # if the longNamefield is empty, check the division field
                if currentJSON['rootTag']['Award']['Organization']['Division']['LongName'] not in validDirectorateNames:
                    # get the current invalid directorate name
                    currentInvalidName=currentJSON['rootTag']['Award']['Organization']['Division']['LongName']
                    # find its index in the directorate remap file
                    currentInvalidNameIndex=directorateRemap.loc[directorateRemap['foundName']==currentInvalidName].index[0]
                    # remap the directorate name
                    currentJSON['rootTag']['Award']['Organization']['Directorate']['LongName']=directorateRemap.loc[currentInvalidNameIndex,'fixedName']
            except:
                try:
                    # if this still fails, check if the field is empty, and then convert it to a "None" string
                    if currentJSON['rootTag']['Award']['Organization']['Division']['LongName'] not in validDirectorateNames:
                        # get the current invalid directorate name
                        currentInvalidName=currentJSON['rootTag']['Award']['Organization']['Division']['LongName']
                        if isempty(currentInvalidName):
                            currentInvalidName='None'
                            # remap the directorate name
                            currentJSON['rootTag']['Award']['Organization']['Directorate']['LongName']=currentInvalidName
                        else:
                            print(currentInvalidName)
                except:
                    print('Directorate remapping failed for '+currentJSON['rootTag']['Award']['AwardID'])

        
        # append the JSON data to the holder as a new record
        jsonData.append(currentJSON)
        
    # save the JSON data
    with open(savePath, 'w') as outfile:
        json.dump(jsonData, outfile)
    # print a message indicating the number of records in the JSON file, and the fields in the JSON file
    print('The JSON file contains '+str(len(jsonData))+' records.')
    print('The JSON file contains the following fields:')
    print(jsonData[0]['rootTag']['Award'].keys())
    # also print the size of the JSON file on disk
    print('The JSON file is '+str(os.path.getsize(savePath)/1e6)+' MB on disk.')
    # remove the XML files
    for iFiles in xmlFiles:
        os.remove(iFiles)
    return

def produceJSONfromXMLs_dask(xmlDirectory=None,savePath=None):
    '''
    This function converts the XML files in the specified directory to a JSON file.
    Inputs:
        xmlDirectory: string
            A string corresponding to the directory in which the XML files are located.
        savePath: string
            A string corresponding to the path to which the JSON file should be saved.
    Outputs:
        JSONpath: string
            A string corresponding to the path to which the JSON file was saved.   
    '''
    import glob
    import os
    import xmltodict
    import json
    import pandas as pd
    from bs4 import BeautifulSoup
    from dask import delayed
    import dask.bag as db
    import dask
    from dask.diagnostics import ProgressBar
    from dask.distributed import Client, progress
    import multiprocessing
    import time
    # start the timer
    startTime=time.time()
    # if the xml directory is not provided, use the current working directory
    if xmlDirectory is None:
        xmlDirectory=os.getcwd()
    # if the save path is not provided, use the current working directory
    if savePath is None:
        savePath=xmlDirectory+os.sep+'NSF_grants.json'
    # get the list of XML files
    xmlFiles=glob.glob(xmlDirectory+os.sep+'*.xml')
    # load the directorate remap file
    directorateRemap=pd.read_csv('../NSF_directorate_remap.csv')
    # get the unique valid directorate names
    validDirectorateNames=directorateRemap['fixedName'].unique()

    # create a logfile to record errors
    errorLogPath=xmlDirectory+os.sep+'errorLog.txt'
    # create a new file if it doesn't exist
    if not os.path.exists(errorLogPath):
        with open(errorLogPath, 'w') as outfile:
            outfile.write('')
    


    # first we define the functions we will use to process the XML files

    def applyFixesToRecord_NSF(inputRecord):
        """
        This function applies the established fixes to the NSF record.
        Inputs:
            inputRecord: dictionary
                A dictionary containing the JSON data.
        Outputs:
            inputRecord: dictionary
                A dictionary containing the JSON data.      
        
        """
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

    def convertXMLtoJSON_NSF(iFile):
        """
        This function converts a single XML file NSF grant application record to JSON.  
        It also includes several fixes for invalid XML files and other issues that have arisen in the NSF dataset.
        Inputs:
            iFile: string path or xml text
                A string corresponding to the path to the XML file, or the XML text itself.
        Outputs:
            currentJSON: dictionary
                A dictionary containing the JSON data.      
        """
        # create a holder for the JSON data
        currentJSON={}

        # determine if the input is a path or text
        if type(iFile)==str:
            # check if the file exists
            if os.path.exists(iFile):
                # open the XML file
                currXml=open(iFile).read()
            # if it's not a path, assume it's xml text
            else:
                currXml=iFile
            # determine if it is a valid XML file
            try:
                currentJSON=xmltodict.parse(currXml)
            except:
                try:
                    # throw a warning indicating that the file is not valid
                    with open(errorLogPath, 'a') as outfile:
                        outfile.write('Warning: \r'+iFile+'\r is not a valid XML file.\r')
                        outfile.write('Attempting to repair the file.\r')
                    # if it is not a valid XML file, use BeautifulSoup to repair it
                    currXml = BeautifulSoup(currXml, 'xml')
                    currentJSON=xmltodict.parse(currXml.prettify())
                except:
                    # if it is still not a valid XML file, throw an error
                    with open(errorLogPath, 'a') as outfile:
                        outfile.write('Error: \r'+iFile+'\r is not a valid XML file.\r')
                        outfile.write('Skipping this file.\r')
        # if its not a string, then it's neither a path nor xml text
        else: 
            # throw an error indicating that the input is not valid
            with open(errorLogPath, 'a') as outfile:
                outfile.write('Error: \r'+iFile+'\r of type '+str(type(iFile))+' is not a valid input.\r')
            
        # check if the currentJSON is empty
        if currentJSON:
            # if it's not empty then begin implementing the fixes
            currentJSON=applyFixesToRecord_NSF(currentJSON)
        else:
            # if it's empty then a warning has already been thrown
            pass
        return currentJSON

    # now we use a dask bag to process the XML files in parallel
    # first find the number of cores on the machine
    numCores=multiprocessing.cpu_count()
    # establish a dask client with the number of cores minus 2
    client = Client(n_workers=numCores-2)
    # print a message indicating the number of cores
    print('Using '+str(numCores-2)+' cores to process the XML files.')
    #


    # first we create a dask bag from the list of XML files
    print('Creating a dask bag from the list of XML files.')
    xmlFilesBag=db.from_sequence(xmlFiles)
    # then we use the dask bag to process the XML files in parallel

    print('Processing the XML files in parallel.')
    jsonFilesBag=xmlFilesBag.map(convertXMLtoJSON_NSF)
    xmlFilesBag.persist()
    progress(jsonFilesBag)
    # finally we convert the dask bag to a list
    # display a progress bar using the distributed client
    print('Converting the dask bag to a list.')
    jsonFilesList=jsonFilesBag.compute()
    # and then we convert the list to a pandas dataframe
    print('Converting the list to a pandas dataframe.')
    jsonFilesDF=pd.DataFrame(jsonFilesList)
    # and then we convert the dataframe to a dictionary
    print ('Converting the pandas dataframe to a dictionary.')
    jsonFilesDict=jsonFilesDF.to_dict('records')
    # and finally we convert the dictionary to a JSON file
    print('Converting the dictionary to a JSON file.')
    jsonFiles=json.dumps(jsonFilesDict,indent=4)
    # write the JSON file to disk  
    with open(savePath, 'w') as outfile:
        outfile.write(jsonFiles)
    outfile.close()
    # print a message indicating the number of records in the JSON file, and the fields in the JSON file
    print('The JSON file contains '+str(len(jsonFilesDict))+' records.')
    print('The JSON file contains the following fields:')
    print(jsonFilesDict[0]['rootTag']['Award'].keys())
    # also print the size of the JSON file on disk
    print('The JSON file is '+str(os.path.getsize(savePath)/1e6)+' MB on disk.')
    # print a message indicating that the conversion is complete in the relevant amount of time
    print('The conversion is complete in '+str(time.time()-startTime)+' seconds.')
    # remove the XML files
    for iFiles in xmlFiles:
        os.remove(iFiles)
    # clear the dask client
    client.close()
    # return the path to the JSON file
    return savePath
    


def detectLocalNSFData(dataDirectory=None,omnibusJSON=False):
    '''
    This function detects whether the local NSF grant data is present in the form of
    the converted omnibus json file.  If it is not present it will download and 
    convert the data, and return the path to the converted json file.  Otherwise,
    it will search the specified directory and subdirectories for the converted json,
    and return the path to the converted json file.
    Inputs:
        dataDirectory: string
            A string corresponding to the directory in which the converted json file should be located.
        omnibusJSON: boolean
            A boolean indicating whether an omnibus json file should be created from the individual xml files.
    
    Outputs:
        jsonPath: string
            A string corresponding to the path to the converted json file.   
    '''
    import glob
    import os
    # if the data directory is not provided, use the current working directory
    if dataDirectory is None:
        dataDirectory=os.getcwd()
    # check for the contents of the data directory
    dataContents=os.listdir(dataDirectory)
    # if the omnibus json file is present and omnibusJSON is True, return the path
    if 'NSF_grants_omnibus.json' in dataContents and omnibusJSON:
        print('The local NSF grant data was found at '+dataDirectory+os.sep+'NSF_grants_omnibus.json.')
        return dataDirectory+os.sep+'NSF_grants_omnibus.json'
    # if the omnibus json file is not present and omnibusJSON is True, create the omnibus json file
    elif 'NSF_grants_omnibus.json' not in dataContents and omnibusJSON:
        print('The local NSF grant data was not found.  Downloading and converting the data.')
        downloadURLs=genNSFdownloadURLs()
        downloadNSFgrantsData(downloadURLs,saveDirectory=dataDirectory)
        # use produceJSONfromXMLs to convert the XML files to a single json file
        produceJSONfromXMLs(dataDirectory,savePath=None)
        # return the path to the omnibus json file
        return dataDirectory+os.sep+'NSF_grants_omnibus.json'
    # if omnibusJSON is False, check to ensure that there are at least 100 xml files in the directory, with the presumption that they each correspond to award data records
    elif len(glob.glob(dataDirectory+os.sep+'*.xml'))>=100:
        print('The putative local NSF grant data was found at '+dataDirectory+'.')
        return dataDirectory
    # if there are not at least 100 xml files in the directory, download and unzip the data
    else:
        print('The local NSF grant data was not found.  Downloading and converting the data.')
        downloadURLs=genNSFdownloadURLs()
        downloadNSFgrantsData(downloadURLs,saveDirectory=dataDirectory)
        return dataDirectory

def NSFjson2DF(jsonPathOrFile):
    '''
    This function converts the NSF json file to a pandas dataframe.
    Inputs:
        jsonPathOrFile: string or file
            A string corresponding to the path to the NSF json file, or a dict object corresponding to the NSF converted json file.
    Outputs:
        NSFgrantDF: pandas dataframe containing the NSF grant award data
    '''
    import pandas as pd
    import json
    import os
    print('Attempting load of ' + jsonPathOrFile)
    # if the input is a string, determine if it is a path to a single file or if it is json formatted text
    if type(jsonPathOrFile) is str:
        # if the input is a path to a single file, load the json file
        if os.path.isfile(jsonPathOrFile):
            print('Loading .json file'+jsonPathOrFile)
            with open(jsonPathOrFile) as f:
                NSFjson=json.load(f)
        # if the input is json formatted text, load the json text
        else:
            print('Parsing .json text')
            NSFjson=json.loads(jsonPathOrFile)
    # if the input is a dict object, load the dict object
    elif type(jsonPathOrFile) is dict:
        print('Parsing .json dict object')
        NSFjson=jsonPathOrFile
    else:
        print('Error: The input to NSFjson2DF must be a string or a dict object.')
        print('Input type: '+str(type(jsonPathOrFile)))
        return None
    # create a holder for the data
    NSFdata=[]
    # iterate across the records in the json file
    for iRecord in NSFjson:
        # extract the data from the record
        currData=iRecord['rootTag']['Award']
        # append the data to the holder
        NSFdata.append(currData)
    # convert the data to a pandas dataframe
    NSFgrantDF=pd.DataFrame(NSFdata)
    return NSFgrantDF

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
