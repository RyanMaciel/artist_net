import sys
import os
import json
from bs4 import BeautifulSoup, NavigableString
import pprint


data_path = 'web_data/'
painters_path = data_path + 'painters/'
painters_list_path = painters_path + 'lists/'
painters_names_path = painters_path + 'names/'


def parse_artist_page(html_string):

    soup = BeautifulSoup(html_string, 'html.parser')

    # parse infobox
    table = soup.find('table', 'infobox')
    if table:
        table_rows = table.find_all('tr')

        attributes = {}
        for tr in table_rows:
            key_html = tr.find('th')
            value_html = tr.find('td')

            if key_html and value_html:     
                attributes[key_html.text.replace('\xa0', ' ')] = value_html.text.replace('\xa0', ' ')
        
        return attributes

    # get all links
    # content = soup.find('div', id='mw-content-text')
    # all_links = content.find_all('a')
    # for link in all_links:
    #     if link.parent.name != 'sup':
    #         print(link.get_text())

    
    

def main(argv):
    artist_pages = os.listdir(painters_names_path)
    
    # html_string = open(painters_names_path + artist_pages[8], 'r').read()
    pp = pprint.PrettyPrinter(depth=4)

    infobox_results = {}

    for i in range(len(artist_pages)):
        name = artist_pages[i].replace('.html', '')

        html_string = open(painters_names_path + artist_pages[i], 'r').read()
        res = parse_artist_page(html_string)
        infobox_results[name] = res

        if i % 100 == 0:
            with open('data.json', 'w') as outfile:
                json.dump(infobox_results, outfile)

if __name__ == "__main__":
   main(sys.argv[1:])