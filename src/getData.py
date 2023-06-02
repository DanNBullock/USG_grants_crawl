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
    from glob import glob

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
                grantsGovFile=glob(location + grantsGovFileStem + '*.[xX][mM][lL]')
                # then check for json, and cat the results
                grantsGovFile=grantsGovFile+glob(location + grantsGovFileStem + '*.[jJ][sS][oO][nN]')
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
                grantsGovFiles=glob(location + '*.xml')
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
                nsfFile=glob(location + nsfFileStem + '*.[xX][mM][lL]')
                # then check for json, and cat the results
                nsfFile=nsfFile+glob(location + nsfFileStem + '*.[jJ][sS][oO][nN]')
                # if the file is found, return the path
                if len(nsfFile)>0:
                    return nsfFile[0]
                # if the file is not found, return False
                else:
                    return False

            # check for the multiple files
            elif singleMulti=='multi':
                # check for the multiple files, just assume they are numbered and end with .xml
                nsfFiles=glob(location + '*.xml')
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
    from glob import glob

    # check if the input destination path already terminates in a directory named sourceOrg
    if destination.split(os.sep)[-1]==sourceOrg:
        # if it already terminates in the sourceOrg directory split out the paths thusly
        rawDestinationPath=os.sep.join(destination.split(os.sep)[:-1])
        destinationPlusSourcePath=os.path.join(destination,sourceOrg)
        destination=destinationPlusSourcePath
    else:
        # otherwise combine the components to the the relevant paths
        rawDestinationPath=destination
        destinationPlusSourcePath=os.path.join(destination,sourceOrg)
        destination=destinationPlusSourcePath
    
    print('Searching for data in ' +destinationPlusSourcePath + '...')

    # in either case
    # first check if the destinationPlusSourcePath exists, as this is the prefered location
    if not os.path.isdir(destinationPlusSourcePath):
        # if it doesn't exist, check if the raw destination exists
        if not os.path.isdir(rawDestinationPath):
            # if it doesn't exist, create it
            os.mkdir(rawDestinationPath)
            # then add the sourceOrg directory
            os.mkdir(destinationPlusSourcePath)
            # then set the destination to the destinationPlusSourcePath
            destination=destinationPlusSourcePath

        # if the raw destination does exist, but the sourceOrg doesn't just create the sourceOrg directory
        else:
            os.mkdir(destinationPlusSourcePath)
            # then set the destination to the destinationPlusSourcePath
            destination=destinationPlusSourcePath  
        
    # if the destinationPlusSourcePath does exist, set the destination to the destinationPlusSourcePath
    # and then check that directory for the 
    else:
        # NOTE: this is where to add additional data sources
        # if it does exist, check for the data
        # for the grants.gov data, check for the single xml
        if sourceOrg=='grantsGov':
            # check for the single file
            # use the file stem to check for the file
            grantsGovFileStem='GrantsDBExtract'
            # first check for xml
            grantsGovFile=glob(destination + os.sep + grantsGovFileStem + '*.xml')

            # then check for json, and cat the results
            # if the file is found, return True, no need to go and re-download
            if len(grantsGovFile)>0:
                print('The grants.gov data has already been downloaded.  No need to re-download.')
                print('The file is located at ' + grantsGovFile[0] + '.')
                return grantsGovFile[0]
            # if the file is not found, continue
            else:
                print('The grants.gov data has not yet been downloaded.  Downloading now.')
                pass

        # for the NIH data, check for the single xml
        # TODO: confirm that this is the case
        elif sourceOrg=='NIH':
            # check for the single file
            # use the file stem to check for the file
            nihFileStem='NIH_Awards'
            # first check for xml
            nihFile=glob(destination + nihFileStem + '*.[xX][mM][lL]')
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
            nsfFiles=glob(destination + '*.zip')
            # then check for tar, cat the results
            nsfFiles=nsfFiles+glob(destination + '*.tar')
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
                    print('The grants.gov data has been downloaded to ' + grantsGovFile + '.')
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