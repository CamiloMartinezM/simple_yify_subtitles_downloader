#!/usr/bin/env python
# -*- coding: utf-8 -*-

encoding = "utf8"

import os
import requests, bs4

"""
    BORING STUFF
"""
# Builds the intro by printing lines according to getTerminalSize()
def buildIntro():
    cmd = 'mode 80,20'
    os.system(cmd)
    sizex = 80/2
    for i in range(sizex):
        print "*",
    print("")
    print("")
    title = "Hi! Welcome to your subtitles downloader!"
    for i in range((sizex*2-len(title))/4):
        print " ",
    print title,
    for i in range((sizex*2-len(title))/4):
        print " ",
    print("")
    title2 = "Developed by Camilo Martinez"
    print(" "*(sizex*2-len(title2)-1)),
    print(title2)
    print("")
    for i in range(sizex):
        print "*",
    print("")
    print("")
    
# Intro
buildIntro()

"""
    DETERMINING INITIAL ENTRIES/PARAMETERS
"""
# Asking what the user is interested in
movieName = raw_input("[+] What movie can I help you with? > ")

codeLang = raw_input("[+] What language? (Enter: es, de, en) > ")
while codeLang != "es" and codeLang != "en" and codeLang != "de":
    codeLang = raw_input("[+] I'm sorry, I didn't get that (Enter: es, de, en) > ")

wordsInMovie = movieName.split()

# Concatenating the string to look for the movie
url = "https://www.yifysubtitles.com/search?q="
cont = 0
for wordInMovie in wordsInMovie:
    if cont == 0:
        url += wordInMovie
    else:
        url += "+" + wordInMovie
    cont = 1

"""
    GENERATING A REQUEST TO LOOK FOR THE MOVIE IN OpenSubtitles
"""
res = requests.get(url)          # Generate a request

try:                             # In case there is an error loading the provided URL
    res.raise_for_status()
except:
    print("")
    print("[+] I'm sorry, there was an error loading the movies.")
    raise SystemExit             # Quits the program

soup = bs4.BeautifulSoup(res.text, features="html.parser")      # BeautifulSoup object 

movieElements = soup.select('a[href] > div > h3.media-heading')                 
yearElements = soup.select('li > div > a[href] > div > span.movinfo-section')
yearElementsNew = []

# Parsing yearElements
for yearElement in yearElements:
    if "year" in yearElement.getText():
        yearElementsNew.append(yearElement)

yearElements = yearElementsNew

"""
    GETTING AND PRINTING TO THE USER THE LIST OF AVAILABLE MOVIES TO CHOOSE FROM
"""
print("[+] List of available movies:")                               
print("") 
cont = 1                                # Counter that lists each movie
possiblePositions = []                  # Stores the values of cont
for movie in movieElements:             # Prints all the movies available in a formatted way
    rawStr = movie.getText()
    newStr = rawStr.replace('"', "")
    newStrList = newStr.split()
    newStr = ""
    for i in newStrList:
        newStr += i + " "

    print(str(cont) + " > " + newStr + "(" + yearElements[cont-1].getText().replace("year","") + ")")
    possiblePositions.append(str(cont))
    cont += 1

print("")

"""
    SPECIFYING WHICH MOVIE THE USER WANTS AND THE NUMBER OF SUBTITLES TO DOWNLOAD
"""
elementPos = raw_input("[+] Number of the movie you want > ")           # Position of the selected movie
while elementPos not in possiblePositions:
    elementPos = raw_input("[+] That is not on the previous list. Repeat > ")

# Sets the actual name of the movie
selectedMovieElement = movieElements[int(elementPos)-1]
yearOfMovie = yearElements[int(elementPos)-1].getText().replace("year","")
rawStr = selectedMovieElement.getText()
newStr = rawStr.replace('"', "")
newStrList = newStr.split()
movieName = ""
for i in newStrList:
    movieName += i + " "
    
numberOfSubtitles = raw_input("[+] How many subtitles do you want to download? > ")   # Defines the number of subtitles to download
repeat = True
while repeat:
    try:
        if int(numberOfSubtitles) >= 1:
            repeat = False
        else:
            numberOfSubtitles = raw_input("[+] That's not possible. Repeat > ")
    except:
        numberOfSubtitles = raw_input("[+] I didn't quite get that. Repeat > ")

print("")

"""
    GETTING THE INFORMATION OF EACH MOST DOWNLOADED SUBTITLE
    -I should probably patent this part of the code-
"""
allMovieLinks = soup.select('li.media.media-movie-clickable > div.media-body > a[href]')
urlContinuation = "" 
for movieLink in allMovieLinks:                             # Finds parent tag that contains the selected movie to get the URL
    href = movieLink.get('href')
    tmpElement = soup.select('a[href="'+href+'"] > div > h3.media-heading[itemprop]')
    if tmpElement[0].getText() == selectedMovieElement.getText():
        urlContinuation = href
        break
        
url = "https://www.yifysubtitles.com" + urlContinuation     # New URL associated with the selected movie
res = requests.get(url)                                     # Generate a request

try:                                                        # In case there is an error loading the provided URL
    res.raise_for_status()
except:
    print("[+] I'm sorry, there was an error loading the subtitles. Try again later.")
    exit

soup = bs4.BeautifulSoup(res.text, features="html.parser")                       # BeautifulSoup object 

subtitleElements = soup.select('tr[data-id] > td.flag-cell > span.sub-lang')     # Gets the elements that matched the provided chain of tags

if codeLang == "de":            # Sets language name
    language = "german"
elif codeLang == "en":
    language = "english"
else:
    language = "spanish"
    
newSubtitleElements = []
pos = 0
cont = 0
alreadyFoundPos = False
for subtitleElement in subtitleElements:                    # Gets the subtitles that match the selected by the user
    if subtitleElement.getText().lower() == language:
        if not alreadyFoundPos:
            pos = cont+1
            alreadyFoundPos = True
        newSubtitleElements.append(subtitleElement)
    cont += 1

subtitleElements = newSubtitleElements

"""
    ACTUALLY DOWNLOAD THE SUBTITLES
"""
import locale

# Returns the default downloads path for linux or windows
def getDownloadPath():
    if os.name == 'nt':
        import ctypes
        from ctypes import windll, wintypes
        from uuid import UUID

        # ctypes GUID copied from MSDN sample code
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8)
            ] 

            def __init__(self, uuidstr):
                uuid = UUID(uuidstr)
                ctypes.Structure.__init__(self)
                self.Data1, self.Data2, self.Data3, \
                    self.Data4[0], self.Data4[1], rest = uuid.fields
                for i in range(2, 8):
                    self.Data4[i] = rest>>(8-i-1)*8 & 0xff

        SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
        SHGetKnownFolderPath.argtypes = [
            ctypes.POINTER(GUID), wintypes.DWORD,
            wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
        ]

        def _get_known_folder_path(uuidstr):
            pathptr = ctypes.c_wchar_p()
            guid = GUID(uuidstr)
            if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
                raise ctypes.WinError()
            return pathptr.value

        FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'
        return _get_known_folder_path(FOLDERID_Download)
    else:
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

# Returns the default my documents path for linux or windows
def getDocumentsPath():
    import ctypes.wintypes
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value

# Downloads the subtitle to the specified folder
def downloadSubtitleToFolder(link, folder):
    url = "https://www.yifysubtitles.com" + link    # New URL associated with the subtitle
    res = requests.get(url)                         # Generate a request

    try:                             # In case there is an error loading the provided URL
        res.raise_for_status()
    except:
        print("")
        print("[+] I'm sorry, there was an error loading the movies.")
        raise SystemExit             # Quits the program

    soup = bs4.BeautifulSoup(res.text, features="html.parser")     # Beautifulsoup object
    download = soup.select("div.col-xs-12 > a.btn-icon.download-subtitle[href]")

    newUrl = download[0].get('href')                # New URL associated with the subtitle
    res = requests.get(newUrl)                      # Generate a request

    try:                             # In case there is an error loading the provided URL
        res.raise_for_status()
    except:
        print("")
        print("[+] I'm sorry, there was an error loading the movies.")
        raise SystemExit             # Quits the program

    zname = os.path.join(folder, "Subtitle"+str(i+1)+".zip")
    zfile = open(zname, "wb")
    zfile.write(res.content)
    zfile.close()
    
# Created a folder in my documents if it doesn't exist yet
newFolder = getDownloadPath() + "\\" + language[0].upper() + language[1:] + " subtitles for " + movieName + "(" + yearOfMovie + ")"
try:
    try:
        if not os.path.exists(newFolder):
            os.mkdir(newFolder)
    except:
        print("[+] There was an error storing the subtitles. Contact Camilo Martinez at once!")
        raise SystemExit             # Quits the program

    for i in range(int(numberOfSubtitles)):
        subtitleElement = soup.select('tbody > tr[data-id]:nth-child('+str(pos+i)+') > td.flag-cell > span.sub-lang')
        if subtitleElement[0].getText().lower() != language:
            if int(numberOfSubtitles) > i:
                if i == 1:
                    plural = ""
                else:
                    plural = "s"
                print("[+] I'm sorry, I could only download " + str(i) + " subtitle" + plural + ".")
                numberOfSubtitles = str(i)
            break
        
        subtitleLinkElement = soup.select('tbody > tr[data-id]:nth-child('+str(pos+i)+') > td > a[href]')[0]
        link = subtitleLinkElement.get('href')
        print("[+] Downloading subtitle " + str(i+1) + "...")
        downloadSubtitleToFolder(link, newFolder)
except:    
    print("[+] I'm sorry, but it seems there are no " + language.lower() + " subtitles for this movie yet.")
    print("[+] Quitting now...")
    raise SystemExit             # Quits the program


print("")
print("[+] Unzipping subtitles...")

# Unzipping files
import zipfile

for i in range(int(numberOfSubtitles)):
    zip_ref = zipfile.ZipFile(newFolder + "\\Subtitle" + str(i+1) + ".zip", 'r')
    zip_ref.extractall(newFolder)
    zip_ref.close()
    os.remove(newFolder + "\\Subtitle" + str(i+1) + ".zip")
        
print("")
print("[+] Done!")
print("[+] Your subtitles have been succesfully stored inside a folder named 'Subtitles for " + movieName + "(" + yearOfMovie + ")'.")
print("[+] Check your Downloads folder!")
print("[+] Have a good one!")
print("[+] Quitting now...")

