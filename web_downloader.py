import urllib.request, urllib.error, urllib.parse
from urllib.error import HTTPError
import string
import time
import os
import sys
import getopt
from bs4 import BeautifulSoup, NavigableString

data_path = 'web_data/'
painters_path = data_path + 'painters/'
painters_list_path = painters_path + 'lists/'
painters_names_path = painters_path + 'names/'

def build_directory_tree():
    for path in [data_path, painters_path, painters_list_path, painters_names_path]:
        if not os.path.isdir(path):
            os.mkdir(path)


# given a percentage, print a progress bar
def print_progress(percentage):
    num_slices = 20

    num_done = int(percentage * num_slices)
    right_pad = num_slices - num_done

    print('[' + ('#' * num_done) + (' ' * right_pad) + '] ' + str(int(percentage * 100)) + '%', end='\r')

    if int(percentage) == 1:
        print('\n')


# takes an array of urls and an optional array of names
# and downloads the pages with corresponding names (just the url name if not provided)
# the check exists flag will not download files that already exist if set to true.
def get_html_files(urls, names=None, path='', check_exists=False):
    
    # keep track of the number we skipped from checking existence.
    num_skipped = 0
    for url_index in range(len(urls)):

        # generate save path.
        url = urls[url_index]
        name = url
        if names:
            name = names[url_index]
        full_path = path + name + '.html'

        # if the check exists flag is on, and it doesn't exist or if the check exists
        # flag is off.
        if (check_exists and not os.path.exists(full_path)) or not check_exists:

            try:
                # fetch from url
                response = urllib.request.urlopen(url)
                web_content = response.read()
                decoded_html = web_content.decode('utf-8')

                # save
                html_file= open(full_path,'w')
                html_file.write(decoded_html)
                html_file.close()
            except HTTPError as err:
                print('Error code: ' + str(err.code))
                print('When processing url:' + url)

            # log progress.
            print_progress((url_index+1)/len(urls))

            # sleep for 7 seconds, not trying to get kicked off wikipedia.
            time.sleep(7)
        else:
            num_skipped += 1
    print('Skipped ' + str(num_skipped) + ' entries while downloading.')

# request painter list files
def populate_painter_list_files(path):
    print('downloading painter list files')
    urls = []
    names = []
    for s in string.ascii_uppercase:
        urls.append('https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22' + s +'%22')
        names.append('painters_' + s)
    get_html_files(urls, names=names, path=path)



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

def populate_painter_names(total_artists, path='', check_exists=False):
    urls = []
    names = []
    for artist_entry in total_artists:
        link = artist_entry['artist_link']
        if link:
            urls.append('https://www.wikipedia.com' + link)
            names.append(artist_entry['name'])
    get_html_files(urls, names, path, check_exists)

def create_list_csv(total_artists):
    csv_string = 'name, desciption, artist_link, \n'
    for artist in total_artists:
        # remove commas and deal with None values
        name = artist['name'].replace(',', '') if artist['name'] else ''
        description = artist['description'].replace(',', '') if artist['description'] else ''
        artist_link = artist['artist_link'].replace(',', '') if artist['artist_link'] else ''

        csv_string += name + ',' + description + ',' + artist_link + ',\n'

    csv_data = open('painter_data.csv','w')
    csv_data.write(csv_string)
    csv_data.close()

def main(argv):

    download = False
    if '--download' in argv or '--d'in argv:
        download = True

    build_directory_tree()

    if download:
        populate_painter_list_files(painters_list_path)

    #get a {name, description, artist_link, associated_links} object for every artist
    # in the painter's name entry.
    total_artists = []
    for s in string.ascii_uppercase:
        html_string = open(painters_list_path + 'painters_' + s + '.html', 'r').read()
        total_artists += parse_html(html_string)

    populate_painter_names(total_artists, path=painters_names_path, check_exists=True)

if __name__ == "__main__":
   main(sys.argv[1:])