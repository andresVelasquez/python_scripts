import os, re

files = os.listdir('/Volumes/Data/Torrents/')
showNamesAndPaths = { # more shows can be added as long as it's 720p and the download site maintains the same naming conventions. Key is show name and value is path where it will be moved to after renaming
    'Boruto': '/Volumes/Data/Videos/Anime/Boruto/', # make sure these paths begin and end with the '/' character
    'One Piece': '/Volumes/Data/Videos/Anime/One Piece/TV/'
}

for fileName in files:
    for show, path in showNamesAndPaths.iteritems():
        if show in fileName and '[720p]' in fileName:
            fileExtension = os.path.splitext('/Volumes/Data/Torrents/{}'.format(fileName))[1] # gets the extension of the file
            if fileExtension != '.part': # .part means torrent is not finished downloading so skip it
                dropNumber = fileName.partition('[720p]')[0] # leave out 720 so episode number is the only number left
                episodeNumber = re.findall('\d+', dropNumber)[0].zfill(3) # strip episode number out pad with zeros if necessary to 3 digit length
                newFileName = '{} {}{}'.format(show, episodeNumber, fileExtension)
                os.rename('/Volumes/Data/Torrents/{}'.format(fileName), '{}{}'.format(showNamesAndPaths[show], newFileName))
                break # no need to check the rest of the show names, move on to the next file
