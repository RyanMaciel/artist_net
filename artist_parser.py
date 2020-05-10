import sys
import os
import json
from bs4 import BeautifulSoup, NavigableString
import pprint


data_path = 'web_data/'
painters_path = data_path + 'painters/'
painters_list_path = painters_path + 'lists/'
painters_names_path = painters_path + 'names/'

# given a percentage, print a progress bar
def print_progress(percentage):
    num_slices = 20

    num_done = int(percentage * num_slices)
    right_pad = num_slices - num_done

    print('[' + ('#' * num_done) + (' ' * right_pad) + '] ' + str(int(percentage * 100)) + '%', end='\r')

    if int(percentage) == 1:
        print('\n')

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

                # parse the movements into a list
                # this is difficult because sometimes movements are linked,
                # and sometimes they are just listed (with different formats lol)
                if key_html.text == 'Movement':

                    movement_list = []

                    # find all linked movements
                    # TODO: sometimes links to the same movement have different labels.
                    # This could be a relatively easy fix.
                    movement_links = value_html.find_all('a')
                    for movement in movement_links:
                        if movement.parent.name != 'sup':
                            movement_list.append(movement.text.replace('\xa0', ' '))
                    
                    # try to make sense of the raw text
                    unlinked_results = value_html.find_all(text=True, recursive=False)
                    for result in unlinked_results:

                        # don't want one of these common separation words.
                        if result.strip() not in ['/', 'to', 'and', ',']:
                            sub_movements = result.strip().replace('\xa0', ' ').split(',')
                            for sub in sub_movements:
                                movement_list.append(sub)
                    attributes[key_html.text.replace('\xa0', ' ')] = movement_list
                else:
                    # TODO deal with unicode issues. You might have to deal with langauge issues which will
                    # take you all the way back to the downloader which might not be fun...   
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

    # for i in range(len(artist_pages)):
    #     name = artist_pages[i].replace('.html', '')
    #     html_string = open(painters_names_path + artist_pages[i], 'r').read()
    #     infobox_results[name] = parse_artist_page(html_string)

    #     if i % 100 == 0:
    #         with open('data.json', 'w') as outfile:
    #             json.dump(infobox_results, outfile)
        
    #     print_progress(i/len(artist_pages))

    data_string = open('data.json', 'r').read()
    data = json.loads(data_string)
    
    movements = {}
    for artist_name in data:
        item = data[artist_name]
        if item != None and 'Movement' in item:
            movement_list = item['Movement']
            for movement in movement_list:
                if movement not in movements:
                    movements[movement] = 1
                else: 
                    movements[movement] += 1
    
    from collections import OrderedDict
    sort_movements = OrderedDict(sorted(movements.items(), key=lambda a: a[1], reverse=True))
    pp.pprint(sort_movements)


if __name__ == "__main__":
   main(sys.argv[1:])