import urllib2, cgi, pickle
from HTMLParser import HTMLParser

# GLOBAL VARIABLES
with open('/users/admin/Documents/episodes.pkl') as openEpisode: # pickle file contains object that tracks what last episode downloaded for each show was
    episodes = pickle.load(openEpisode)
# websites won't accept a connection from 'python' so I got the user_agent headers for my browser from a website and use that in the request
user_agent = 'USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
headers = {'User-Agent': user_agent}
episodeLinks = { # got these URLs from Network tab of Chrome's inspector under 'XHR'
    'boruto': 'http://horriblesubs.info/lib/getshows.php?type=show&showid=869',
    'onepiece': 'http://horriblesubs.info/lib/getshows.php?type=show&showid=347'
}
searchStrings = { # create search strings for each show using the episode number read from episodes.pkl
    'boruto': 'Boruto - Naruto Next Generations - {} [720p]'.format(episodes['boruto']),
    'onepiece': 'One Piece - {} [720p]'.format(episodes['onepiece'])
}

class MyHTMLParser(HTMLParser): # I heard 3rd party library BeautifulSoup makes HTML parsing super easy but I wanted to try with built in library. Also used Python 2 code because I wanted it to work on my Mac server out of the box
    def __init__(self):
        HTMLParser.__init__(self)
        self.show = ''
        self.tdCount = 0
        
    def handle_starttag(self, tag, attrs):
        if self.show and tag == 'td':
            self.tdCount += 1
        if self.tdCount == 2: # the torrent link is always in the second <td> tag after the searchString is found
            try:
                if attrs[0][1] == 'Torrent Link': # the tag with 'Torrent Link' will have the URL needed to download the torrent file
                    torrentLink = attrs[1][1]
                    request = urllib2.Request(url = torrentLink, data=None, headers = headers) # makes request to download torrent file
                    torrentData = urllib2.urlopen(request)
                    _, params = cgi.parse_header(torrentData.headers.get('Content-Disposition', ''))
                    filename = urllib2.unquote(params['filename'])
                    dataToWrite = torrentData.read()
                    with open('/users/admin/Downloads/{}'.format(filename), 'wb') as saveTorrent: # save torrent file in downloads folder
                        saveTorrent.write(dataToWrite)
                        saveTorrent.close()
                    episodes[self.show] += 1 # increment episode count for show corresponding to current searchString. This script won't work with the occasional special shows that have different name/number scheme
                    with open('/users/admin/Documents/episodes.pkl', 'wb') as saveEpisode: # save pickle with current episode counts
                        pickle.dump(episodes, saveEpisode)
                        saveEpisode.close()          
                    self.show = '' # reset perser properties so next searchString can be found
                    self.tdCount = 0
            except:
                pass

    def handle_data(self, data):
        for show, searchString in searchStrings.iteritems():
            if data == searchString:
                self.show = show # searchString found so set self.show to name of show so I know which show's episode number to increment

def makeParserData(): # takes the episodeLinks URLs and makes one concatenated HTML string to feed to the parser
    parserData = ''
    for link in episodeLinks.itervalues():
        request = urllib2.Request(url = link, data=None, headers = headers)
        response = urllib2.urlopen(request)
        parserData += response.read()
    return parserData

showParser = MyHTMLParser()
showParser.feed(makeParserData())

