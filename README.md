# 🌌 artist_net 🖼
An effort to catalogue artists in an interesting way. Currently this is basically a parser for wikipedia's [list of painters by name](https://en.wikipedia.org/wiki/List_of_painters_by_name). The hope is to be able to find links between artists and art movements and present them graphically.

# Usage
## Dependencies
Written in Python 3.7 HTML parsing is done using BeautifulSoup4, which you can install like this:
`conda install -c anaconda beautifulsoup4`

## Usage
`python web_parser.py --download`

This will download 26 html files from wikipedia (one for each letter) and wait 7 seconds in between each one because I'm really not trying to get blocked from Wikipedia. Then it will output a csv file that takes some relevant data from the html. There should be about 3.4k rows right now.
