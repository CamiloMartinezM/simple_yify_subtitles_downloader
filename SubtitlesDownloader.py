#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bs4
import requests
import zipfile
import shutil
import os
encoding = "utf8"


def buildIntro():
    """ Builds the introduction of the program """

    cmd = 'mode 80,20'
    os.system(cmd)
    sizex = 80/2
    for i in range(int(sizex)):
        print("*", end=" ")
    print("")
    print("")
    title = "Hi! Welcome to your subtitles downloader!"
    for i in range(int((sizex*2-len(title))/2)):
        print("", end=" ")
    print(title, end=" ")
    for i in range(int((sizex*2-len(title))/2)):
        print("", end=" ")
    title2 = "Developed by Camilo Martinez"
    print(" "*(int(sizex*2-len(title2)-3)), end=""),
    print(title2)
    print("")
    for i in range(int(sizex)):
        print("*", end=" ")
    print("")
    print("")


def getUserEntries():
    """ Gets the information of the movie the user is interested in """

    movieName = input("[+] What movie can I help you with? > ")

    codeLang = input("[+] What language? (Enter: es, de, en) > ")
    while codeLang != "es" and codeLang != "en" and codeLang != "de":
        codeLang = input("[+] I'm sorry, I didn't get that (Enter: es, de, en) > ")

    return movieName, codeLang


def createUrl(movieName, codeLang):
    """ Creates the correct url to look for the movie """

    wordsInMovie = movieName.split()
    url = "https://www.yifysubtitles.com/search?q="
    cont = 0
    for wordInMovie in wordsInMovie:    # Concatenation of the strings necessary to create the url.
        if cont == 0:
            url += wordInMovie
        else:
            url += "+" + wordInMovie
        cont = 1

    return url


def getMovieElements(url):
    """ Gets the movie elements (tag objects) in YifySubtitles """

    res = requests.get(url)   # Generates a request to the created url.

    try:
        res.raise_for_status()
    except:
        print("")
        print("[+] I'm sorry, there was an error loading the movies.")
        raise SystemExit

    soup = bs4.BeautifulSoup(res.text, features="html.parser")

    movieElements = soup.select('a[href] > div > h3.media-heading')
    yearElements = soup.select('li > div > a[href] > div > span.movinfo-section')
    yearElementsNew = []

    # Parsing yearElements
    for yearElement in yearElements:
        if "year" in yearElement.getText():
            yearElementsNew.append(yearElement)

    yearElements = yearElementsNew

    if not movieElements:
        print("[+] It seems there are no available movies that match your entry. I'm sorry.")
        trash = input("[+] Press any key to quit...")
        raise SystemExit

    return yearElements, movieElements, soup


def printListOfAvailableMovies(yearElements, movieElements):
    """ Prints the table of available movies """

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

        print(str(cont) + " > " + newStr +
              "(" + yearElements[cont-1].getText().replace("year", "") + ")")
        possiblePositions.append(str(cont))
        cont += 1

    print("")
    return possiblePositions


def getPositionFromListOfAvailableMovies(possiblePositions):
    """ Gets the position of the movie the user wants from the list of available movies """

    position = input("[+] Number of the movie you want > ")
    while position not in possiblePositions:
        elementPos = input("[+] That is not on the previous list. Repeat > ")

    return position


def getActualMovieInformation(positionOfMovie, movieElements, yearElements):
    """ Sets the actual name of the movie the user wants """

    elementPos = positionOfMovie
    selectedMovieElement = movieElements[int(elementPos)-1]
    yearOfMovie = yearElements[int(elementPos)-1].getText().replace("year", "")
    rawStr = selectedMovieElement.getText()
    newStr = rawStr.replace('"', "")
    newStrList = newStr.split()
    movieName = ""
    for i in newStrList:
        movieName += i + " "

    return movieName, selectedMovieElement, yearOfMovie


def getNumberOfSubtitles():
    """ Gets the number of subtitles the user wants """

    numberOfSubtitles = input("[+] How many subtitles do you want to download? > ")
    repeat = True
    while repeat:
        try:
            if int(numberOfSubtitles) >= 1:
                repeat = False
            else:
                numberOfSubtitles = input("[+] That's not possible. Repeat > ")
        except:
            numberOfSubtitles = input("[+] I didn't quite get that. Repeat > ")

    return numberOfSubtitles


def getSubtitleElements(soup, codeLang, selectedMovieElement, language):
    """ Gets the information of each most downloaded subtitle of the movie the user specified """

    allMovieLinks = soup.select('li.media.media-movie-clickable > div.media-body > a[href]')
    urlContinuation = ""
    for movieLink in allMovieLinks:                             # Finds parent tag that contains the selected movie to get the URL
        href = movieLink.get('href')
        tmpElement = soup.select('a[href="'+href+'"] > div > h3.media-heading[itemprop]')
        if tmpElement[0].getText() == selectedMovieElement.getText():
            urlContinuation = href
            break

    # New URL associated with the selected movie
    url = "https://www.yifysubtitles.com" + urlContinuation
    res = requests.get(url)                                     # Generate a request

    try:                                                        # In case there is an error loading the provided URL
        res.raise_for_status()
    except:
        print("[+] I'm sorry, there was an error loading the subtitles. Try again later.")
        trash = input("")
        raise SystemExit

    # BeautifulSoup object
    soup = bs4.BeautifulSoup(res.text, features="html.parser")

    # Gets the elements that matched the provided chain of tags
    subtitleElements = soup.select('tr[data-id] > td.flag-cell > span.sub-lang')

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
    return subtitleElements, pos, soup


def getDownloadPath():
    """ Returns the default downloads path for linux or windows """

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
                    self.Data4[i] = rest >> (8-i-1)*8 & 0xff

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


def getDocumentsPath():
    """ Returns the default my documents path for linux or windows """

    import ctypes.wintypes
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value


def downloadSubtitleToFolder(link, folder, i):
    """ Downloads the subtitle to the specified folder """

    url = "https://www.yifysubtitles.com" + link    # New URL associated with the subtitle
    res = requests.get(url)                         # Generate a request

    try:
        res.raise_for_status()
    except:
        print("")
        print("[+] I'm sorry, there was an error loading the movies.")
        raise SystemExit

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

    zname = os.path.join(folder, "Subtitle" + str(i+1) + ".zip")
    zfile = open(zname, "wb")
    zfile.write(res.content)
    zfile.close()


def createFolderToStoreSubtitles(language, movieName, yearOfMovie):
    """ Creates a folder to store the subtitles """

    formattedMovieName = ' '.join(movieName.strip().split())
    newFolder = getDownloadPath() + "\\" + \
        language[0].upper() + language[1:] + " subtitles for " + \
        formattedMovieName + "(" + yearOfMovie.strip() + ")"
    newFolderCreated = True

    try:
        os.mkdir(newFolder)
    except:
        try:
            shutil.rmtree(newFolder, ignore_errors=True)
            os.mkdir(newFolder)
        except:
            try:
                newFolder = getDownloadPath() + "\\" + language[0].upper(
                ) + language[1:] + " subtitles for " + movieName.strip().split()[0] + " (" + yearOfMovie.strip() + ")"
                os.mkdir(newFolder)
            except:
                try:
                    shutil.rmtree(newFolder, ignore_errors=True)
                    os.mkdir(newFolder)
                except:
                    newFolderCreated = False

    if not newFolderCreated:            # In case a new folder could not be created.
        newFolder = getDownloadPath()

    return newFolder


def downloadSubtitles(soup, language, numberOfSubtitles, positionOfSubtitles, movieName, yearOfMovie, folder):
    """ Downloads the subtitles to the created folder """

    print("")
    try:
        pos = positionOfSubtitles
        forLoopBroken = False
        for i in range(int(numberOfSubtitles)):
            subtitleElement = soup.select(
                'tbody > tr[data-id]:nth-child('+str(pos+i)+') > td.flag-cell > span.sub-lang')
            if subtitleElement[0].getText().lower() != language:
                forLoopBroken = True
                numberOfSubtitles = i
                break

            subtitleLinkElement = soup.select(
                'tbody > tr[data-id]:nth-child('+str(pos+i)+') > td > a[href]')[0]
            link = subtitleLinkElement.get('href')
            print("[+] Downloading subtitle " + str(i+1) + "...")
            downloadSubtitleToFolder(link, folder, i)

        if forLoopBroken:
            if i == 1:
                plural = ""
            else:
                plural = "s"

            print("")
            print("[+] I'm sorry, I could only download " + str(i) + " subtitle" + plural + ".")

        return numberOfSubtitles
    except:
        print("[+] I'm sorry, I could not download the subtitles. Try again later.")
        trash = input("[+] Press any key to quit...")
        raise SystemExit


def unzipSubtitles(numberOfSubtitles, folder, movieName, year, codeLang):
    """ Unzips the downloaded subtitles """

    print("")
    print("[+] Unzipping subtitles...")
    for i in range(int(numberOfSubtitles)):
        zip_ref = zipfile.ZipFile(folder + "\\Subtitle" + str(i+1) + ".zip", 'r')
        zip_ref.extractall(folder + "\\Subtitle" + str(i+1))
        zip_ref.close()

    i = 0
    j = 0
    for j in range(int(numberOfSubtitles)):
        zipdata = zipfile.ZipFile(folder + "\\Subtitle" + str(j+1) + ".zip", 'r')
        zipinfos = zipdata.infolist()

        for zipinfo in zipinfos:
            old_file = os.path.join(folder + "\\Subtitle" + str(j+1), zipinfo.filename)
            new_file = os.path.join(folder, "Subtitle" + str(i+1) + "_" + codeLang +
                                    "_" + '.'.join(movieName.strip().split()) + "(" + year.strip() + ").srt")

            try:
                os.rename(old_file, new_file)
            except:
                new_file = os.path.join(folder, "Subtitle" + str(i+1) + "_" + codeLang +
                                        "_" + movieName.strip().split()[0] + "(" + year.strip() + ").srt")
                os.rename(old_file, new_file)

            i += 1

        zipdata.close()

    for i in range(int(numberOfSubtitles)):
        os.remove(folder + "\\Subtitle" + str(i+1) + ".zip")
        shutil.rmtree(folder + "\\Subtitle" + str(i+1), ignore_errors=True)

    print("")
    print("[+] Done!")
    print("[+] Your subtitles have been succesfully stored in your downloads folder!")

    trash = input("[+] Press any key to quit...")


def main():
    """ Main function """

    # Build the introduction to the program.
    buildIntro()

    # Gets the name of the movie and the language the user wants.
    movieName, codeLang = getUserEntries()

    # Sets language name
    if codeLang == "de":
        language = "german"
    elif codeLang == "en":
        language = "english"
    else:
        language = "spanish"

    # Creates a valid url for YifySubtitles in order to get a list of available
    # movies whose name match the name provided by the user.
    url = createUrl(movieName, codeLang)

    # Gets the movie and year tag-elements associated with the created url.
    yearElements, movieElements, soup = getMovieElements(url)

    # Prints the list of available movies and gets all the possible possible
    # positions associated with them.
    possiblePositionsOfMovies = printListOfAvailableMovies(yearElements, movieElements)

    # Gets the position of the movie the user actually wants.
    positionOfMovie = getPositionFromListOfAvailableMovies(possiblePositionsOfMovies)

    # Gets the number of subtitles the user wants to download.
    numberOfSubtitles = getNumberOfSubtitles()

    # Gets the actual information associated with the movie the user wants,
    # taken directly from YifySubtitles.
    movieName, selectedMovieElement, yearOfMovie = getActualMovieInformation(
        positionOfMovie, movieElements, yearElements)

    # Gets all the subtitle elements available for the movie.
    subtitleElements, positionOfSubtitles, soup = getSubtitleElements(
        soup, codeLang, selectedMovieElement, language)

    # Creates a folder to store the subtitles.
    folder = createFolderToStoreSubtitles(language, movieName, yearOfMovie)

    # Downloads the subtitles. Stores the value of numberOfSubtitles in case the amount of
    # subtitles downloaded is less than the number of subtitles the user wants.
    numberOfSubtitles = downloadSubtitles(
        soup, language, numberOfSubtitles, positionOfSubtitles, movieName, yearOfMovie, folder)

    # Unzips the subtitles.
    unzipSubtitles(numberOfSubtitles, folder, movieName, yearOfMovie, codeLang)


if __name__ == "__main__":
    main()
