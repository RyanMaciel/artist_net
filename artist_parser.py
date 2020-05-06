import sys
import os
from bs4 import BeautifulSoup, NavigableString

data_path = 'web_data/'
painters_path = data_path + 'painters/'
painters_list_path = painters_path + 'lists/'
painters_names_path = painters_path + 'names/'


def parse_artist_page(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    table = soup.find("table", "infobox")
    table_rows = table.find_all('tr')
    for tr in table_rows:
        for header in tr.find_all('th'):
            print(header.text)
        td = tr.find_all('td')
        row = [i.text for i in td]
        print(row)

def main(argv):
    artist_pages = os.listdir(painters_names_path)
    
    html_string = open(painters_names_path + artist_pages[8], 'r').read()
    parse_artist_page(html_string)
    

if __name__ == "__main__":
   main(sys.argv[1:])