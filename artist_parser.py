import sys
import os
import json
import re
import urllib.parse
from bs4 import BeautifulSoup, NavigableString
import pprint

data_path = 'web_data/'
painters_path = data_path + 'painters/'
painters_list_path = painters_path + 'lists/'
painters_names_path = painters_path + 'names/'
movements_list_path = 'movements.txt'

# given a percentage, print a progress bar
def print_progress(percentage):
    num_slices = 20

    num_done = int(percentage * num_slices)
    right_pad = num_slices - num_done

    print('[' + ('#' * num_done) + (' ' * right_pad) + '] ' + str(int(percentage * 100)) + '%', end='\r')

    if int(percentage) == 1:
        print('\n')


# Given the document body (soup object), get all of the links to
# movements by matching with the movements_list param.
def get_movements_from_all_links(doc_body, movement_list):

    # open the movements_list_path. We expect this to be a list of
    # movements that correspond to wikipedia relative links
    result_movements = []
    all_links = doc_body.find_all(href=True)
    for link in all_links:
        clean_link = urllib.parse.unquote(link['href'].replace('/wiki/', '')).replace('_', ' ').lower()
        if clean_link in movement_list:
            result_movements.append(clean_link)
    return result_movements

# Given a (Beautiful Soup) row from the infobox
# parse out the movements (a list of strings)
def get_movements_from_row(row):
    movement_list = []

    # find all linked movements
    movement_links = row.find_all('a')
    for movement in movement_links:
        if movement.parent.name != 'sup':
            # get the 'cleaned' relative link. Decode html encoding, remove /wiki/ and _
            rel_link = urllib.parse.unquote(movement['href'].replace('/wiki/', '')).replace('_', ' ')
            
            # remove items in parentheses, strip and lowercase
            rel_link = re.sub(r'\(.+\)', '', rel_link).strip().lower().replace('\xa0', ' ')

            movement_list.append(rel_link)
    
    # try to make sense of the raw text

    # All text at the row level (ie. not in <a></a> or otherwise)
    unlinked_results = row.find_all(text=True, recursive=False)
    for result in unlinked_results:
        result = result.lower().replace('\xa0', ' ')
        # don't want one of these common separation words.
        # Iteratively split result by each of them.
        sep_words = ['to', 'and', 'or', 'of', 'founder', 'also']
        sep_punc = ['/', ',', ';', '(', ')']
        sep_split_words = [result]
        
        # deal with word separators
        for sep in sep_words:
            temp_sep_split = []
            for w in sep_split_words:
                # when we do word separators, make sure they are not surrounded by
                # letters. ie. Don't split 'sculptor' on 'to'
                temp_sep_split += re.split(r'\b{sep}\b', w)
            sep_split_words = temp_sep_split

        # deal with punctuation separators
        for sepp in sep_punc:
            temp_sep_split = []
            for w in sep_split_words:
                temp_sep_split += w.split(sepp)
            sep_split_words = temp_sep_split
                    
        for w in sep_split_words:
            w = w.strip()
            if len(w) != 0:
                movement_list.append(w)

    return movement_list

# Parse the artist page from the html, looking for movements
# in movement_list
def parse_artist_page(html_string, movement_list):

    soup = BeautifulSoup(html_string, 'html.parser')
    # get main text content
    content = soup.find('div', id='mw-content-text')
    attributes = {}
    linked_movements = get_movements_from_all_links(content, movement_list)
    attributes['Movement'] = linked_movements

    # parse infobox
    table = soup.find('table', 'infobox')
    if table:
        table_rows = table.find_all('tr')

        for tr in table_rows:
            key_html = tr.find('th')
            value_html = tr.find('td')

            if key_html and value_html:

                # parse the movements into a list
                # this is difficult because sometimes movements are linked,
                # and sometimes they are just listed (with different formats lol)
                if key_html.text == 'Movement':
                    
                    # parse out movements (expect there are some from the main body of the text already)
                    current_movements = attributes['Movement']
                    current_movements += get_movements_from_row(value_html)
                    attributes['Movement'] = current_movements
                else:
                    # TODO deal with unicode issues. You might have to deal with langauge issues which will
                    # take you all the way back to the downloader which might not be fun...   
                    attributes[key_html.text.replace('\xa0', ' ')] = value_html.text.replace('\xa0', ' ')
        
    return attributes

    
    


# read from all of the artist pages and generate json data about them.
# curently, this data is:
# {
#   'Artist_Name': {
#       'infobox_key': 'infobox_value'
#   }
# }
# Where infobox is the wikipedia right hand side thing
# artist_metadata (from web_downloader.py): 
#   {
#        name: <String or None if there is no link associated with the artist>
#        description: <String: brief description of the artist from the list page>
#        artist_link: <String: relative link to artist wiki>
#        associated_links: [<String: relative link to any links in the descriptions>, ...]
#   },  
def generate_artist_json(save_path='data.json', artist_metadata=[], save_freq=300):
    infobox_results = {}

    # get the list of movements we want to recognize.
    with open(movements_list_path) as movement_list_file:
        movements = [line.rstrip('\n').lower() for line in movement_list_file]

        for i in range(len(artist_metadata)):
            name = artist_metadata[i]['name']
            try:
                with open(painters_names_path + name + '.html', 'r') as raw_file:
                    html_string = raw_file.read()
                    final_data = parse_artist_page(html_string, movements)
                    
                    # TODO: This step is going to throw out a lot of artists that
                    # we aren't able to parse well right now (ones that don't have
                    # info boxes)
                    if final_data and len(final_data['Movements']) > 0:
                        # attach the link from the metadata to the parsed data.
                        final_data['artist_link'] = artist_metadata[i]['artist_link']
                        infobox_results[name] = final_data

                        # interstatial save (this loop takes a few minutes on my laptop.)
                        if i % save_freq == 0:
                            with open(save_path, 'w') as outfile:
                                json.dump(infobox_results, outfile)
                        
                    print_progress(i/len(artist_metadata))
            except Exception as e:
                print('An error occured on opening ' + name + '\'s html file.')
                print(e)
                print('\n')

    # save the last few
    with open(save_path, 'w') as outfile:
        json.dump(infobox_results, outfile)

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
    PARSE_DATA_SAVE_PATH = 'artist_data.json'

    # handle flags.
    js_output = False
    csv = False
    no_parse = False
    if '--csv' in argv:
        csv = True
    if '--js-output' in argv:
        js_output = True
    if '--no-parse' in argv:
        no_parse = True
    
    # In order for the JS to use the data, we want to write it to a js file
    # that has a single variable, dataString which is just a json string to be
    # parsed. This is absolutely not best practice, but good enough.
    if js_output:
        with open(PARSE_DATA_SAVE_PATH, 'r') as list_json_file:
            list_json = json.load(list_json_file)
            stringified = json.dumps(list_json)

            # escape ' \n \r and \" (to \\"" https://stackoverflow.com/questions/24559625/javascript-escape-double-quotes)
            stringified = stringified.replace("'", "\\'").replace('\\r', '').replace('\\n', '').replace('\\"', '\\\\"')
            js_string = "let dataString='" + stringified + "'" # AH! Very scary js in python
            with open("data.js", "w") as js_output:
                js_output.write(js_string)

    # Get the data file from web_downloader.py.
    if not no_parse:
        with open('artist_list_file.json', 'r') as list_json_file:
            list_json = json.load(list_json_file)
            parsed_data = generate_artist_json(save_path=PARSE_DATA_SAVE_PATH, artist_metadata=list_json)

            if csv:
                data_string = open(PARSE_DATA_SAVE_PATH, 'r').read()
                data = json.loads(data_string)
                output_csv_from_json(json.loads(data_string))

            # Create a dictionary of movement names and # of occurences.
            # Useful for debugging data quality for right now.
            movements = {}
            for artist_name in parsed_data:
                item = parsed_data[artist_name]
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