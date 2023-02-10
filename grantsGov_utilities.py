from bs4 import BeautifulSoup
import xmltodict
import sys
import os
import pandas as pd
import glob

testString='test1234567'

testString.replace('test','oops').replace('test','yeay')

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
    grantsDF=pd.DataFrame.from_records(govGrantData_dictionary['Grants']['OpportunitySynopsisDetail_1_0'], columns=['OpportunityID', 'OpportunityTitle','OpportunityNumber','AgencyCode', 'AgencyName', 'AwardCeiling', 'AwardFloor', 'EstimatedTotalProgramFunding', 'ExpectedNumberOfAwards', 'Description'])
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
    savePath : str
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
    if savePath == None:
        savePath = ''
    # check if the path exists
    elif os.path.isdir(savePath):
        # do nothing, the path is set
        pass
    # if the directory doesn't exist, *don't* make the directory, instead raise an error
    else:
        raise Exception ('Input save path\n' + savePath + '\ndoes not exist. Create first.')

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
        print('Saved to ' + savePath)

    # establish save path
    zipSavePath=os.path.join(savePath,fullFileName)
    # download
    download_url(queryURL, zipSavePath, chunk_size=128)
    # unzip in place
    with zipfile.ZipFile(zipSavePath, 'r') as zip_ref:
        zip_ref.extractall(savePath)
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
                print(grantQuantificationValues_RE_sorted)
        if not np.equal(grantQuantificationValues,grantQuantificationValues_RE_sorted):
            correctedCount=correctedCount+1
        print(str(correctedCount) + ' grant funding value records repaired')
        grantsDF[[quantColumns]].iloc[iIndex]=grantQuantificationValues_RE_sorted

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
    grantsDF.insert(allColumnNameslist.index('AgencyCode')+1,'AgencySubCode', '')
    #quantColumns=['AgencyName','AgencyCode']
    # set a fill value for null name values
    fillValue='Other'

    correctedCount=0
    for iIndex,iRows in grantsDF.iterrows():
        currAgencyName=iRows['AgencyName']
        currAngencyCode=iRows['AgencyCode']
        # try and split the subcode out now
        try:
            currAngencySubCode=currAngencyCode.split('-',1)[1]
        except:
            currAngencySubCode=''
        # go ahead and throw it in
        grantsDF['AgencySubCode'].iloc[iIndex]=currAngencySubCode

        #create a vector to hold all of these
        
        inputInfo=[currAgencyName,currAngencyCode,currAngencySubCode]

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

            correctedCount =correctedCount + 1

        # if the name is null set it to the fill value as well
        if currAgencyName == '':
            currAgencyName=fillValue
            correctedCount =correctedCount + 1
            try:
                currAngencySubCode=currAngencyCode.split('-',1)[1]
            except:
                currAngencySubCode=''
        
        outputInfo=[currAgencyName,currAngencyCode,currAngencySubCode]
        #if there is new information to add, update the record
        if not inputInfo==outputInfo:
            grantsDF[['AgencyName','AgencyCode','AgencySubCode']].iloc[iIndex] =  outputInfo
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


















    # find the list elements where the agency full name was not available (i.e. worst case), and thus set to NAN (which was then replaced with 0)
    grantsDF['AgencyName'].loc[grantsDF['AgencyName'].eq(0)]='Other'
    # this will serve as a backstop in the event no information was provided

    # in the event no agency code is provided (and thus set to 0) use the capital letters of the agency name
    grantsDF['AgencyCode'].loc[grantsDF['AgencyCode'].eq(0)]=grantsDF['AgencyName'].loc[grantsDF['AgencyCode'].eq(0)].map(lambda x: ''.join([char for char in x if char.isupper()]))

    # however, we don't want to have surreptitiously created the 'O' agency, so set 'O' to other, instead of the abbreviation
    grantsDF['AgencyCode'].loc[grantsDF['AgencyCode'].eq('O')]='Other'

    # also remove everything after the first hyphen.  We dont need to go that far down for this in the hirearchy
    grantsDF['AgencyCode']=grantsDF['AgencyCode'].map(lambda x: x.split('-',1)[0])




                        
    # get an exclusion vector for where there's simply no useful information
    emptyFundingVec=np.all(grantsDF[['AwardCeiling','AwardFloor','EstimatedTotalProgramFunding']].eq(0).values,axis=1)
    singletonGrantVec=grantsDF['ExpectedNumberOfAwards'].eq(1).values
    notUsefulVec=np.logical_and(emptyFundingVec,singletonGrantVec)

    # you're giving at least one grant, lets assume that 
    grantsDF['ExpectedNumberOfAwards'].loc[ grantsDF['ExpectedNumberOfAwards'].eq(0)]=1

    # where you have a value for an award ceiling and an expected number of awards, you can at least guess an 
    # estimated total program funding when there is a single expected award
    grantsDF['EstimatedTotalProgramFunding'].loc[ grantsDF['ExpectedNumberOfAwards'].eq(1)]=grantsDF['AwardCeiling'].loc[ grantsDF['ExpectedNumberOfAwards'].eq(1)]
    
    # find candidates for AwardCeiling--ExpectedNumberOfAwards flip
    ceilLessAwardNumBool=np.less(grantsDF['AwardCeiling'],grantsDF['ExpectedNumberOfAwards'])
    awardNumLargerAwardFloor=np.greater(grantsDF['ExpectedNumberOfAwards'],grantsDF['AwardFloor'])
    
    grantNumAboveFloorValThresh=grantsDF['ExpectedNumberOfAwards'].ge(floorThresh).values
    grantsDF.loc[np.all([np.logical_not(notUsefulVec),grantNumAboveFloorValThresh,ceilLessAwardNumBool,awardNumLargerAwardFloor],axis=0)]

    # find the grant locations where the expected number of grants exceeds the total value (indicating something has been enered wrong)
    # but there's still useful info
    
    grantsDF.loc[np.logical_and(np.logical_not(notUsefulVec),np.less_equal(grantsDF['EstimatedTotalProgramFunding'],grantsDF['ExpectedNumberOfAwards']))]




























# if the cleaned data already exists
if os.path.isfile('allGrantsData.csv'):
    # remember, we are using the bar instead of comma
    grantsDF=pd.read_csv('allGrantsData.csv',sep='|')
    print('Cleaned CSV loaded')
    
    # Use wildcard to find anything that matches the requirement, and use the latest one
elif os.path.isfile(glob.glob(os.path.join('inputData','GrantsDBExtract*.xml'))[-1]):
    pathToXML=glob.glob(os.path.join('inputData','GrantsDBExtract*.xml'))[-1]
    # open and parse file
    with open(pathToXML, 'r') as f:
        govGrantData_raw = f.read()
    # convert xml to dictionary
    with open(pathToXML) as xml_file:
        govGrantData_dictionary = xmltodict.parse(xml_file.read())
        
    # convert to pandas dataframe
    grantsDF=pd.DataFrame.from_records(govGrantData_dictionary['Grants']['OpportunitySynopsisDetail_1_0'], columns=['OpportunityID', 'OpportunityTitle','OpportunityNumber','AgencyCode', 'AgencyName', 'AwardCeiling', 'AwardFloor', 'EstimatedTotalProgramFunding', 'ExpectedNumberOfAwards', 'Description'])
    # proactively replace nans for agency name with other
    # replace the nans
    grantsDF=grantsDF.fillna(0)
    # free up memory
    del govGrantData_dictionary
    




    # now do a bit of cleaning
    grantsDF[['AwardCeiling','AwardFloor','EstimatedTotalProgramFunding','ExpectedNumberOfAwards']]=grantsDF[['AwardCeiling','AwardFloor','EstimatedTotalProgramFunding','ExpectedNumberOfAwards']].astype(np.int64)
    # ideally, the names would all be formatted the same and reliable, allowing us to just index into a pandas column. 
    # however, they're not, so we have to use this approach, and attempt to replace unreliable ones.

    # find the list elements where the agency full name was not available (i.e. worst case), and thus set to NAN (which was then replaced with 0)
    grantsDF['AgencyName'].loc[grantsDF['AgencyName'].eq(0)]='Other'
    # this will serve as a backstop in the event no information was provided

    # in the event no agency code is provided (and thus set to 0) use the capital letters of the agency name
    grantsDF['AgencyCode'].loc[grantsDF['AgencyCode'].eq(0)]=grantsDF['AgencyName'].loc[grantsDF['AgencyCode'].eq(0)].map(lambda x: ''.join([char for char in x if char.isupper()]))

    # however, we don't want to have surreptitiously created the 'O' agency, so set 'O' to other, instead of the abbreviation
    grantsDF['AgencyCode'].loc[grantsDF['AgencyCode'].eq('O')]='Other'

    # also remove everything after the first hyphen.  We dont need to go that far down for this in the hirearchy
    grantsDF['AgencyCode']=grantsDF['AgencyCode'].map(lambda x: x.split('-',1)[0])
    print('XML file loaded, converted to dataframe, and partially cleaned')
else:
# FUTURE NOTE: it may be possible to do a check for a local file meeting the relevant criterion and conditionally 
# download from https://www.grants.gov/extract/ (and extract compressed file) in the event a local target isn't found.
# For the moment thoug




import zipfile
with zipfile.ZipFile("file.zip","r") as zip_ref:
    zip_ref.extractall("targetdir")









# checker.py


from http.client import HTTPConnection
from urllib.parse import urlparse
import numpy as np

def site_is_online(url, timeout=2):
    """Return True if the target URL is online.

    Raise an exception otherwise.
    """
    error = Exception("unknown error")
    parser = urlparse(url)
    host = parser.netloc or parser.path.split("/")[0]
    for port in (80, 443):
        connection = HTTPConnection(host=host, port=port, timeout=timeout)
        try:
            connection.request("HEAD", "/")
            return True
        except Exception as e:
            return False
        finally:
            connection.close()
    raise error



testLinkGood = 'https://www.grants.gov/grantsws/rest/opportunity/att/download/324381'
testLinkBad  = '123456'

print(site_is_online(testLinkGood))
print(site_is_online(testLinkBad))


import requests

def get_url_status(url):  # checks status for each url in list urls
    
        try:
            r = requests.get(url)
            return r.status_code
        except Exception as e:
           
            return False

print(get_url_status(testLinkGood))
print(get_url_status(testLinkBad))



open_df = pd.read_csv('open_applications.csv')
open_id = list(open_df['id'])
base_url='http://www.grants.gov/grantsws/rest/opportunity/details?oppId='
#base_url= 'http://www.grants.gov/grantsws/OppDetails?oppId='
document_url = 'http://www.grants.gov/grantsws/rest/oppdetails/att/download/'

import json
import requests

def readPDF(filename):
    input = PdfFileReader(file(filename, "rb"))
    content = ''
    for page in input.pages:
        content += ' ' + page.extractText()
    return content

def download_file(url):
    local_filename = url.split('/')[-1] + '.pdf'
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

def getGrantData(oppID):
    url = base_url + str(oppID)
    response = requests.get(url)
    data = json.loads(response.content)
    f = open(str(oppID) + '.json', 'wb')
    try:
        document_id = data['synopsisAttachmentFolders'][0]['synopsisAttachments'][0]['id']
        doc_url = document_url + str(document_id)
        pdfFileName = download_file(doc_url)
        pdfData = readPDF(pdfFileName)
        data['synopsisAttachmentFolders'][0]['synopsisAttachments'][0]['documentContent'] = pdfData
    except:
        pass
    data = json.dumps(data)
    return data


testID=262149

#grantDataOut=getGrantData(262149)
#print(grantDataOut)
oppID=testID

def load_details(opp_id):
    return requests.post("https://www.grants.gov/grantsws/rest/opportunity/details", data={'oppId': opp_id}).json()
detailsOut=load_details(oppID)

grantsFindJSON='C:\\Users\\dbullock\\Documents\\code\\gitDir\\USG_grants_crawl\\grantFindsOut.json'
# Opening JSON file
f = open(grantsFindJSON)
keywordsData=json.load(f )
f.close()

idList=[]
for iKeywords in list(keywordsData.keys()):
    idList.extend(keywordsData[iKeywords])
import numpy as np
uniqueIDs,counts=np.unique(idList, return_counts=True)

atLeastTwiceIDs=uniqueIDs[counts>=2]
storeOutputDirectory='C:\\Users\\dbullock\\Documents\\code\\dataSources\\grantData'
import os
docDownloadLink='https://www.grants.gov/grantsws/rest/opportunity/att/download/'

for twiceIDs in atLeastTwiceIDs:
    currentSaveDir=os.path.join(storeOutputDirectory,str(twiceIDs))
    if not os.path.exists(currentSaveDir):
        os.mkdir(currentSaveDir)
        detailsOut=load_details(twiceIDs)
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
            pass