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


# read from all of the artist pages and generate json data about them.
# curently, this data is:
# {
#   'Artist_Name': {
#       'infobox_key': 'infobox_value'
#   }
# }
# Where infobox is the wikipedia right hand side thing
def generate_artist_json(save_path='data.json', save_freq=100):
    infobox_results = {}

    artist_pages = os.listdir(painters_names_path)
    for i in range(len(artist_pages)):
        name = artist_pages[i].replace('.html', '')
        html_string = open(painters_names_path + artist_pages[i], 'r').read()
        infobox_results[name] = parse_artist_page(html_string)

        if i % save_freq == 0:
            with open(save_path, 'w') as outfile:
                json.dump(infobox_results, outfile)
        
        print_progress(i/len(artist_pages))
    
    return infobox_results
    

def output_csv_from_json(data):
    csv_string = 'artist_name, movement1, movement2, movement3, movement4, movement5,\n'

    for artist_name in data:
        entry = data[artist_name]
        if entry != None and 'Movement' in entry:
            csv_string += artist_name+','
            movement_list = entry['Movement']
            num = 0
            for movement in movement_list:
                csv_string += movement + ','
                num+=1
            csv_string += ','*(5-num)
        csv_string += '\n'
    
    csv_data = open('data.csv','w')
    csv_data.write(csv_string)

def main(argv):
    
    pp = pprint.PrettyPrinter(depth=4)


    #generate_artist_json(save_path='data.json')


    data_string = open('data.json', 'r').read()
    data = json.loads(data_string)
    #output_csv_from_json(json.loads(data_string))


    # Create a dictionary of movement names and # of occurences.
    # Useful for debugging data quality for right now.
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