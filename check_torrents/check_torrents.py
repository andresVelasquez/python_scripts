#!/usr/bin/python
import urllib2, cgi, pickle, os, subprocess, logging
from HTMLParser import HTMLParser

if not os.path.isdir('/Volumes/Data/Torrents/'): # Quit program if volume 'Data' on external drive is not mounted
    print('/Volumes/Data/Torrents/ is not available.')
    quit()

# GLOBAL VARIABLES
# websites won't accept a connection from 'python' so I got the user_agent headers for my browser from a website and use that in the request
user_agent = 'USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
headers = {'User-Agent': user_agent}
shows = { # got these URLs from Network tab of Chrome's inspector under 'XHR'
    'boruto': 'https://www.horriblesubs.info/api.php?method=getshows&type=show&showid=869',
    'onepiece': 'https://www.horriblesubs.info/api.php?method=getshows&type=show&showid=347'
}
torrent_found = False

class MyHTMLParser(HTMLParser): # I heard 3rd party library BeautifulSoup makes HTML parsing super easy but I wanted to try with built in library. Also used Python 2 code because I wanted it to work on my Mac server out of the box
    def __init__(self, episode):
        HTMLParser.__init__(self)
        self.current_episode = episode
        self.high_episode = episode
        self.found_ep = False

    def handle_starttag(self, tag, attrs):
        if not self.found_ep and tag == 'div' and attrs[0][1] == 'rls-link link-720p' and int(attrs[1][1].split('-')[0]) > self.current_episode:
            self.found_ep = True
            if int(attrs[1][1].split('-')[0]) > self.high_episode:
                self.high_episode = int(attrs[1][1].split('-')[0])
        if self.found_ep and tag == 'a' and attrs[0][1] == 'Torrent Link':
            torrentLink = attrs[1][1]
            request = urllib2.Request(url = torrentLink, data=None, headers = headers) # makes request to download torrent file
            torrentData = urllib2.urlopen(request)
            _, params = cgi.parse_header(torrentData.headers.get('Content-Disposition', '')) # get filename from the response headers
            filename = urllib2.unquote(params['filename']) # unquote will convert the URL filename to regular filename. For example, changing %20 to a space
            dataToWrite = torrentData.read()
            with open('/Users/Andres/Downloads/{}'.format(filename), 'wb') as saveTorrent: # save torrent file in Downloads folder
                saveTorrent.write(dataToWrite)
                saveTorrent.close()
            self.found_ep = False
            global torrent_found
            torrent_found = True

def makeParserData(url): # gets the shows URLs and makes one concatenated HTML string from the page to feed to the parser
    request = urllib2.Request(url = url, data=None, headers = headers)
    response = urllib2.urlopen(request)
    parserData = response.read()
    return parserData

with open('/Volumes/Data/Torrents/check_torrents/episodes.pkl') as openEpisode: # pickle file contains object that tracks what last episode downloaded for each show was
    showList = pickle.load(openEpisode)

for show, episode in showList.iteritems():
    showParser = MyHTMLParser(episode)
    try:
        showParser.feed(makeParserData(shows[show]))
        showList[show] = showParser.high_episode

    except Exception as e:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S -', filename='/Volumes/Data/Torrents/check_torrents/error.log', level=logging.ERROR)
        logging.error(str(e))
        pass

with open('/Volumes/Data/Torrents/check_torrents/episodes.pkl', 'wb') as saveEpisode: # save pickle with current episode counts
    pickle.dump(showList, saveEpisode)
    saveEpisode.close()

# Open Transmission app if it's not running and torrent files were downloaded
if torrent_found:
    process = subprocess.Popen('pgrep Transmission', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.communicate()[0] == '':
        subprocess.call(["/usr/bin/open", "-j", "-g", "-a", "/Applications/Transmission.app"])
