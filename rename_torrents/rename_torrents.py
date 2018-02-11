import os, re

files = os.listdir('/users/andres/Downloads/')
showNames = ( # more shows can be added as long as it's 720p and the download site maintains the same naming conventions
    'Boruto',
    'One Piece'
)

for fileName in files:
    for show in showNames:
        if show in fileName and '[720p]' in fileName:
            fileExtension = os.path.splitext('/users/andres/Downloads/{}'.format(fileName))[1] # gets the extension of the file
            if fileExtension != '.part':
                dropNumber = fileName.partition('[720p]')[0] # leave out 720 so episode number is the only number left
                episodeNumber = re.findall('\d+', dropNumber)[0].zfill(3) # strip episode number out pad with zeros if necessary to 3 digit length
                newFileName = '{} {}{}'.format(show, episodeNumber, fileExtension)
                os.rename('/users/andres/Downloads/{}'.format(fileName), '/users/andres/Downloads/ztest/{}'.format(newFileName))
                break # no need to check the rest of the show names, move on to the next file
