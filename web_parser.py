import urllib.request, urllib.error, urllib.parse
import string
import time
import os
from bs4 import BeautifulSoup, NavigableString

data_path = 'web_data/'

def get_html_files():
    for s in string.ascii_uppercase:
        url = 'https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22' + s +'%22'
        response = urllib.request.urlopen(url)
        web_content = response.read()
        decoded_html = web_content.decode('utf-8')
        html_file= open(data_path + 'painters_' + s + '.html','w')
        html_file.write(decoded_html)
        html_file.close()
        time.sleep(10)
        print('Retrieved painters beginning with: ' + s)

if len(os.listdir(path=data_path)) == 0:
    print('html data not found, requesting now')
    get_html_files()
else:
    print('html data already loaded')


# Parse the html file for a single artist letter name.
# Returns an array of artists of the form: [
#   {
#        name: <String or None if there is no link associated with the artist>
#        description: <String: brief description of the artist from the list page>
#        artist_link: <String: relative link to artist wiki>
#        associated_links: [<String: relative link to any links in the descriptions>, ...]
#   }, 
#   ...
# ]
#
def parse_html(html_string):
    file_artists = []

    soup = BeautifulSoup(html_string, 'html.parser')
    container_result = soup.find_all('div', attrs={'class': 'mw-parser-output'})
    list_result = soup.find_all('ul')
    if len(list_result) > 0:
        # call str() on navigable strings to remove reference to soup object.
        for artist_entry in list_result[1].children:
            if not isinstance(artist_entry, NavigableString):
                links = artist_entry.find_all('a')
                links = list(map(lambda link: str(link.attrs['href']), links))

                # there might not be any links associated with the artist.
                if len(links) > 0:
                    artist_link = links[0]
                    if len(links) > 1:
                        associated_links = links[1:]
                    else:
                        associated_links = []
                else:
                    artist_link = None
                
                # if there is no link, the artists will have no name
                # since it is not delineated in a html tag...
                if artist_entry.a:
                    name = artist_entry.a.string
                description = artist_entry.text

                file_artists.append({
                    'name': str(name),
                    'description': str(description),
                    'artist_link': artist_link,
                    'associated_links': associated_links
                })
    return file_artists

total_artists = []
for s in string.ascii_uppercase:
    html_string = open(data_path + 'painters_' + s + '.html', 'r').read()
    total_artists += parse_html(html_string)

csv_string = 'name, desciption, artist_link, \n'
for artist in total_artists:
    # remove commas and deal with None values
    name = artist['name'].replace(',', '') if artist['name'] else ''
    description = artist['description'].replace(',', '') if artist['description'] else ''
    artist_link = artist['artist_link'].replace(',', '') if artist['artist_link'] else ''

    csv_string += name + ',' + description + ',' + artist_link + ',\n'

csv_data = open(data_path + 'painter_data.csv','w')
csv_data.write(csv_string)
csv_data.close()
 
from pprint import pprint




